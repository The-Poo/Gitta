# Installation

Du behöver två saker: **Git** och **Gitta**. Båda är gratis.

## 1. Git

Git är motorn som sparar historiken. Gitta är bara ett vackert skal runt den.

Gitta kollar själv om Git finns när du startar den. Saknas det erbjuder
Gitta att installera det åt dig. Vill du göra det själv:

1. Öppna <https://git-scm.com/download/win>.
2. Ladda ner och kör installationsprogrammet. Alla standardval är bra, du kan
   trycka "Next" hela vägen.
3. Starta om Gitta.

Alternativ: öppna PowerShell och skriv `winget install --id Git.Git -e`.

Kontrollera: öppna PowerShell och skriv `git --version`. Du ska få något i stil
med `git version 2.47.0.windows.1`. Versionen ska vara 2.25 eller nyare.

## 2. Gitta

1. Lägg `Gitta.exe` var du vill, till exempel på skrivbordet.
2. Dubbelklicka. Windows kan varna ("Windows skyddade din dator") eftersom
   programmet inte är signerat. Tryck **Mer information** och sedan
   **Kör ändå**.

## 3. Första starten

1. Tryck **Koppla GitHub-konto**.
2. Gitta visar en kod, kopierar den och öppnar GitHub i webbläsaren.
3. Klistra in koden (Ctrl+V), logga in om det behövs och tryck **Authorize**.
4. Gitta går vidare av sig själv och visar alla dina projekt.

Har du inget GitHub-konto? Skapa ett gratis på <https://github.com/signup>
först.

## Om något krånglar

| Problem | Lösning |
|---|---|
| "Git saknas" | Installera Git (se ovan) och starta om Gitta |
| "Client ID saknas" | Programmet är inte färdigkonfigurerat, se [02-skapa-oauth-app.md](02-skapa-oauth-app.md) |
| Koden fungerar inte | Starta inloggningen igen, koden gäller bara en kort stund |
| "GitHub avvisade inloggningen" | Arkiv > Logga ut och koppla kontot igen |
