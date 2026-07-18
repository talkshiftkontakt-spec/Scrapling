# Inne decyzje wizualne (nie tylko fonty)

## Radius (drabinka)
| Element | Soft Instrument | Precision | Editorial |
|---|---|---|---|
| Input / chip | 8–10px | 6–8px | 8–10px |
| Button | pill OK | pill OK | pill OK |
| Card | 12–16px | 10–14px | 14–18px |
| Product stage | 18–24px | 16–20px | 20–24px |

Nie dawaj `border-radius: 999px` na karty i stage.

## Cienie
- 1 warstwa, duży blur, niska opacity
- Na dark: częściej **1px border** niż cień
- Unikaj: `0 10px 15px -3px` × 3 stacked (Material default look)

## Spacing pierwszego viewportu
- Nav → H1: 48–80px
- H1 → sub: 16–24px
- sub → CTA: 24–32px
- CTA → visual: 40–72px
- Boki: min 24px mobile / 48px desktop

## CTA
- Primary solid + secondary ghost
- Ta sama wysokość (~44–48px)
- Jeden akcent koloru na primary **albo** ink/black

## Tło
| Tak | Nie |
|---|---|
| Off-white `#F7F6F3` | Pure `#FFF` bez tekstury/oddechu |
| Warm near-black `#0F0E0C` | Random purple mesh |
| Foto full-bleed z overlay | Stock handshake |
| Dot grid bardzo delikatny | Noise na całym UI + glow |

## Ilustracja / product proof
1. Real product UI (przycięty, 1 workflow)
2. Albo 1 mocna ilustracja custom (Clay-level)
3. Albo foto atmosferyczne
4. Nie: 6 ikonek Lucide w kółkach

## Motion (2–3 max)
- Fade/slide stage
- Composer focus
- Opcjonalnie ticker metryk **albo** subtle parallax — nie oba + grain shimmer + glow
