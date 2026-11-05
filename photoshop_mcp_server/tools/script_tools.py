"""Script execution MCP tools for Photoshop."""

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.registry import register_tool


def register(mcp):
    """Register script execution tools.

    Args:
        mcp: The MCP server instance.

    """

    def execute_jsx(script: str) -> dict:
        """Execute JavaScript (JSX) code in Photoshop.

        This is a universal tool that can run any Photoshop JavaScript code,
        giving access to the full Photoshop API including operations not covered
        by other dedicated tools.

        A JSON.stringify polyfill is automatically injected since Photoshop's
        ExtendScript engine is based on ECMAScript 3 which lacks native JSON.

        Look up classes, members and enums with the photoshop_dom_* tools before
        writing the script.

        Args:
            script: JavaScript/JSX code to execute in Photoshop.
                    The script should return a value (string, number, or JSON string).
                    If no return statement is present, the last expression is returned.

        Returns:
            dict: Result containing 'success' flag and 'result' with the script output,
                  or 'error' if execution failed.

        Examples:
            Get layer count:
                script: "app.activeDocument.artLayers.length;"

            Get all layer names as JSON:
                script: '''
                var doc = app.activeDocument;
                var names = [];
                for (var i = 0; i < doc.artLayers.length; i++) {
                    names.push(doc.artLayers[i].name);
                }
                JSON.stringify(names);
                '''

            Create a rectangle shape:
                script: '''
                var doc = app.activeDocument;
                var layer = doc.artLayers.add();
                layer.name = "Rectangle";
                var selection = doc.selection;
                selection.select([[100,100],[500,100],[500,400],[100,400]]);
                selection.fill(app.foregroundColor);
                selection.deselect();
                "done";
                '''

        """
        ps_app = PhotoshopApp()
        try:
            result = ps_app.execute_javascript(script)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    tool_name = register_tool(mcp, execute_jsx, "execute_jsx")
    registered = [tool_name]

    def execute_jsx_file(file_path: str) -> dict:
        """Execute a .jsx file on disk in Photoshop via $.evalFile.

        Use this for scripts in Presets/Scripts or any other folder, including
        scripts that user actions also call.

        Args:
            file_path: Absolute path to the .jsx file.

        Returns:
            dict: success flag and eval result or error.

        """
        from pathlib import Path

        path = Path(file_path)
        if not path.is_file():
            return {"success": False, "error": f"Script file not found: {file_path}"}

        jsx_path = (
            str(path.resolve())
            .replace("\\", "\\\\")
            .replace('"', '\\"')
        )
        script = (
            "(function () {"
            "app.displayDialogs = DialogModes.NO;"
            f'var f = new File("{jsx_path}");'
            "if (!f.exists) return JSON.stringify({success:false, error:'file not found'});"
            "var result = $.evalFile(f);"
            "return (result === undefined || result === null) ? 'ok' : String(result);"
            "})()"
        )
        ps_app = PhotoshopApp()
        try:
            result = ps_app.execute_javascript(script)
            return {"success": True, "file_path": str(path.resolve()), "result": result}
        except Exception as e:
            return {"success": False, "file_path": str(path.resolve()), "error": str(e)}

    registered.append(register_tool(mcp, execute_jsx_file, "execute_jsx_file"))
    return registered
