/** Prepare the public browser files for GitHub Pages or another static host. */
import { lstat, mkdir, readFile, realpath, rm, writeFile } from "node:fs/promises";
import { basename, dirname, resolve } from "node:path";
import { PUBLIC_ASSETS } from "./public-assets";

export async function packageSite(): Promise<string> {
  const root = await realpath(resolve(__dirname, ".."));
  const output = resolve(root, "dist");
  // Never permit the recursive cleanup to escape the fixed build directory.
  if (dirname(output) !== root || basename(output) !== "dist") {
    throw new Error("Invalid static output directory");
  }
  const existing = await lstat(output).catch((error: NodeJS.ErrnoException) => {
    if (error.code === "ENOENT") return undefined;
    throw error;
  });
  if (existing?.isSymbolicLink()) throw new Error("Static output must not be a symbolic link");

  // Check every input before replacing an existing successful build.
  const files = await Promise.all(PUBLIC_ASSETS.map(async name => ({
    name, content: await readFile(resolve(root, name)),
  })));
  await rm(output, { recursive: true, force: true });
  await mkdir(output);
  await Promise.all(files.map(file => writeFile(resolve(output, file.name), file.content)));
  await writeFile(resolve(output, ".nojekyll"), "");
  return output;
}

if (require.main === module) {
  packageSite().then(output => console.log(`Static website: ${output}`)).catch((error: unknown) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}
