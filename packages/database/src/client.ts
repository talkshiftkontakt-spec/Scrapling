import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";

import { readEnv } from "@design-intelligence/shared";

const env = readEnv();
const pool = new Pool({ connectionString: env.DATABASE_URL });

export const db = drizzle(pool);
export { pool };
