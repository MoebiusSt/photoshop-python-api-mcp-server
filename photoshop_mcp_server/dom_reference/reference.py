"""In-memory query layer over the bundled api.json files.

Upstream: https://www.indesignjs.de/indesignapi/ (Gregor Fellenz). Files in ``data/``:

- ``photoshop.json``  - Photoshop object model (``photoshop/api.json``)
- ``javascript.json`` - ExtendScript Core JavaScript (``javascript/api.json``)
- ``scriptui.json``   - ScriptUI (``scriptui/api.json``)

Refresh them with ``python -m photoshop_mcp_server.dom_reference.update``.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

API_BASE_URL = "https://www.indesignjs.de/indesignapi"
DATA_DIR = Path(__file__).parent / "data"

# source key -> upstream target slug (also the file name in data/)
SOURCES = {
    "photoshop": "photoshop",
    "javascript": "javascript",
    "scriptui": "scriptui",
}

SOURCE_NOTES = {
    "photoshop": (
        "Newest object model Adobe exported is Photoshop CC 2015.5. The ExtendScript DOM has barely "
        "changed since; features without a DOM equivalent are scripted through the Action Manager "
        "(executeAction, ActionDescriptor, charIDToTypeID/stringIDToTypeID)."
    ),
    "javascript": "ExtendScript Core JavaScript ($, File, Folder, UnitValue, XML, ...). Not available in UXP.",
    "scriptui": "ScriptUI dialogs (legacy). Not available in UXP.",
}

KIND_MAP = {"Object": "object", "Collection": "collection", "Enumeration": "enum"}
SUPPORTED_FORMAT_VERSION = 2

_WORD_RE = re.compile(r"[A-Za-z0-9_$]+")


def _method_kind(source: str, class_name: str, method: dict) -> str:
    name = method["name"]
    if method.get("static"):
        return "static"
    if name == class_name and source != "photoshop":
        return "constructor"
    if source == "scriptui" and re.match(r"on[A-Z]", name):
        return "event"
    return "instance"


def _signature(method: dict) -> str:
    params = [
        f"{p['name']}{'?' if p.get('optional') else ''}: {p.get('type') or 'any'}"
        for p in method.get("parameters", [])
    ]
    return f"{method['name']}({', '.join(params)}) -> {method.get('returns') or 'void'}"


class DomReference:
    """Lookup over the Photoshop, Core JavaScript and ScriptUI object models."""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.meta: dict[str, dict[str, Any]] = {}
        self.classes: dict[str, dict[str, dict]] = {}
        for source, target in SOURCES.items():
            path = data_dir / f"{target}.json"
            raw = json.loads(path.read_text(encoding="utf-8"))
            if raw.get("formatVersion", 1) < SUPPORTED_FORMAT_VERSION:
                raise ValueError(f"{path.name}: api.json formatVersion {SUPPORTED_FORMAT_VERSION} required")
            self.meta[source] = {
                "version": raw.get("version", ""),
                "generated": raw.get("generated", ""),
                "runtimes": raw.get("runtimes", ["extendscript"]),
                "counts": raw.get("counts", {}),
                "url": f"{API_BASE_URL}/{target}/api.json",
            }
            self.classes[source] = {obj["name"]: {**obj, "target": target} for obj in raw.get("objects", [])}

    # ------------------------------------------------------------------ helpers

    def _find(self, name: str, source: str | None) -> list[tuple[str, dict]]:
        sources = [source] if source else list(SOURCES)
        hits = []
        for src in sources:
            obj = self.classes.get(src, {}).get(name)
            if obj is not None:
                hits.append((src, obj))
        if not hits:
            lowered = name.lower()
            for src in sources:
                for cls_name, obj in self.classes.get(src, {}).items():
                    if cls_name.lower() == lowered:
                        hits.append((src, obj))
        return hits

    def _chain(self, source: str, obj: dict) -> list[dict]:
        chain, seen = [obj], {obj["name"]}
        parent = obj.get("extends")
        while parent and parent not in seen:
            parent_obj = self.classes[source].get(parent)
            if parent_obj is None:
                break
            chain.append(parent_obj)
            seen.add(parent_obj["name"])
            parent = parent_obj.get("extends")
        return chain

    def _doc_url(self, obj: dict) -> str:
        page = obj.get("page") or f"{obj['name']}.html"
        return f"{API_BASE_URL}/{obj['target']}/{page.removesuffix('.html')}.md"

    @staticmethod
    def _property_entry(prop: dict, defined_in: str, is_enum: bool, full: bool) -> dict:
        entry = {
            "name": prop["name"],
            "type": prop.get("type"),
            "access": prop.get("access"),
        }
        if is_enum or prop.get("static"):
            entry["static"] = True
        if "value" in prop:
            entry["value"] = prop["value"]
        if full:
            entry["description"] = prop.get("description", "")
            if prop.get("range"):
                entry["range"] = prop["range"]
            entry["defined_in"] = defined_in
        return entry

    def _method_entry(self, source: str, method: dict, defined_in: str, full: bool) -> dict:
        entry = {
            "name": method["name"],
            "signature": _signature(method),
            "kind": _method_kind(source, defined_in, method),
        }
        if full:
            entry["description"] = method.get("description", "")
            entry["returns"] = method.get("returns")
            entry["parameters"] = method.get("parameters", [])
            entry["defined_in"] = defined_in
        return entry

    # ------------------------------------------------------------------ queries

    def info(self) -> dict:
        return {
            "upstream": API_BASE_URL,
            "sources": {
                src: {**meta, "note": SOURCE_NOTES[src], "classes": len(self.classes[src])}
                for src, meta in self.meta.items()
            },
            "name_collisions": sorted(set(self.classes["photoshop"]) & set(self.classes["scriptui"])),
            "usage": (
                "photoshop_dom_search to find classes and members, photoshop_dom_lookup_class for a class with "
                "all members, photoshop_dom_get_member for descriptions and parameters, "
                "photoshop_dom_get_enum_values for enumeration constants. Pass source when a name exists in "
                "more than one source. Each class carries doc_url, the upstream Markdown page."
            ),
        }

    def lookup_class(self, name: str, source: str | None = None, include_inherited: bool = True) -> list[dict]:
        result = []
        for src, obj in self._find(name, source):
            kind = KIND_MAP.get(obj.get("kind", ""), "object")
            is_enum = kind == "enum"
            chain = self._chain(src, obj) if include_inherited else [obj]
            properties, methods, seen_p, seen_m = [], [], set(), set()
            for owner in chain:
                for prop in owner.get("properties", []):
                    if prop["name"] not in seen_p:
                        seen_p.add(prop["name"])
                        properties.append(self._property_entry(prop, owner["name"], is_enum, full=False))
                for method in owner.get("methods", []):
                    if method["name"] not in seen_m:
                        seen_m.add(method["name"])
                        methods.append(self._method_entry(src, method, owner["name"], full=False))
            entry = {
                "name": obj["name"],
                "source": src,
                "kind": kind,
                "description": obj.get("description", ""),
                "doc_url": self._doc_url(obj),
            }
            if obj.get("extends"):
                entry["superclass_chain"] = [c["name"] for c in chain[1:]] or [obj["extends"]]
            subclasses = sorted(n for n, o in self.classes[src].items() if o.get("extends") == obj["name"])
            if subclasses:
                entry["direct_subclasses"] = subclasses
            if obj.get("elementType"):
                entry["collection_of"] = obj["elementType"]
            if is_enum:
                entry["values"] = properties
            else:
                entry["properties"] = properties
                entry["methods"] = methods
            result.append(entry)
        return result

    def get_member(self, class_name: str, member_name: str, source: str | None = None) -> list[dict]:
        result = []
        for src, obj in self._find(class_name, source):
            is_enum = obj.get("kind") == "Enumeration"
            for owner in self._chain(src, obj):
                for prop in owner.get("properties", []):
                    if prop["name"] == member_name:
                        result.append(
                            {"member_type": "property", "class": obj["name"], "source": src,
                             **self._property_entry(prop, owner["name"], is_enum, full=True)}
                        )
                for method in owner.get("methods", []):
                    if method["name"] == member_name:
                        result.append(
                            {"member_type": "method", "class": obj["name"], "source": src,
                             **self._method_entry(src, method, owner["name"], full=True)}
                        )
                if result:
                    break
        return result

    def get_enum_values(self, enum_name: str) -> dict | None:
        for src, obj in self._find(enum_name, None):
            if obj.get("kind") == "Enumeration":
                return {
                    "name": obj["name"],
                    "source": src,
                    "description": obj.get("description", ""),
                    "values": [
                        {"name": p["name"], "value": p.get("value"), "description": p.get("description", "")}
                        for p in obj.get("properties", [])
                    ],
                }
        return None

    def search(self, query: str, source: str | None = None, max_results: int = 20) -> list[dict]:
        terms = [t.lower() for t in _WORD_RE.findall(query)] or [query.strip().lower()]
        scored = []
        for src in [source] if source else list(SOURCES):
            for cls_name, obj in self.classes.get(src, {}).items():
                candidates = [("class" if obj.get("kind") != "Enumeration" else "enum", cls_name, "",
                               obj.get("description", ""))]
                kind_label = "value" if obj.get("kind") == "Enumeration" else "property"
                candidates += [(kind_label, p["name"], cls_name, p.get("description", ""))
                               for p in obj.get("properties", [])]
                candidates += [("method", m["name"], cls_name, m.get("description", ""))
                               for m in obj.get("methods", [])]
                for entity_type, name, parent, desc in candidates:
                    lname, ldesc = name.lower(), desc.lower()
                    score = 0
                    for term in terms:
                        if lname == term:
                            score += 10
                        elif term in lname:
                            score += 5
                        elif term in ldesc:
                            score += 1
                        else:
                            score = 0
                            break
                    if score:
                        scored.append((score, src, entity_type, name, parent, desc))
        scored.sort(key=lambda x: (-x[0], x[1], x[4], x[3]))
        return [
            {"entity_type": t, "name": n, "class": p or None, "source": s, "description": d[:200]}
            for _, s, t, n, p, d in scored[:max_results]
        ]


@lru_cache(maxsize=1)
def get_reference() -> DomReference:
    """Load the bundled reference once per process."""
    return DomReference()
