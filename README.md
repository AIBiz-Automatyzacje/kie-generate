# kie-generate

Skill dla Claude Code do generowania grafik i wideo AI przez [Kie.ai](https://kie.ai).

- **Grafiki** (Nano Banana 2 / Nano Banana Pro / GPT Image-2) — generowanie od zera, edycja, kompozycja, usuwanie tła
- **Wideo** (Kling 3.0 / Seedance 2.0 / Seedance 2.5 / MiniMax H3) — text-to-video, image-to-video z klatką początkową i końcową, seamless loopy

## Instalacja

Skopiuj folder `skills/kie-generate/` do katalogu `.claude/skills/` w swoim workspace:

```bash
cp -r skills/kie-generate ~/.claude/skills/
# lub do projektu:
cp -r skills/kie-generate .claude/skills/
```

## Konfiguracja

W Claude Code odpal:

```
skonfiguruj kie-generate
```

Claude przeprowadzi Cię przez onboarding — sprawdzi Pythona, zainstaluje zależności, poprosi o klucze API i zapyta o Twój brand.

### Klucze API (potrzebne podczas onboardingu)

- **Kie.ai** → [kie.ai](https://kie.ai) → Dashboard → API Keys. Doładuj konto (~$5, obrazek ≈ $0.01–0.04). Wideo jest dużo droższe — klip 5 s w jakości standard ≈ 135 kredytów
- **ImgBB** → [imgbb.com](https://imgbb.com) + [api.imgbb.com](https://api.imgbb.com) → darmowy, bez karty. Potrzebny do trybów `edit` / `compose` / `remove-bg`. Wideo go NIE wymaga (obrazy wejściowe idą przez magazyn kie.ai)

Klucze zapisują się w `.env` w root Twojego workspace'u.

## Użycie

Po konfiguracji — po prostu mów do Claude'a:

```
wygeneruj grafikę z napisem "Hello World" na ciemnym tle, format 16:9
```

```
usuń tło z tego obrazka
```

```
ożyw tę grafikę — 5 sekund, delikatny ruch, zapętlone
```

Pełna dokumentacja trybów i parametrów: [skills/kie-generate/SKILL.md](skills/kie-generate/SKILL.md)
Zasady promptowania: [skills/kie-generate/prompting-guide.md](skills/kie-generate/prompting-guide.md)

## Struktura

```
skills/kie-generate/
├── SKILL.md           # manifest skilla (czyta Claude)
├── ONBOARDING.md      # kroki konfiguracji (prowadzi Claude)
├── prompting-guide.md # zasady tworzenia promptów
├── brand-rules.md     # przykład — nadpisywany w onboardingu
└── scripts/
    ├── env_loader.py  # loader .env
    ├── kie_image.py   # CLI do grafik
    └── kie_video.py   # CLI do wideo
```

## Wymagania

- Python 3.8+
- `requests` (onboarding zainstaluje)
- `ffmpeg` — opcjonalnie, tylko przy wideo (konwersja klatek zapisanych jako WebP z rozszerzeniem `.png`)
- Claude Code
