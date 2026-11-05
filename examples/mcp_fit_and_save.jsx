#target photoshop
/*
<javascriptresource>
<name>MCP Fit 800 and Save _mcp.jpg</name>
<about>Flattened copy, fit to 800x800, save as filename_mcp.jpg next to the original.</about>
<category>MCP</category>
<enableinfo>true</enableinfo>
</javascriptresource>
*/

(function () {
    app.displayDialogs = DialogModes.NO;

    if (app.documents.length === 0) {
        throw new Error("No active document");
    }

    var origDoc = app.activeDocument;
    var docName = origDoc.name;
    var docPath;
    try {
        docPath = origDoc.fullName;
    } catch (e) {
        throw new Error("Document must be saved on disk before running this script");
    }

    var pathSeparator = String(docPath).indexOf("\\") !== -1 ? "\\" : "/";
    var full = String(docPath);
    var directory = full.substring(0, full.lastIndexOf(pathSeparator) + 1);
    var dotIndex = docName.lastIndexOf(".");
    var baseName = dotIndex !== -1 ? docName.substring(0, dotIndex) : docName;
    var outFile = new File(directory + baseName + "_mcp.jpg");

    var dup = origDoc.duplicate(baseName + "_mcp", true);
    var w = dup.width.as("px");
    var h = dup.height.as("px");
    var maxDim = 800;
    var scale = Math.min(maxDim / w, maxDim / h, 1);
    if (scale < 1) {
        dup.resizeImage(
            UnitValue(w * scale, "px"),
            UnitValue(h * scale, "px"),
            dup.resolution,
            ResampleMethod.BICUBICSHARPER
        );
    }

    var jpg = new JPEGSaveOptions();
    jpg.quality = 8;
    jpg.embedColorProfile = true;
    jpg.formatOptions = FormatOptions.OPTIMIZEDBASELINE;
    jpg.matte = MatteType.NONE;
    dup.saveAs(outFile, jpg, true);
    dup.close(SaveOptions.DONOTSAVECHANGES);

    return outFile.fsName;
})();
