async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderHealth(data) {
  const health = document.getElementById("health");
  health.innerHTML = `
    <h2>Status</h2>
    <p>Stan: <strong>${data.status}</strong></p>
    <p>Nadchodzące mecze: <strong>${data.upcoming_events}</strong></p>
    <p>Baza: <code>${data.db_path}</code></p>
  `;
}

function renderEvents(events) {
  const container = document.getElementById("events");
  if (!events.length) {
    container.innerHTML = "<h2>Mecze</h2><p>Brak nadchodzących meczów.</p>";
    return;
  }

  container.innerHTML = `<h2>Mecze (${events.length})</h2>` + events.map((event) => {
    const stats = event.prematch_stats;
    const odds = event.odds || [];
    const oddsHtml = odds.slice(0, 6).map((item) =>
      `<span class="tag">${item.bookmaker}: ${item.market} ${item.selection} @ ${item.odds_decimal}</span>`
    ).join("");

    const statsHtml = stats ? `
      <div class="stats">
        xG: ${stats.home_season_xg ?? "-"} vs ${stats.away_season_xg ?? "-"} |
        H2H: ${(stats.h2h || []).length}
      </div>
    ` : `<div class="stats">Brak statystyk</div>`;

    return `
      <article class="event">
        <h3>${event.home_participant} vs ${event.away_participant}</h3>
        <div class="meta">
          <span class="tag">${event.sport}</span>
          <span class="tag">${event.league}</span>
          <span>${new Date(event.start_time).toLocaleString()}</span>
        </div>
        ${statsHtml}
        <div class="odds">${oddsHtml || "Brak kursów"}</div>
      </article>
    `;
  }).join("");
}

async function refresh() {
  const sport = document.getElementById("sportFilter").value;
  const query = sport ? `?sport=${sport}` : "";
  const [health, events] = await Promise.all([
    fetchJson("/health"),
    fetchJson(`/upcoming${query}`),
  ]);
  renderHealth(health);
  renderEvents(events);
}

document.getElementById("refreshBtn").addEventListener("click", refresh);
document.getElementById("sportFilter").addEventListener("change", refresh);
refresh().catch((error) => {
  document.getElementById("events").innerHTML = `<p>Błąd: ${error.message}</p>`;
});
