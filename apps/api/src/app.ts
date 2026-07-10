import Fastify from "fastify";
import fastifyStatic from "@fastify/static";
import { join } from "node:path";

import { createLogger, readServerEnv } from "@design-intelligence/shared";

import { registerRoutes } from "./routes/index.js";

export function buildApp() {
  const logger = createLogger("design-intelligence-api");
  const env = readServerEnv();
  const app = Fastify({ loggerInstance: logger });

  const libraryRoot = join(process.cwd(), env.DESIGN_LIBRARY_PATH);
  app.register(fastifyStatic, {
    root: libraryRoot,
    prefix: "/static/",
    decorateReply: false
  });

  registerRoutes(app as never);

  return app;
}
