# LingoLogy — Dzień 0: checklist techniczny + prompty do Cursora

Wykonaj **przed** uruchomieniem Meta Ads (sekcja 16 głównego planu).  
Każdy punkt: co sprawdzić → jak → prompt do Cursora (jeśli techniczne).

---

## 1. Lingotutor — ścieżka mobile

**Co:** Link działa bez logowania; wiesz ile kliknięć do potwierdzenia.

**Prompt do Cursora:**
```
Przejdź ścieżkę użytkownika na mobile (symulacja):
1. Otwórz lingology.pl na telefonie lub DevTools mobile view
2. Kliknij główne CTA "Umów konsultację"
3. Zapisz: czy wymaga logowania przed wyborem terminu, ile pól formularza, ile kliknięć do potwierdzenia
4. Sprawdź czy link to Lingotutor (nie stary formularz mailowy)
5. Zmierz czas ładowania strony docelowej
Wynik: krótka tabela kroków + rekomendacja jeśli >3 kliknięcia lub wolne ładowanie
```

**Checklist ręczny:**
- [ ] CTA hero → Lingotutor (nie formularz)
- [ ] Działa na iPhone + Android
- [ ] Potwierdzenie terminu ≤ 4 kliknięcia od wejścia na stronę

---

## 2. Lingotutor — wolne terminy i Plan B

**Co:** Wiesz, jak daleko w przód widać sloty. Masz plan B, gdy brak terminu „w tym tygodniu”.

**Prompt do Cursora / zadanie dla siebie:**
```
Sprawdź w Lingotutor:
1. Najbliższy wolny slot konsultacji (data + godzina)
2. Ile dni w przód są dostępne terminy konsultacji
3. Ile slotów konsultacji tygodniowo realnie możesz przyjąć przy ~20 uczniach (np. max 3-5 konsultacji/tydzień na start kampanii)
Jeśli brak slotu w ciągu 7 dni — opisz co pokazuje UI użytkownikowi
```

**Plan B (wdroż na stronie / w Lingotutor):**

| Sytuacja | Co robi użytkownik | Co robisz Ty |
|----------|-------------------|--------------|
| Brak slotu w 7 dni | Widzi komunikat + formularz „Zapisz się na listę” | Otwierasz 2–3 sloty konsultacji w najbliższym tygodniu **przed** startem ads |
| Tylko slot za 10+ dni | Tekst: „Najbliższy termin: [data]. Zarezerwuj teraz — miejsca ograniczone.” | Nie kłam o „dziś”; urgency = prawda |
| Zero slotów | CTA zmienia się na „Napisz — podam termin w 24h” + formularz backup | Odpowiedź w 24h z linkiem do konkretnego slotu |

**Checklist:**
- [ ] Min. **3 sloty konsultacji** otwarte w najbliższych 7 dniach przed startem ads
- [ ] Komunikat na stronie jeśli Lingotutor pusty (nie martwy link)
- [ ] Plan B przetestowany ręcznie

---

## 3. Szybkość strony (mobile)

**Prompt do Cursora:**
```
Uruchom PageSpeed Insights lub Lighthouse dla https://www.lingology.pl/ w trybie mobile.
Podaj: Performance score, LCP, CLS, główne rekomendacje.
Jeśli Performance < 70 — wypisz 3 najszybsze poprawki (obrazy, fonty, JS) bez pełnego redesignu.
```

**Checklist:**
- [ ] Performance mobile ≥ 70 (lub wiesz, co blokuje i kiedy naprawisz)
- [ ] Hero + cena ładują się bez długiego białego ekranu

---

## 4. Meta Pixel + event CTA

**Prompt do Cursora:**
```
Sprawdź na lingology.pl:
1. Czy Meta Pixel (Facebook Pixel) jest zainstalowany — szukaj fbq w kodzie strony lub Meta Pixel Helper
2. Czy jest event na kliknięcie linku do Lingotutor (Lead lub custom event np. ScheduleConsultation)
3. Jeśli Lingotutor to inna domena (np. lingotutor.*) — czy Pixel jest też tam
Jeśli brak — dodaj Pixel na lingology.pl i event onclick na wszystkich CTA Lingotutor.
Podaj ID Pixela i nazwę eventu.
```

**Checklist:**
- [ ] Pixel aktywny (Meta Events Manager pokazuje PageView)
- [ ] Event na klik CTA Lingotutor
- [ ] Pixel na domenie Lingotutor jeśli osobna

---

## 5. UTM-y na linkach Lingotutor

**Prompt do Cursora:**
```
Zaktualizuj wszystkie linki CTA do Lingotutor na lingology.pl:
- Hero główny CTA
- Sekcja konsultacji na dole
- Linki w stopce jeśli są

Domyślny link bez kampanii: utm_source=website&utm_medium=organic&utm_campaign=7d

Przygotuj też w komentarzu / docs gotowe URL z UTM dla:
- meta paid barrier_a, creds_b, comeback_c
- facebook organic, fb_group, linkedin dm, referral student

Nie psuj istniejącego URL Lingotutor — tylko dodaj parametry query string.
```

**Checklist:**
- [ ] Wszystkie CTA mają UTM (min. website organic)
- [ ] 3 URL-e gotowe do wklejenia w Meta Ads (z pliku meta-ads-texts.md)

---

## 6. GA4 / analityka

**Prompt do Cursora:**
```
Sprawdź czy na lingology.pl jest Google Analytics 4 (gtag G-XXXX lub GTM).
Jeśli brak — dodaj GA4 z measurement ID (użytkownik poda ID) lub instrukcję gdzie wkleić.
Skonfiguruj event click na CTA Lingotutor jako generate_lead lub custom event.
```

**Checklist:**
- [ ] GA4 zbiera ruch
- [ ] Wiesz, jak sprawdzić źródła w Realtime w trakcie kampanii

---

## 7. Meta title, description, OG image

**Prompt do Cursora:**
```
Sprawdź lingology.pl:
- <title> i meta description (czy opisują dorosłych + mówienie + konsultacja 0 zł)
- og:title, og:description, og:image — czy istnieją i czy obrazek to min. 1200x630
Jeśli brak OG — dodaj z portretem Kuby lub zdjęciem przy laptopie.
Podaj aktualne wartości i proponowane poprawki.
```

**Checklist:**
- [ ] Title/description OK
- [ ] OG image — podgląd linku w Messenger/WhatsApp wygląda profesjonalnie

---

## 8. Hierarchia CTA vs formularz backup

**Prompt do Cursora:**
```
Na lingology.pl porównaj wizualnie:
- główny CTA Lingotutor (kolor, rozmiar, pozycja)
- formularz "napisz / umów konsultację" na dole strony
Formularz backup powinien być wyraźnie słabszy (mniejszy przycisk, niższy kontrast, niżej).
Zaproponuj minimalną zmianę CSS/klas jeśli oba wyglądają równie ważnie.
```

**Checklist:**
- [ ] Jeden dominujący CTA (Lingotutor)
- [ ] Formularz backup nie konkuruje

---

## 9. Cena + wiarygodność above the fold (mobile)

**Prompt do Cursora:**
```
Na mobile viewport 390x844 sprawdź lingology.pl bez scrolla:
- Czy widać cenę (od 80 zł / 55 min)?
- Czy widać element wiarygodności (1200+ lekcji lub psychologia UJ)?
- Czy widać główny CTA?
Zrzut opisu co widać / czego brakuje.
```

**Checklist:**
- [ ] Cena widoczna bez scrolla
- [ ] Min. 1 linia trust (1200+ / UJ) widoczna lub tuż pod hero

---

## 10. RODO przy Lingotutor

**Checklist:**
- [ ] Informacja o przetwarzaniu danych przy zapisie w Lingotutor
- [ ] Screen App w materiałach — dane uczniów nieczytelne (sprawdź zoom 100%)

---

## 11. Dokumenty operacyjne gotowe

- [ ] `lingology-skrypt-konsultacji.md` — wydruk / Notion / drugi monitor
- [ ] `lingology-meta-ads-texts.md` — 3 kreatywy skopiowane do Ads Manager
- [ ] Arkusz Google: data | źródło UTM | imię | status
- [ ] Szablony mail + SMS follow-up 2h (w skrypcie) — zapisane w telefonie jako notatki

---

## 12. Kreatyw B — wersja dojrzalsza (przed wklejeniem do Meta)

Używaj w ads **B**:

> **Nie:** „student psychologii UJ” (może brzmieć niepewnie dla 35+)  
> **Tak:** „w trakcie studiów psychologicznych na Uniwersytecie Jagiellońskim” + „1200+ lekcji 1:1”

Pełne teksty → `lingology-meta-ads-texts.md`

---

## Podsumowanie dnia 0

| # | Status |
|---|--------|
| Lingotutor mobile OK | ☐ |
| Min. 3 sloty konsultacji w 7 dni | ☐ |
| Plan B jeśli brak terminów | ☐ |
| PageSpeed mobile OK | ☐ |
| Pixel + event CTA | ☐ |
| UTM-y | ☐ |
| GA4 | ☐ |
| OG image | ☐ |
| CTA hierarchy | ☐ |
| Cena + trust mobile | ☐ |
| Skrypt + szablony follow-up | ☐ |
| Meta Ads 3 kreatywy w Managerze | ☐ |

**Dopiero gdy ≥10/12 — odpal budżet Meta (dzień 1 kampanii).**
