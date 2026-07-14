import { processPendingWebsites } from "./lib.js";

const limit = Number(process.argv[2] ?? "20");

const result = await processPendingWebsites(Number.isFinite(limit) ? limit : 20);
console.log(JSON.stringify(result, null, 2));
