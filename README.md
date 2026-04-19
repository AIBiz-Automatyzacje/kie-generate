# kie-generate

Skill dla Claude Code do generowania grafik AI przez [Kie.ai](https://kie.ai) (Nano Banana 2 / Nano Banana Pro). Obsługuje generowanie od zera, edycję, kompozycję i usuwanie tła.

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

- **Kie.ai** → [kie.ai](https://kie.ai) → Dashboard → API Keys. Doładuj konto (~$5, obrazek ≈ $0.01–0.04)
- **ImgBB** → [imgbb.com](https://imgbb.com) + [api.imgbb.com](https://api.imgbb.com) → darmowy, bez karty. Potrzebny do trybów `edit` / `compose` / `remove-bg`

Klucze zapisują się w `.env` w root Twojego workspace'u.

## Użycie

Po konfiguracji — po prostu mów do Claude'a:

```
wygeneruj grafikę z napisem "Hello World" na ciemnym tle, format 16:9
```

```
usuń tło z tego obrazka
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
    ├── env_loader.py  # shared loader .env
    └── kie_image.py   # CLI do API Kie.ai
```

## Wymagania

- Python 3.8+
- `requests` (onboarding zainstaluje)
- Claude Code
