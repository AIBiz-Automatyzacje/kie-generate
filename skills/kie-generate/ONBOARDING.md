# Onboarding — kie-generate

Instrukcja dla Claude'a: jak przeprowadzić nowego użytkownika przez konfigurację skilla `kie-generate` na jego systemie (Mac/Windows/Linux).

**Wywołanie:** user mówi "skonfiguruj kie-generate" / "onboarding kie-generate" / "uruchom kie-generate setup" / "zrób mi setup kie-generate".

## Zasady działania

1. **Idempotentność** — za każdym uruchomieniem sprawdzaj stan na żywo. Jak krok już zrobiony → ✅ skip i komunikat "już skonfigurowane". Nic nie pamiętamy między sesjami.
2. **Bez realnych call testowych** — nie palimy kasy usera na weryfikację kluczy. Pytamy "dodałeś?" i sprawdzamy tylko że klucz jest w `.env`.
3. **Skip zamiast nadpisywać** — jeśli user ma już skonfigurowany brand / lokalizację outputu, nie dotykamy.
4. **Komunikacja krótka, konkretna** — każdy krok: co sprawdzam → wynik → co dalej. Bez wstępów.

## Kroki

### 1. Python 3

**Check:**
```bash
python3 --version
```

- Jeśli wersja ≥ 3.8 → ✅ "Python OK: {wersja}"
- Jeśli brak `python3` lub starsza → poinformuj usera:
  - **Mac:** `brew install python3`
  - **Windows:** pobierz z python.org, zaznacz "Add to PATH" przy instalacji
  - **Linux:** `sudo apt install python3` (Debian/Ubuntu) lub odpowiednik
- Po instalacji user musi **restartnąć terminal**, potem re-run onboardingu

### 2. Biblioteka `requests`

**Check:**
```bash
python3 -c "import requests; print(requests.__version__)"
```

- Jeśli działa → ✅ "requests OK: {wersja}"
- Jeśli `ModuleNotFoundError` → zapytaj usera: "Zainstalować `requests`? [tak/nie]"
  - Jeśli tak → `pip3 install requests` (lub `pip install requests` jeśli pip3 nie istnieje)
  - Jeśli nie → stop, poinformuj że skill nie zadziała bez tej biblioteki

### 3. Plik `.env` w workspace

**Check:**
```bash
test -f .env && echo "EXISTS" || echo "MISSING"
```

- Jeśli istnieje → ✅ "Plik .env znaleziony"
- Jeśli nie istnieje → utwórz pusty `.env` w root workspace'u (tam gdzie `.obsidian/` lub gdzie user pracuje), poinformuj: "Utworzyłem pusty .env w {ścieżka}"

### 4. `KIE_API_KEY`

**Check:**
```bash
grep -q "^KIE_API_KEY=" .env && echo "SET" || echo "MISSING"
```

- Jeśli SET → ✅ "KIE_API_KEY w .env — skip"
- Jeśli MISSING → **wyświetl userowi:**

```
Aby zdobyć klucz Kie.ai:

1. Wejdź na https://kie.ai → Sign up (email + hasło)
2. Dashboard → API Keys → Create API Key
3. Doładuj konto minimum ~$5 (Nano Banana 2 ≈ $0.01-0.04 za obrazek)
4. Skopiuj klucz i dodaj do .env:

   KIE_API_KEY=sk-xxxxxxxxxxxx

Dodałeś klucz do .env? [tak/nie]
```

- Po odpowiedzi "tak" → re-check gotowości (`grep` raz jeszcze)
  - Jeśli klucz jest → ✅ przejdź dalej
  - Jeśli nadal brak → "Nie widzę klucza. Sprawdź czy zapisałeś .env i czy nazwa to dokładnie `KIE_API_KEY=`"
- "nie" → zatrzymaj onboarding, poinformuj że user może dokończyć później re-runem

### 5. `IMGBB_API_KEY`

**Check:**
```bash
grep -q "^IMGBB_API_KEY=" .env && echo "SET" || echo "MISSING"
```

- Jeśli SET → ✅ "IMGBB_API_KEY w .env — skip"
- Jeśli MISSING → **wyświetl userowi:**

```
ImgBB to darmowy hosting do referencyjnych obrazków (dla edit/compose/remove-bg).
Bez karty, bez konfiguracji, 2 minuty setupu.

1. Wejdź na https://imgbb.com → Sign up (email + hasło)
2. Wejdź na https://api.imgbb.com → "Get API key" (przycisk pod opisem)
3. Skopiuj klucz i dodaj do .env:

   IMGBB_API_KEY=xxxxxxxxxxxx

Dodałeś klucz do .env? [tak/nie]
```

- Re-check po "tak" (analogicznie do kroku 4)

### 6. Brand rules

**Check:**
```bash
test -f .claude/skills/kie-generate/brand-rules.md && head -1 .claude/skills/kie-generate/brand-rules.md
```

- Jeśli plik istnieje i pierwsza linia zawiera "Akademia Automatyzacji" → plik ma domyślny brand AA
- Zapytaj usera:

```
Widzę że masz brand-rules.md z konfiguracją "Akademia Automatyzacji".
Chcesz skonfigurować własny brand? [tak/nie/pokaż obecny]

- tak   → przeprowadzę dialog i wygeneruję twój brand-rules.md
- nie   → zostawiamy obecny, możesz zawsze edytować ręcznie
- pokaż → wyświetlę obecny brand-rules.md żebyś zobaczył
```

- Jeśli user wybierze "tak" — przeprowadź **dialog brandowy** (pytaj po jednym, nie wszystkie na raz):

  **Pytanie 1 — Nazwa marki / projekt:**
  > "Jak nazywa się Twoja marka / projekt? (np. 'Moja Firma', 'Studio Kowalski')"

  **Pytanie 2 — Kolory:**
  > "Jakie kolory są kluczowe dla Twojego brandu? Podaj 1-3 kolory (nazwy lub hex, np. 'głęboki zielony #2D5016 + kremowy')."

  **Pytanie 3 — Styl wizualny:**
  > "Jaki styl wizualny Ci pasuje? Kilka słów wystarczy:
  > - minimalistyczny / bogaty-detale
  > - nowoczesny / retro / vintage
  > - korporacyjny / luzowy / premium / energetyczny
  > - inne określenia które pasują"

  **Pytanie 4 — Zastosowanie:**
  > "Do czego głównie używasz grafik? (posty FB/IG, thumbnaile YT, prezentacje, strona www, reklamy, inne)"

  **Pytanie 5 — Logo (opcjonalne):**
  > "Masz logo w formie publicznego URL-a (Google Drive / dropbox / imgur)? Jeśli tak — wklej link. Jeśli nie — pomijamy."

  **Pytanie 6 — Czego unikać (opcjonalne):**
  > "Jest coś czego wizualnie nie lubisz / co byłoby off-brand? (np. 'żadnego AI-cyberpunku', 'bez pastelowych różów', 'bez gradientów')"

- Po zebraniu odpowiedzi:
  1. Wygeneruj `brand-rules.md` w strukturze zbliżonej do obecnego pliku AA (sekcje: Kolory, Typografia, Styl wizualny, Logo, Czego unikać)
  2. **Pokaż userowi draft przed zapisem** — "Oto twój brand-rules.md. Zapisać czy coś poprawić?"
  3. Po akceptacji → nadpisz `.claude/skills/kie-generate/brand-rules.md`

- Jeśli user wybierze "nie" / "pokaż" → odpowiednio zostaw lub wyświetl `brand-rules.md`

### 7. Lokalizacja outputu

**Check:** przeczytaj `SKILL.md`, znajdź linię z domyślną lokalizacją (sekcja "Domyślna lokalizacja", obecnie `Marketing/media/`).

- Zapytaj usera:

```
Domyślnie grafiki zapisują się do: Marketing/media/
Ta ścieżka Ci pasuje? [tak/inna]

Jeśli inna — podaj ścieżkę względną od root workspace'u (np. 'media/', 'assets/ai/', 'grafiki/wygenerowane/')
```

- Jeśli "tak" → ✅ skip
- Jeśli podał inną ścieżkę:
  1. Edytuj `SKILL.md` — znajdź sekcję "Domyślna lokalizacja" i podmień ścieżkę
  2. Utwórz folder jeśli nie istnieje: `mkdir -p {nowa_ścieżka}`
  3. Potwierdź: "Zmieniłem domyślną lokalizację na {nowa_ścieżka}"

### 8. Podsumowanie

Wyświetl userowi finalny status:

```
✅ kie-generate — setup ukończony

Co masz skonfigurowane:
- Python {wersja} + requests {wersja}
- Plik .env z kluczami KIE_API_KEY i IMGBB_API_KEY
- Brand: {nazwa_brandu lub "domyślny AA"}
- Domyślny output: {ścieżka}

Pierwszy test — powiedz po prostu:
"wygeneruj grafikę z napisem 'Hello World' na ciemnym tle"

Jeśli coś nie zadziała przy pierwszym użyciu:
- 401 → sprawdź KIE_API_KEY (typo, spacja, cudzysłów w .env)
- 402 → doładuj konto Kie.ai
- IMGBB error → sprawdź IMGBB_API_KEY
```

## Obsługa błędów podczas onboardingu

- **Brak uprawnień do pip install** → poinformuj o `pip install --user requests` albo `pip install requests --break-system-packages` (na niektórych Linuxach)
- **User w innej lokalizacji niż workspace** — sprawdź `pwd` na początku, jeśli brak `.obsidian/` lub `.env` → poproś o `cd` do katalogu workspace'u i re-run
- **User podaje klucz w złym formacie** (np. z cudzysłowami, spacjami) — pokaż przykład prawidłowego formatu `.env`: `KLUCZ=wartość` bez spacji przed `=`, bez cudzysłowów (chyba że wartość ma spacje)

## Czego NIE robić

- ❌ Nie instaluj nic bez pytania usera (`pip install`, `brew install`)
- ❌ Nie robisz realnego calla do Kie.ai ani ImgBB żeby zweryfikować klucze (user sam zobaczy przy pierwszym użyciu)
- ❌ Nie nadpisuj istniejącego `brand-rules.md` jeśli user nie wybrał "tak"
- ❌ Nie wypisuj kluczy API na ekran (nawet częściowo) — bezpieczeństwo
- ❌ Nie edytuj `kie_image.py` ani `env_loader.py` — to nie jest część onboardingu
