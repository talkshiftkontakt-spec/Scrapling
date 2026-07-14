import { readServerEnv } from "@design-intelligence/shared";

import { buildApp } from "./app.js";

const app = buildApp();
const env = readServerEnv();

async function main() {
  await app.listen({ host: "0.0.0.0", port: env.PORT });
}

main().catch((error) => {
  app.log.error(error);
  process.exit(1);
});
