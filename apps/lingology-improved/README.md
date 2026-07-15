# LingoLogy improved preview

Static visual refresh of [lingology.pl](https://www.lingology.pl/), cloned content + assets, redesigned with patterns inspired by the DesignLibrary reference pack (editorial serif hierarchy, photo-led mid bands, product/app showcase, quieter card density).

## Run

```bash
cd apps/lingology-improved
python3 -m http.server 3300 --bind 0.0.0.0
```

Open http://localhost:3300

## What changed vs original

- Kept brand: cream / teal / Cormorant + DM Sans
- Varied section rhythm (text band → photo strip → editorial steps → offers → app device)
- Stronger App showcase (device frame + real screenshot)
- One hero testimonial + quieter secondary quotes
- Removed theme-switcher noise from marketing chrome
- Primary vs text-link CTA hierarchy
