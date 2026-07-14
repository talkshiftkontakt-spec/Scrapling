import Fastify from "fastify";
import fastifyStatic from "@fastify/static";
import { dirname, isAbsolute, join } from "node:path";
import { fileURLToPath } from "node:url";

import { createLogger, readServerEnv } from "@design-intelligence/shared";

import { registerRoutes } from "./routes/index.js";

function resolveLibraryRoot(pathFromEnv: string): string {
  if (isAbsolute(pathFromEnv)) {
    return pathFromEnv;
  }

  const currentFile = fileURLToPath(import.meta.url);
  const monorepoRoot = join(dirname(currentFile), "../../..");
  return join(monorepoRoot, pathFromEnv);
}

export function buildApp() {
  const logger = createLogger("design-intelligence-api");
  const env = readServerEnv();
  const app = Fastify({ loggerInstance: logger });

  const libraryRoot = resolveLibraryRoot(env.DESIGN_LIBRARY_PATH);
  app.register(fastifyStatic, {
    root: libraryRoot,
    prefix: "/static/",
    decorateReply: false
  });

  registerRoutes(app as never);

  return app;
}
