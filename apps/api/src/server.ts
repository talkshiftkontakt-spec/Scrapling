import { buildApp } from "./app.js";

const app = buildApp();

async function main() {
  await app.listen({ host: "0.0.0.0", port: app.appEnv.PORT });
}

main().catch((error) => {
  app.log.error(error);
  process.exit(1);
});
