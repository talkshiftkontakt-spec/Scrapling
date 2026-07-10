import Fastify from "fastify";

import { createLogger } from "@design-intelligence/shared";

import { registerRoutes } from "./routes/index.js";

export function buildApp() {
  const logger = createLogger("design-intelligence-api");
  const app = Fastify({ loggerInstance: logger });

  registerRoutes(app as never);

  return app;
}
