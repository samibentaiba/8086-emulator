"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.packageSite = packageSite;
/** Prepare the public browser files for GitHub Pages or another static host. */
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const public_assets_1 = require("./public-assets");
async function packageSite() {
    const root = await (0, promises_1.realpath)((0, node_path_1.resolve)(__dirname, ".."));
    const output = (0, node_path_1.resolve)(root, "dist");
    // Never permit the recursive cleanup to escape the fixed build directory.
    if ((0, node_path_1.dirname)(output) !== root || (0, node_path_1.basename)(output) !== "dist") {
        throw new Error("Invalid static output directory");
    }
    const existing = await (0, promises_1.lstat)(output).catch((error) => {
        if (error.code === "ENOENT")
            return undefined;
        throw error;
    });
    if (existing?.isSymbolicLink())
        throw new Error("Static output must not be a symbolic link");
    // Check every input before replacing an existing successful build.
    const files = await Promise.all(public_assets_1.PUBLIC_ASSETS.map(async (name) => ({
        name, content: await (0, promises_1.readFile)((0, node_path_1.resolve)(root, name)),
    })));
    await (0, promises_1.rm)(output, { recursive: true, force: true });
    await (0, promises_1.mkdir)(output);
    await Promise.all(files.map(file => (0, promises_1.writeFile)((0, node_path_1.resolve)(output, file.name), file.content)));
    await (0, promises_1.writeFile)((0, node_path_1.resolve)(output, ".nojekyll"), "");
    return output;
}
if (require.main === module) {
    packageSite().then(output => console.log(`Static website: ${output}`)).catch((error) => {
        console.error(error instanceof Error ? error.message : String(error));
        process.exitCode = 1;
    });
}
