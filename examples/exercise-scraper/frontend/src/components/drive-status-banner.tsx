"use client";

import { useEffect, useState } from "react";
import { fetchDriveStatus } from "@/lib/api";
import type { DriveStatus } from "@/lib/types";

export function DriveStatusBanner() {
  const [status, setStatus] = useState<DriveStatus | null>(null);

  useEffect(() => {
    fetchDriveStatus()
      .then(setStatus)
      .catch(() => setStatus(null));
  }, []);

  if (!status || status.configured) {
    return null;
  }

  return (
    <div className="rounded-[1.25rem] border border-[#e8d4a8] bg-[#fff6e8] px-4 py-3 text-sm text-[#7a5a12]">
      <p className="font-semibold">Google Drive nie jest skonfigurowany</p>
      <p className="mt-1">
        Ustaw <code className="rounded bg-white px-1">GOOGLE_DRIVE_ROOT_FOLDER_ID</code> oraz poświadczenia
        serwisowe, aby włączyć synchronizację. Zobacz{" "}
        <code className="rounded bg-white px-1">docs/GOOGLE-DRIVE-SETUP.md</code>.
      </p>
      {!status.package_installed ? (
        <p className="mt-2">Brak pakietu Drive: <code>pip install -e &quot;examples/exercise-scraper[drive]&quot;</code></p>
      ) : null}
    </div>
  );
}
