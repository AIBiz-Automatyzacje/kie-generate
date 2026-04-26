---
name: kie-generate
description: Generuje grafiki AI przez Kie.ai (Nano Banana 2 / Nano Banana Pro / GPT Image-2). Interaktywnie pyta o prompt i parametry, zapisuje do Marketing/media/ lub wskazanej lokalizacji.
allowed-tools: ["Bash", "Read", "Write", "Glob"]
---

# Kie Generate

Skill do generowania grafik AI przez API Kie.ai.

## Wybór modelu

Domyślnie używaj **GPT Image-2** — skrypt automatycznie wybiera wariant text-to-image lub image-to-image w zależności od tego czy podano `--image`.

Przełączaj się tylko gdy user wprost o to poprosi:

| User mówi | Przekaż `--model` |
|-----------|-------------------|
| (nic, default) | `gpt-image-2` |
| "Nano", "Nano Banana", "banana" | `nano-banana-2` |
| "pro", "wyższa jakość", "lepiej" | `nano-banana-pro` |

**GPT Image-2 ograniczenia:** brak `--resolution` i `--format` (skrypt je ignoruje), krótsza lista ratio (bez 1:4, 1:8, 4:1, 8:1). Jeśli user potrzebuje rozdzielczości lub formatu innego niż domyślne — przełącz na `nano-banana-2`.

## Wymagania

W `.env` workspace'u:

| Zmienna | Opis | Tryby |
|---------|------|-------|
| `KIE_API_KEY` | Klucz API Kie.ai (kie.ai) | wszystkie |
| `IMGBB_API_KEY` | Klucz API ImgBB (imgbb.com/api) — temporary hosting reference images | `edit`, `compose`, `remove-bg` |

Biblioteki Python: `requests`.

**Pierwsza konfiguracja:** jeśli user prosi o "setup", "konfigurację", "onboarding kie-generate" — przeprowadź go przez checklistę z [ONBOARDING.md](ONBOARDING.md).

## Tryby pracy

| Tryb | Opis | Kiedy użyć |
|------|------|------------|
| `generate` | text → image | Nowa grafika od zera |
| `edit` | image + instruction → image | Modyfikacja istniejącej grafiki |
| `compose` | multiple images + instruction → image | Łączenie elementów z kilku obrazków |
| `remove-bg` | image → image (transparent) | Usunięcie tła z grafiki |

## Workflow

1. **Rozpoznaj tryb** na podstawie inputu użytkownika:
   - Brak obrazków → `generate`
   - 1 obrazek + instrukcja edycji → `edit`
   - 2+ obrazków + instrukcja → `compose`
   - Użytkownik prosi o usunięcie tła → `remove-bg`

2. **Zapytaj o szczegóły** (jeśli nie podane):
   - Co ma być na grafice? (prompt)
   - Proporcje? (domyślnie 1:1, dla social media często 16:9)
   - Rozdzielczość? (1K/2K/4K, domyślnie 1K)
   - Gdzie zapisać? (domyślnie `Marketing/media/`)

3. **Zbuduj prompt** według zasad z [prompting-guide.md](prompting-guide.md):
   - 7-elementowa struktura (styl, scena, subject, kamera, światło, tekstury, negacje)
   - Wagi `(element:1.3)` dla kluczowych cech
   - Blok `TEXT CONTENT TO DISPLAY` jeśli są konkretne teksty

4. **Zastosuj brand** jeśli dotyczy Akademii Automatyzacji → [brand-rules.md](brand-rules.md)

5. **Wywołaj skrypt** i poinformuj o wyniku

## Użycie skryptu

```bash
# Generate (text → image) — domyślnie Nano Banana 2
python3 {baseDir}/scripts/kie_image.py generate "prompt" output.png
python3 {baseDir}/scripts/kie_image.py generate "prompt" output.png --ratio 16:9 --resolution 2K

# Generate z Nano Banana Pro (starszy model)
python3 {baseDir}/scripts/kie_image.py generate "prompt" output.png --model nano-banana-pro

# Generate / edit z GPT Image-2 (skrypt sam wybiera text-to-image vs image-to-image)
python3 {baseDir}/scripts/kie_image.py generate "prompt" output.png --model gpt-image-2 --ratio 16:9
python3 {baseDir}/scripts/kie_image.py edit "instruction" output.png --image input.png --model gpt-image-2

# Edit (image + instruction → image)
python3 {baseDir}/scripts/kie_image.py edit "instruction" output.png --image input.png

# Compose (multiple images → image)
python3 {baseDir}/scripts/kie_image.py compose "instruction" output.png --image img1.png --image img2.png

# Remove background
python3 {baseDir}/scripts/kie_image.py remove-bg input.png output.png
```

## Parametry

| Parametr | Opcje | Domyślnie |
|----------|-------|-----------|
| `--model` | nano-banana-2, nano-banana-pro, gpt-image-2 | nano-banana-2 |
| `--ratio` | 1:1, 1:4*, 1:8*, 2:3, 3:2, 3:4, 4:1*, 4:3, 4:5, 5:4, 8:1*, 9:16, 16:9, 21:9, auto | 1:1 |
| `--resolution` | 1K, 2K, 4K | 1K |
| `--format` | png, jpg | png |

*\* Proporcje 1:4, 1:8, 4:1, 8:1 — dostępne tylko w Nano Banana 2*
*\* GPT Image-2 ignoruje `--resolution` i `--format`; ratio musi być z listy: auto, 1:1, 5:4, 9:16, 21:9, 16:9, 4:3, 3:2, 4:5, 3:4, 2:3*

## Proporcje - kiedy które

| Proporcja | Użycie |
|-----------|--------|
| `1:1` | Instagram post, avatar |
| `16:9` | YouTube thumbnail, banner, X post |
| `9:16` | Instagram/TikTok story, reel |
| `4:3` | Prezentacja |

## Domyślna lokalizacja

Zapisuj do `Marketing/media/` z opisową nazwą:
- `Marketing/media/post-automatyzacja-2026-01-23.png`
- `Marketing/media/infografika-korzysci-ai.png`

## Jak działa upload reference images

Dla trybów `edit`, `compose`, `remove-bg` Kie.ai wymaga publicznego URL-a dla inputowych obrazków. Skrypt uploaduje plik do **ImgBB** (TTL 1h, auto-delete), dostaje publiczny URL i przekazuje go do API. Limit: **32 MB** na plik. Retry 3× z exponential backoff przy błędach 5xx/sieci.

## Obsługa błędów

**Kie.ai:**

| Kod | Znaczenie |
|-----|-----------|
| 401 | Sprawdź `KIE_API_KEY` |
| 402 | Brak środków na koncie Kie.ai |
| 429 | Rate limit — poczekaj |

**ImgBB:**

| Sytuacja | Rozwiązanie |
|----------|-------------|
| `IMGBB_API_KEY not configured` | Dodaj klucz do `.env` (imgbb.com/api) |
| `File too large: X MB (limit 32 MB)` | Skompresuj lub zmniejsz rozdzielczość przed uploadem |
| `ImgBB upload failed after 3 attempts` | Problem sieci/API ImgBB — spróbuj ponownie za chwilę |

---

## Referencje

- Zasady tworzenia promptów: [prompting-guide.md](prompting-guide.md)
- Brand rules Akademii Automatyzacji: [brand-rules.md](brand-rules.md)
