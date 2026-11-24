/** Local preview server. Browser code and schematics are built from TypeScript. */
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { resolve, extname } from "node:path";
import { PUBLIC_ASSETS } from "./public-assets";

const root = resolve(__dirname, "..");
const port = Number(process.env.PORT || 8086);
if (!Number.isInteger(port) || port < 0 || port > 65535) {
  throw new Error("PORT must be an integer between 0 and 65535.");
}
// Serve only the website's public assets, never source/configuration files.
const assets = new Set<string>(PUBLIC_ASSETS);
const mime: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
};
const server = createServer(async (request, response) => {
  if (request.method !== "GET" && request.method !== "HEAD") {
    response.writeHead(405, { Allow: "GET, HEAD" }).end();
    return;
  }
  let name: string;
  try {
    name = decodeURIComponent(new URL(request.url || "/", "http://localhost").pathname).slice(1) || "index.html";
  } catch {
    response.writeHead(400).end("Invalid URL");
    return;
  }
  if (!assets.has(name)) {
    response.writeHead(404).end("Not found");
    return;
  }
  try {
    const content = await readFile(resolve(root, name));
    response.writeHead(200, {
      "Content-Type": mime[extname(name)],
      "Content-Length": content.length,
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    });
    response.end(request.method === "HEAD" ? undefined : content);
  } catch {
    response.writeHead(500).end("Build the workbench with npm run build first.");
  }
});
server.on("error", error => {
  console.error(error.message);
  process.exitCode = 1;
});
server.listen(port, "127.0.0.1", () => {
  const address = server.address();
  if (address && typeof address !== "string") {
    console.log(`Local: http://127.0.0.1:${address.port}/`);
  }
});
process.on("SIGINT", () => server.close());
process.on("SIGTERM", () => server.close());
