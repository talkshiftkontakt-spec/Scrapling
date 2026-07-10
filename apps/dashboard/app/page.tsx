const cards = [
  {
    title: "Reference Search",
    description: "Query high-quality design references after scoring, deduplication, and Qdrant indexing."
  },
  {
    title: "Component Library",
    description: "Browse hero, pricing, dashboard, testimonial, and CTA crops as first-class assets."
  },
  {
    title: "Design Specs",
    description: "Generate structured design specifications before any downstream code generation."
  },
  {
    title: "Design Critic",
    description: "Evaluate generated UI against premium references and flag generic outputs."
  }
];

export default function HomePage() {
  return (
    <main style={{ padding: 40, maxWidth: 1200, margin: "0 auto" }}>
      <header style={{ marginBottom: 32 }}>
        <p style={{ textTransform: "uppercase", letterSpacing: 2, color: "#8ea0c9" }}>Design Intelligence Platform</p>
        <h1 style={{ fontSize: 48, margin: "8px 0 12px" }}>Curated design intelligence built on Scrapling ingestion</h1>
        <p style={{ maxWidth: 780, color: "#c6d1ea", lineHeight: 1.6 }}>
          This admin dashboard is the curator-facing layer for discovery, scoring, component extraction, semantic search,
          design-spec generation, and post-generation critique.
        </p>
      </header>

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20 }}>
        {cards.map((card) => (
          <article key={card.title} style={{ background: "#131a31", border: "1px solid #263154", borderRadius: 20, padding: 24 }}>
            <h2 style={{ marginTop: 0, marginBottom: 12 }}>{card.title}</h2>
            <p style={{ margin: 0, color: "#c6d1ea", lineHeight: 1.5 }}>{card.description}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
