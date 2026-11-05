"""Photoshop ExtendScript DOM reference tools (read-only, no Photoshop needed)."""

from __future__ import annotations

from typing import Any

from photoshop_mcp_server.dom_reference import SOURCES, get_reference
from photoshop_mcp_server.registry import register_tool


def _check_source(source: str | None) -> dict[str, Any] | None:
    if source and source not in SOURCES:
        return {"success": False, "error": f"Unknown source '{source}'. Use one of: {', '.join(SOURCES)}."}
    return None


def register(mcp):
    """Register DOM reference tools.

    Args:
        mcp: The MCP server instance.

    """
    registered = []

    def dom_info() -> dict[str, Any]:
        """Describe the bundled ExtendScript API reference for writing photoshop_execute_jsx code.

        Covers three sources: "photoshop" (Photoshop DOM, CC 2015.5 - the newest object model
        Adobe exported), "javascript" (ExtendScript Core: $, File, Folder, UnitValue, XML) and
        "scriptui" (dialogs). Call this once before the other photoshop_dom_* tools.

        Returns:
            dict: Versions, notes and usage hints per source.

        """
        return {"success": True, **get_reference().info()}

    registered.append(register_tool(mcp, dom_info, "dom_info", debug=False))

    def dom_lookup_class(name: str, source: str | None = None, include_inherited: bool = True) -> dict[str, Any]:
        """Look up a Photoshop/ExtendScript class with all properties and method signatures.

        Args:
            name: Class name, e.g. "ArtLayer", "Document", "SolidColor", "File", "Window".
            source: Optional "photoshop", "javascript" or "scriptui" (needed for names that
                exist in several sources, e.g. "Point").
            include_inherited: Include members of superclasses (e.g. ArtLayer -> Layer).

        Returns:
            dict: Matching classes with kind, description, properties (name/type/access),
            methods (signature/kind) or enum values, collection element type and doc_url.

        """
        error = _check_source(source)
        if error:
            return error
        matches = get_reference().lookup_class(name, source=source, include_inherited=include_inherited)
        if not matches:
            return {"success": False, "error": f"Class '{name}' not found. Try photoshop_dom_search."}
        return {"success": True, "matches": matches}

    registered.append(register_tool(mcp, dom_lookup_class, "dom_lookup_class", debug=False))

    def dom_get_member(class_name: str, member_name: str, source: str | None = None) -> dict[str, Any]:
        """Get the full description of one property or method, including parameters.

        Args:
            class_name: Class name, e.g. "Document".
            member_name: Property or method name, e.g. "resizeImage" or "resolution".
            source: Optional "photoshop", "javascript" or "scriptui".

        Returns:
            dict: Member entries with type/signature, description, parameters and range.

        """
        error = _check_source(source)
        if error:
            return error
        matches = get_reference().get_member(class_name, member_name, source=source)
        if not matches:
            return {"success": False, "error": f"Member '{member_name}' not found on '{class_name}'."}
        return {"success": True, "matches": matches}

    registered.append(register_tool(mcp, dom_get_member, "dom_get_member", debug=False))

    def dom_get_enum_values(enum_name: str) -> dict[str, Any]:
        """Get the constants of a Photoshop enumeration, e.g. "BlendMode", "ResampleMethod".

        Args:
            enum_name: Enumeration name.

        Returns:
            dict: Enumeration description and its values (name, numeric value, description).

        """
        result = get_reference().get_enum_values(enum_name)
        if result is None:
            return {"success": False, "error": f"Enumeration '{enum_name}' not found."}
        return {"success": True, **result}

    registered.append(register_tool(mcp, dom_get_enum_values, "dom_get_enum_values", debug=False))

    def dom_search(query: str, source: str | None = None, max_results: int = 20) -> dict[str, Any]:
        """Search class, property, method and enum value names and descriptions.

        All terms must match (name or description); name matches rank first.

        Args:
            query: Search terms, e.g. "resize image", "blend mode", "save jpeg".
            source: Optional "photoshop", "javascript" or "scriptui".
            max_results: Maximum number of hits (default 20).

        Returns:
            dict: Hits with entity_type, name, class, source and a short description.

        """
        error = _check_source(source)
        if error:
            return error
        hits = get_reference().search(query, source=source, max_results=max_results)
        return {"success": True, "count": len(hits), "results": hits}

    registered.append(register_tool(mcp, dom_search, "dom_search", debug=False))
    return registered
