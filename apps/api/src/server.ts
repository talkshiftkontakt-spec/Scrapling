import { buildApp } from "./app.js";
import { readEnv } from "@design-intelligence/shared";

const app = buildApp();
const env = readEnv();

async function main() {
  await app.listen({ host: "0.0.0.0", port: env.PORT });
}

main().catch((error) => {
  app.log.error(error);
  process.exit(1);
});
