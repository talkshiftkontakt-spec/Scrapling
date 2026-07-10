import Fastify from "fastify";

import { createLogger, readEnv } from "@design-intelligence/shared";

import { registerRoutes } from "./routes/index.js";

export function buildApp() {
  const env = readEnv();
  const logger = createLogger("design-intelligence-api");

  const app = Fastify({ logger });
  app.decorate("appEnv", env);

  registerRoutes(app);

  return app;
}
