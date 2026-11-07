# CLAUDE.md - Gitta

Gitta är ett fristående grafiskt Git/GitHub-program för Windows (Python,
Tkinter, endast standardbiblioteket). Se `README.md` och `docs/00-for-utvecklare.md`.

## Konventioner

- Kod, kommentarer, docstrings och loggar på engelska. Användartexter i
  programmet och all Markdown-dokumentation på svenska. Git-termer
  (commit, push, pull, clone, branch ...) översätts aldrig.
- Inga externa beroenden. Allt ska fungera med bara Python-standardbiblioteket.
- Ändrar du en av guiderna `docs/03-readme-guide.md`, `docs/04-commit-filer.md`
  eller `docs/05-ordlista.md`, ändra också kopian i
  `kopiera-till-nya-projekt/gitta-docs/`.

## Commit-rutin (Gitta)

- **Efter varje ändring i kodbasen** (nya filer, buggfixar, refaktorering,
  dokumentation) skriv eller uppdatera `.Gitta-commit` i projektets rot, innan
  du avslutar svaret. Skriv om filen helt så den bara beskriver det som är
  osparat just nu. Format: kort titelrad (under 60 tecken), tom rad, sedan
  några punkter om vad och varför, på svenska.
- Gäller även små ändringar och felsökningspass med många Edit-anrop. Tumregel:
  skulle `git status` visa något, uppdatera filen.
- Påminn användaren om att öppna Gitta och trycka commit and push när ett
  delsteg är klart. Kör aldrig `git commit` eller `git push` själv om
  användaren inte ber om det.
- Innan du skriver commit-filen: kolla ändrade filer efter nycklar, tokens,
  lösenord och `.env`. Hittar du något, varna tydligt med filnamn.
- Användaren testar själv i sin egen terminal. Bygg inga egna test- eller
  sandlådemiljöer. Syntaxkontroll och körning av rena funktioner är okej.
