# För dig som delar ut eller bygger Gitta

## Teknik

Python 3 med Tkinter och enbart standardbiblioteket (inga beroenden).
Gitta anropar riktiga `git` och GitHubs REST-API. Inloggning sker med OAuth
device flow. Paketeras till en enda `Gitta.exe` med PyInstaller.

```
gitta/
  app.py         fönster och knappar (Tkinter)
  gitops.py      anrop till git på kommandoraden
  github.py      GitHubs API och inloggning
  commitfile.py  commit-filen .Gitta-commit
  leakcheck.py   varnar för nycklar och lösenord innan upload
  config.py      inställningar i %APPDATA%\Gitta\config.json
  texts.py       hjälptexter
  defaults.py    inbyggt Client ID
```

## Första gången

1. Skapa en OAuth App: [02-skapa-oauth-app.md](02-skapa-oauth-app.md).
2. Skriv in Client ID i `gitta/defaults.py`. Det är inte hemligt, så det är
   okej att committa det till ett publikt repo.
3. Provkör: `python run_gitta.py`

## Lägg upp på GitHub

Du kan använda Gitta själv: **Nytt projekt**, välj mappen `gitta`, avmarkera
"Skapa en ny mapp", och kryssa i **public** så att din vän kan ladda ner.

Eller med git i terminalen, från mappen `gitta`:

```
git init -b main
git add -A
git commit -m "Första versionen av Gitta"
gh repo create gitta --public --source . --push
```

## Bygg och dela ut exe-filen

1. `.\build.ps1` ger `dist\Gitta.exe` (mappen `dist` följer inte med i repot).
2. Skapa en release på GitHub och bifoga filen:
   `gh release create v0.1.0 dist\Gitta.exe --title "Gitta 0.1.0" --notes "Första versionen"`
   Eller via webben: repot > **Releases** > **Draft a new release** > dra in `Gitta.exe`.
3. Din vän laddar ner `Gitta.exe` från Releases.

Bygger du om med ändringar: höj `__version__` i `gitta/__init__.py` och gör
en ny release.
