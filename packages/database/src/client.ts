import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";

import { readDatabaseEnv } from "@design-intelligence/shared";

let database: ReturnType<typeof drizzle> | null = null;
let pool: Pool | null = null;

export function getPool(): Pool {
  if (pool) {
    return pool;
  }

  const env = readDatabaseEnv();
  pool = new Pool({ connectionString: env.DATABASE_URL });
  return pool;
}

export function getDb() {
  if (database) {
    return database;
  }

  database = drizzle(getPool());
  return database;
}
