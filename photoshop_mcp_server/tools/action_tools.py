"""Photoshop Actions panel MCP tools."""

from __future__ import annotations

import json
from pathlib import Path

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.registry import register_tool

_LIST_ACTIONS_JSX = """
(function () {
    var result = [];
    var setIndex = 1;
    while (true) {
        var ref = new ActionReference();
        ref.putIndex(charIDToTypeID("ASet"), setIndex);
        var desc;
        try {
            desc = executeActionGet(ref);
        } catch (e) {
            break;
        }
        var setName = desc.getString(charIDToTypeID("Nm  "));
        var count = desc.hasKey(charIDToTypeID("NmbC"))
            ? desc.getInteger(charIDToTypeID("NmbC"))
            : 0;
        var actions = [];
        for (var j = 1; j <= count; j++) {
            var aref = new ActionReference();
            aref.putIndex(charIDToTypeID("Actn"), j);
            aref.putIndex(charIDToTypeID("ASet"), setIndex);
            try {
                var adesc = executeActionGet(aref);
                actions.push(adesc.getString(charIDToTypeID("Nm  ")));
            } catch (e2) {}
        }
        result.push({ name: setName, count: count, actions: actions });
        setIndex++;
    }
    return JSON.stringify(result);
})()
"""


def _jsx_string(value: str) -> str:
    """Escape a Python string for use inside a JSX double-quoted string."""
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )


def _parse_json_result(raw: str):
    """Parse a JSON string returned from ExtendScript, including error wrappers."""
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    if text.endswith(";"):
        text = text[:-1].strip()
    for candidate in (text, text.strip('"')):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, str):
            try:
                return json.loads(parsed)
            except json.JSONDecodeError:
                return parsed
        return parsed
    return text


def register(mcp):
    """Register Photoshop action tools.

    Args:
        mcp: The MCP server instance.

    Returns:
        list: List of registered tool names.

    """
    registered_tools = []

    def list_actions() -> dict:
        """List all loaded Photoshop action sets and the actions in each set.

        Use this before play_action to learn the exact action name and set name.
        User-defined actions are typically in a set such as "User Actions".

        Returns:
            dict: success flag plus a list of {name, count, actions} objects.

        """
        ps_app = PhotoshopApp()
        try:
            raw = ps_app.execute_javascript(_LIST_ACTIONS_JSX)
            parsed = _parse_json_result(raw)
            if isinstance(parsed, dict) and parsed.get("success") is False:
                return {"success": False, "error": parsed.get("error", raw)}
            if not isinstance(parsed, list):
                return {
                    "success": False,
                    "error": f"Unexpected list_actions result: {raw}",
                }
            return {"success": True, "action_sets": parsed}
        except Exception as e:
            return {"success": False, "error": str(e)}

    registered_tools.append(register_tool(mcp, list_actions, "list_actions"))

    def play_action(action_name: str, action_set: str = "User Actions") -> dict:
        """Play a Photoshop action from a loaded action set.

        This is the primary way to run user actions, including actions that
        themselves call JavaScript files from Presets/Scripts.

        Dialogs are suppressed (DialogModes.NO / playbackDisplayDialogs = NO).

        Args:
            action_name: Exact action name as shown in the Actions panel.
            action_set: Exact action set name. Defaults to "User Actions".

        Returns:
            dict: success flag, action name, set name, and optional error.

        """
        ps_app = PhotoshopApp()
        script = (
            "(function () {"
            "app.displayDialogs = DialogModes.NO;"
            "app.playbackDisplayDialogs = DialogModes.NO;"
            f'app.doAction("{_jsx_string(action_name)}", "{_jsx_string(action_set)}");'
            'return JSON.stringify({played: true});'
            "})()"
        )
        try:
            raw = ps_app.execute_javascript(script)
            parsed = _parse_json_result(raw)
            if isinstance(parsed, dict) and parsed.get("success") is False:
                return {
                    "success": False,
                    "action_name": action_name,
                    "action_set": action_set,
                    "error": parsed.get("error", raw),
                }
            return {
                "success": True,
                "action_name": action_name,
                "action_set": action_set,
                "result": parsed,
            }
        except Exception as e:
            return {
                "success": False,
                "action_name": action_name,
                "action_set": action_set,
                "error": str(e),
            }

    registered_tools.append(register_tool(mcp, play_action, "play_action"))

    def create_action_set(set_name: str) -> dict:
        """Create a new Photoshop action set in the Actions panel.

        Args:
            set_name: Name of the action set to create.

        Returns:
            dict: success flag and set name.

        """
        ps_app = PhotoshopApp()
        script = (
            "(function () {"
            "var desc = new ActionDescriptor();"
            "var ref = new ActionReference();"
            'ref.putClass(charIDToTypeID("ASet"));'
            'desc.putReference(charIDToTypeID("null"), ref);'
            f'desc.putString(charIDToTypeID("Nm  "), "{_jsx_string(set_name)}");'
            'executeAction(charIDToTypeID("Mk  "), desc, DialogModes.NO);'
            'return JSON.stringify({created: true});'
            "})()"
        )
        try:
            raw = ps_app.execute_javascript(script)
            parsed = _parse_json_result(raw)
            if isinstance(parsed, dict) and parsed.get("success") is False:
                return {"success": False, "set_name": set_name, "error": parsed.get("error", raw)}
            return {"success": True, "set_name": set_name, "result": parsed}
        except Exception as e:
            return {"success": False, "set_name": set_name, "error": str(e)}

    registered_tools.append(register_tool(mcp, create_action_set, "create_action_set"))

    def create_action_with_script(
        action_name: str,
        script_path: str,
        action_set: str = "MCP Actions",
        create_set_if_missing: bool = True,
    ) -> dict:
        """Create a Photoshop action whose recorded step runs a JSX file.

        Photoshop starts recording when the action is created. This tool then
        inserts an "AdobeScriptAutomation Scripts" step pointing at script_path
        and stops recording. The script is executed once during recording.

        On Photoshop 2026 the Action Manager "make" command is currently
        unavailable via COM/ExtendScript ("Der Befehl erstellen ist momentan
        nicht verfuegbar"). Prefer execute_jsx_file to run a JSX file, and
        play_action to run existing Actions-panel actions.

        Args:
            action_name: Name of the new action.
            script_path: Absolute path to a .jsx file.
            action_set: Action set to place the action in.
            create_set_if_missing: Create the set first if it does not exist.

        Returns:
            dict: success flag plus action/set/script metadata.

        """
        path = Path(script_path)
        if not path.is_file():
            return {
                "success": False,
                "error": f"Script file not found: {script_path}",
            }

        ps_app = PhotoshopApp()
        jsx_path = _jsx_string(str(path.resolve()))
        set_name = _jsx_string(action_set)
        act_name = _jsx_string(action_name)
        create_set_js = "true" if create_set_if_missing else "false"

        script = f"""
(function () {{
    app.displayDialogs = DialogModes.NO;
    app.playbackDisplayDialogs = DialogModes.NO;

    function setExists(name) {{
        var i = 1;
        while (true) {{
            var ref = new ActionReference();
            ref.putIndex(charIDToTypeID("ASet"), i);
            var desc;
            try {{ desc = executeActionGet(ref); }} catch (e) {{ return false; }}
            if (desc.getString(charIDToTypeID("Nm  ")) === name) return true;
            i++;
        }}
    }}

    function actionExists(setName, actionName) {{
        var i = 1;
        while (true) {{
            var ref = new ActionReference();
            ref.putIndex(charIDToTypeID("ASet"), i);
            var desc;
            try {{ desc = executeActionGet(ref); }} catch (e) {{ return false; }}
            if (desc.getString(charIDToTypeID("Nm  ")) === setName) {{
                var count = desc.hasKey(charIDToTypeID("NmbC"))
                    ? desc.getInteger(charIDToTypeID("NmbC")) : 0;
                for (var j = 1; j <= count; j++) {{
                    var aref = new ActionReference();
                    aref.putIndex(charIDToTypeID("Actn"), j);
                    aref.putIndex(charIDToTypeID("ASet"), i);
                    try {{
                        var adesc = executeActionGet(aref);
                        if (adesc.getString(charIDToTypeID("Nm  ")) === actionName) return true;
                    }} catch (e2) {{}}
                }}
                return false;
            }}
            i++;
        }}
    }}

    function step(label, fn) {{
        try {{
            fn();
            return null;
        }} catch (e) {{
            return label + ": " + e.toString();
        }}
    }}

    var setName = "{set_name}";
    var actionName = "{act_name}";
    var scriptFile = new File("{jsx_path}");
    if (!scriptFile.exists) {{
        return JSON.stringify({{success: false, error: "Script file not found"}});
    }}

    var err;
    if ({create_set_js} && !setExists(setName)) {{
        err = step("create_set", function () {{
            var setDesc = new ActionDescriptor();
            var setRef = new ActionReference();
            setRef.putClass(stringIDToTypeID("actionSet"));
            setDesc.putReference(charIDToTypeID("null"), setRef);
            setDesc.putString(charIDToTypeID("Nm  "), setName);
            executeAction(charIDToTypeID("Mk  "), setDesc, DialogModes.NO);
        }});
        if (err) return JSON.stringify({{success: false, error: err}});
    }}

    if (actionExists(setName, actionName)) {{
        return JSON.stringify({{
            success: true,
            already_existed: true,
            action_name: actionName,
            action_set: setName
        }});
    }}

    err = step("create_action", function () {{
        var mkDesc = new ActionDescriptor();
        var mkRef = new ActionReference();
        mkRef.putClass(stringIDToTypeID("action"));
        mkDesc.putReference(charIDToTypeID("null"), mkRef);
        mkDesc.putString(charIDToTypeID("Nm  "), actionName);
        var atRef = new ActionReference();
        atRef.putName(stringIDToTypeID("actionSet"), setName);
        mkDesc.putReference(charIDToTypeID("At  "), atRef);
        executeAction(charIDToTypeID("Mk  "), mkDesc, DialogModes.NO);
    }});
    if (err) return JSON.stringify({{success: false, error: err}});

    err = step("insert_script", function () {{
        var runDesc = new ActionDescriptor();
        runDesc.putPath(charIDToTypeID("jsCt"), scriptFile);
        runDesc.putString(charIDToTypeID("jsMs"), "undefined");
        executeAction(stringIDToTypeID("AdobeScriptAutomation Scripts"), runDesc, DialogModes.NO);
    }});
    if (err) return JSON.stringify({{success: false, error: err, action_created: true}});

    err = step("stop_recording", function () {{
        var stopDesc = new ActionDescriptor();
        executeAction(charIDToTypeID("Stop"), stopDesc, DialogModes.NO);
    }});

    return JSON.stringify({{
        success: true,
        already_existed: false,
        action_name: actionName,
        action_set: setName,
        script_path: scriptFile.fsName,
        stop_error: err
    }});
}})()
"""
        try:
            raw = ps_app.execute_javascript(script)
            parsed = _parse_json_result(raw)
            if isinstance(parsed, dict) and parsed.get("success") is False:
                return {
                    "success": False,
                    "action_name": action_name,
                    "action_set": action_set,
                    "script_path": str(path.resolve()),
                    "error": parsed.get("error", raw),
                }
            if not isinstance(parsed, dict):
                return {
                    "success": False,
                    "error": f"Unexpected create_action_with_script result: {raw}",
                }
            parsed.setdefault("success", True)
            parsed["script_path"] = str(path.resolve())
            return parsed
        except Exception as e:
            return {
                "success": False,
                "action_name": action_name,
                "action_set": action_set,
                "script_path": str(path.resolve()),
                "error": str(e),
            }

    registered_tools.append(
        register_tool(mcp, create_action_with_script, "create_action_with_script")
    )

    return registered_tools
