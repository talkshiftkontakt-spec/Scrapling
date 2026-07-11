"use client";

import { useEffect, useState } from "react";
import { checkApiHealth } from "@/lib/api";

export function ApiStatusBanner() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function probe() {
      const ok = await checkApiHealth();
      if (!cancelled) setOnline(ok);
    }

    probe();
    const timer = window.setInterval(probe, 5000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  if (online !== false) return null;

  return (
    <div className="rounded-[1.25rem] border border-[#e8b4a8] bg-[#f6d9d1] px-5 py-4 text-[var(--accent-deep)]">
      <p className="font-semibold">Backend nie działa</p>
      <p className="mt-2 text-sm leading-6">
        Uruchom API w osobnym terminalu:
        <code className="ml-2 rounded bg-white px-2 py-1 text-[var(--ink)]">
          ./examples/exercise-scraper/scripts/run-api.sh
        </code>
      </p>
    </div>
  );
}
