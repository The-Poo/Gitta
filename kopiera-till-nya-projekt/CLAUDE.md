# Git och commit-rutin (Gitta)

Användaren är nybörjare på git och använder programmet Gitta för att
committa och pusha. Hjälp till så här:

- **Commit-fil:** Efter varje avslutad ändring (ny funktion, buggfix,
  refaktorering, ändrad dokumentation) skriv eller uppdatera
  `.Gitta-commit` i projektets rot. Fråga inte användaren om
  commit-meddelandet. Skriv om filen helt så den bara beskriver det som är
  osparat just nu, inte staplat från tidigare omgångar. Format: en kort titelrad utan formatering (under 60 tecken), tom rad, sedan en formaterad text i Markdown:
  `**Vad:**`/`**Varför:**` som fet text och punkter med `- `, gärna med ett **fet** nyckelord först i varje punkt. Gitta visar
  formateringen i en förhandsvisning. Skriv på svenska om inget annat sägs.
  Detaljer: `gitta-docs/commit-filer.md`.
- **Påminn om att spara:** När ett naturligt delsteg är klart, eller när
  användaren verkar vara på väg att avsluta, säg tydligt: "Det här är ett
  bra läge att öppna Gitta och trycka commit and push. Beskrivningen ligger
  redan i commit-filen."
- **Kolla att det är committat:** Innan du avslutar en arbetsomgång, kör
  `git status --short`. Finns osparade ändringar, påminn användaren om att
  committa. Kör aldrig `git commit` eller `git push` själv om användaren
  inte uttryckligen ber om det.
- **README:** Finns ingen `README.md`, föreslå att skapa en enligt
  `gitta-docs/readme-guide.md`. Ändras installation, användning eller
  beroenden, uppdatera README i samma omgång och nämn det i commit-filen.
- **Känslig information (viktigt):** Projektet kan bli publikt på GitHub, och
  det som väl är pushat går inte att ta tillbaka på riktigt. Detaljer och
  `.gitignore`-mall: `gitta-docs/kanslig-information.md`.
  - Skriv aldrig lösenord, API-nycklar, tokens, privata nycklar eller
    personuppgifter i filer som ska committas. Använd en `.env`-fil (eller
    miljövariabler) som läses av koden, och lägg `.env` i `.gitignore`
    *innan* den skapas.
  - Finns ingen `.gitignore`, skapa en enligt mallen i guiden.
  - **Innan du skriver `.Gitta-commit`:** titta på de ändrade filerna
    (`git status --short`) och sök efter nycklar och lösenord. Hittar du
    något, eller en fil som `.env`, `*.pem`, `*.key`, `*secret*`,
    `*password*`, `*credential*`, **varna användaren tydligt, med filnamnet,
    och be dem inte committa den.** Skriv inte `.Gitta-commit` som om allt
    vore i ordning.
  - Är projektet public, eller kommer det bli det, påminn om att även
    gammal historik är synlig.
  - Har en hemlighet redan pushats: säg att den ska anses läckt, att nyckeln
    måste bytas hos tjänsten den hör till, och att det inte räcker att radera
    filen.
- **Förklara enkelt:** Använd git-termerna (commit, push, pull) men förklara
  dem med en halv mening första gången de dyker upp i en session.
  Ordlista: `gitta-docs/ordlista.md`.
