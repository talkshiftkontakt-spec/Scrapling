import { ReferenceBrowser } from "../components/reference-browser";
import { fetchReferences, fetchStats } from "../lib/api";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [references, stats] = await Promise.all([fetchReferences(150), fetchStats()]);

  return <ReferenceBrowser references={references} stats={stats} />;
}
