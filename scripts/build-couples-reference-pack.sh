#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${ROOT}/export/couples-us-references"
MIN_BYTES=80000
STAMP="$(date +%Y%m%d-%H%M%S)"
ARCHIVE="${ROOT}/export/couples-us-references-${STAMP}.zip"

rm -rf "${OUT}"
mkdir -p "${OUT}/screenshots" "${OUT}/docs"

python3 <<'PY'
import json, os, shutil, subprocess
from pathlib import Path

ROOT = Path("/workspace")
OUT = ROOT / "export/couples-us-references"
SCREEN = OUT / "screenshots"
MIN = 80_000

# website_name -> (modules for Us app, rationale PL, priority)
CURATED = {
    "Serotoninn": (["home", "daily-ritual", "hero"], "Hero ekranu głównego — duży emocjonalny element, ciepły editorial.", 1),
    "Bloom 1": (["home", "warm-ui"], "Ciepły home z dużą typografią i whitespace — wzorzec „Our Day”.", 1),
    "Joy Rush": (["playful", "wellbeing", "home"], "Playful energy — Sunday Morning, mikrointerakcje bez korpo-chłodu.", 1),
    "Heaven In Color": (["illustration", "home", "warm-ui"], "Ilustracja + pastelowa paleta — empty states i onboarding.", 1),
    "Emily Nixon": (["paper-ink", "memories", "storytelling", "gifts"], "Paper & Ink — timeline, opowieść, prezenty.", 1),
    "Floema": (["journal", "memories", "travel", "holiday"], "Journal + travel — Memories, Holiday Planner, timeline.", 1),
    "Lemaire": (["quiet-studio", "premium", "typography"], "Quiet Studio — spokojna typografia, premium daily use.", 1),
    "Bennett Clive": (["premium", "home"], "Premium lifestyle home — zaufanie i spokój.", 2),
    "Inkfish": (["quiet-studio", "editorial"], "Editorial calm — czytelność i hierarchia.", 2),
    "Gustaf Furusten Portfolio": (["warm-ui", "storytelling"], "Ciepła narracja wizualna.", 2),
    "Https Www Mosaicist Com": (["paper-ink", "craft"], "Rzemiosło i tekstura — Paper & Ink refined.", 2),
    "Burrito Madre": (["meals", "food"], "Meals — ciepły food bez diet-obsessive UI.", 1),
    "Living With Ibd": (["wellbeing", "health", "habits"], "Health tracking — check-in, nawyki, wellbeing tab.", 1),
    "Day One R Run": (["wellbeing", "fitness", "training"], "Fitness / streak — Training & kudos.", 1),
    "Mens Health Week": (["wellbeing", "health"], "Health awareness — prosty health UI.", 2),
    "David Whyte Experience": (["couple-growth", "reflection", "memories"], "Refleksja i głębia — Couple Growth / weekly reflection.", 1),
    "Magnet Lover": (["couple", "gifts", "warm-ui"], "Love & gifts — ciepły lifestyle dla pary.", 1),
    "James Breedlove Portfolio": (["couple", "emotional", "storytelling"], "Emocjonalna narracja — relacja jako historia.", 1),
    "Bridge": (["together", "shared"], "Metafora połączenia — Together tab.", 2),
    "Cocoon App": (["onboarding", "private-space", "app-shell"], "Prywatna przestrzeń dla dwojga — kluczowa metafora „Us”.", 1),
    "Cibby": (["onboarding", "app-shell", "mobile-ui"], "Mobilny app shell — bottom nav, onboarding.", 1),
    "Flowty": (["plan", "calendar", "tasks"], "Plan — kalendarz, zadania, planowanie.", 1),
    "Billow": (["finance", "app-ui"], "Finance app — wydatki i saldo (najlepszy finance capture w kolekcji).", 1),
    "Invoicemon": (["finance", "expenses"], "Expenses / faktury — split expenses UI.", 2),
    "Weppy": (["app-ui", "mobile-ui"], "Nowoczesny mobile product UI.", 2),
    "Units": (["home", "plan"], "Home management — Casa-like planowanie domu.", 2),
    "Kfc Rewards": (["streaks", "daily-engagement"], "Streak / loyalty — Duolingo-style daily ritual.", 1),
    "Loud Clear": (["shared-content", "storytelling"], "Editorial feed — Shared Content / link inbox.", 1),
}

db = subprocess.check_output(
    ["psql", os.environ["DATABASE_URL"], "-tAc", "SELECT id::text || chr(9) || website_name || chr(9) || coalesce(canonical_url,'') FROM websites"],
    text=True,
)
by_name = {}
for line in db.splitlines():
    parts = line.split("\t", 2)
    if len(parts) >= 2:
        by_name[parts[1]] = {"id": parts[0], "url": parts[2] if len(parts) > 2 else ""}

manifest = {
    "app": "Us — private life-management app for two",
    "target": "Google Antigravity reference pack",
    "viewport": "mobile-only (390x844)",
    "max_archive_mb": 200,
    "sites": [],
    "module_index": {},
    "skipped_broken_captures": [
        "Opennote", "Fruitful", "Casa", "Sarah Matt Wedding", "Ceremony Framer Template",
        "AÏDO", "Les Amis", "Alone in New York", "Flamingo Estate", "Fora",
        "— captures były puste/zepsute (<80KB); nie nadają się jako referencja",
    ],
}

lib = ROOT / "DesignLibrary/PageScreenshots"
total_bytes = 0

for name, (modules, why, priority) in sorted(CURATED.items(), key=lambda x: x[1][2]):
    row = by_name.get(name)
    if not row:
        continue
    wid = row["id"]
    src = lib / wid / "mobile"
    if not src.exists():
        continue
    files = sorted([p for p in src.glob("*.png") if p.stat().st_size >= MIN])
    if not files:
        continue

    slug = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")[:48]
    dest_dir = SCREEN / f"{priority:02d}-{slug}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for f in files:
        target = dest_dir / f.name
        shutil.copy2(f, target)
        copied.append({"file": f.name, "bytes": f.stat().st_size})
        total_bytes += f.stat().st_size

    entry = {
        "name": name,
        "url": row["url"],
        "modules": modules,
        "why": why,
        "priority": priority,
        "screenshots": copied,
        "folder": str(dest_dir.relative_to(OUT)),
    }
    manifest["sites"].append(entry)
    for m in modules:
        manifest["module_index"].setdefault(m, []).append(name)

manifest["site_count"] = len(manifest["sites"])
manifest["screenshot_count"] = sum(len(s["screenshots"]) for s in manifest["sites"])
manifest["total_bytes"] = total_bytes
manifest["total_mb"] = round(total_bytes / 1024 / 1024, 2)

(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Packed {manifest['site_count']} sites, {manifest['screenshot_count']} shots, {manifest['total_mb']} MB")
PY

# Master prompt + short guide for Antigravity
cp "/home/ubuntu/.cursor/projects/workspace/uploads/couples-app-master-prompt_72d4.md" "${OUT}/docs/couples-app-master-prompt.md"

python3 <<'PY'
from pathlib import Path
import json
OUT = Path("/workspace/export/couples-us-references")
manifest = json.loads((OUT / "manifest.json").read_text())

lines = [
    "# Us — paczka referencji dla Antigravity",
    "",
    "Mobilne screenshoty (390×844) wybrane pod **„Us”** — tylko strony z realnymi, czytelnymi capture'ami.",
    "",
    f"- Stron: **{manifest['site_count']}**",
    f"- Screenshotów: **{manifest['screenshot_count']}**",
    f"- Rozmiar: **{manifest['total_mb']} MB** (limit 200 MB)",
    "",
    "## Jak używać w Antigravity",
    "",
    "1. Wgraj cały folder `couples-us-references/` lub zip.",
    "2. Wklej prompt z `docs/couples-app-master-prompt.md`.",
    "3. Dodaj: *„Użyj screenshotów w `screenshots/` jako referencji wizualnych per moduł (patrz manifest.json). Nie kopiuj layoutu 1:1 — przenieś paletę, hierarchię hero, ciepło micro-copy i mobile patterns.”*",
    "",
    "## Mapowanie moduł → referencje",
    "",
]

module_hints = {
    "home": "Ekran „Our Day” — hero, daily strip",
    "daily-ritual": "Rytuał dzienny, streak",
    "onboarding": "Onboarding pary, invite code",
    "finance": "Shared Finances, settle up",
    "plan": "Plan tab — tasks, calendar",
    "together": "Finanse, cele, bucket list",
    "wellbeing": "Health, fitness, meals",
    "memories": "Journal, timeline",
    "couple-growth": "Weekly reflection, date ideas",
    "paper-ink": "Paper & Ink refined — serif + cream",
    "quiet-studio": "Quiet Studio — premium calm",
    "playful": "Sunday Morning — playful couples",
}

for mod in sorted(manifest["module_index"].keys()):
    sites = ", ".join(manifest["module_index"][mod])
    hint = module_hints.get(mod, "")
    lines.append(f"### `{mod}`")
    if hint:
        lines.append(f"{hint}")
    lines.append(f"- {sites}")
    lines.append("")

lines += ["## Lista stron (priorytet 1 = najważniejsze)", ""]
for site in manifest["sites"]:
    pri = "★" if site["priority"] == 1 else "·"
    mods = ", ".join(site["modules"])
    lines.append(f"- {pri} **{site['name']}** — {mods}")
    lines.append(f"  - {site['why']}")
    lines.append(f"  - {site['url']}")
    lines.append("")

(OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
PY

cd "${ROOT}/export"
rm -f couples-us-references-latest.zip
zip -rq "${ARCHIVE}" couples-us-references
ln -sfn "$(basename "${ARCHIVE}")" couples-us-references-latest.zip
ls -lh "${ARCHIVE}" couples-us-references-latest.zip
