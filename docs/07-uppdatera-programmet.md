# Uppdatera Gitta utan att känslig information hamnar på GitHub

Både du och din vän kan ändra och förbättra Gitta i framtiden. Den här guiden
visar hur ni gör det säkert.

## Vad är känsligt, och var ligger det?

| Vad | Var det ligger | Hamnar på GitHub? |
|---|---|---|
| Din inloggning (access-token) | `%APPDATA%\Gitta\config.json`, alltså **utanför** projektmappen | Nej, aldrig |
| Dina projektmappar och inställningar | Samma fil | Nej |
| Client ID | `gitta/defaults.py` i projektet | Ja, och det är okej. Det är offentligt och ger ingen åtkomst till något. |
| Client **secret** | Ska inte finnas. Gitta behöver ingen. | – |
| Lösenord, nycklar, `.env`-filer | Om du lägger dem i projektmappen | **Ja, om du inte ser upp.** |

Tryck `Win + R`, skriv `%APPDATA%\Gitta` och Enter om du vill se
inställningsmappen. Den är fristående från projektet och följer inte med när
du committar.

> **Har du ändå råkat skicka en nyckel eller ett lösenord till GitHub?**
> Radera inte bara filen. Historiken sparar den. Ta bort åtkomsten hos
> tjänsten som nyckeln hör till och skapa en ny nyckel. För Gitta: gå till
> <https://github.com/settings/applications>, ta bort Gitta under
> *Authorized OAuth Apps* och logga in på nytt.

## Skydd som redan finns

- **`.gitignore`** i projektet håller bland annat `.env`, `*.pem`, `*.key`,
  `*.token`, `config.json`, `dist/` och `build/` borta från GitHub.
- **Gitta kontrollerar filerna** innan något skickas till GitHub, på tre ställen:
  innan **commit and push**, och när du skapar ett **Nytt projekt** eller
  **lägger till en befintlig mapp**. Den tittar både på filnamn (`.env`,
  `*.pem`, namn med `secret` eller `password`) och på *innehållet*:
  GitHub-tokens, AWS- och API-nycklar, privata nycklar och rader som
  `password = "..."`. Hittar den något visas filnamn och radnummer (aldrig själva
  hemligheten) och du får välja. Svara **Nej** om du är osäker. Är projektet
  public står det tydligt i varningen.
  Kontrollen är ett skyddsnät, inte en garanti: den hittar inte allt, och den
  tittar bara på filerna som ligger i mappen nu, inte på gammal historik i en
  befintlig git-mapp. Filer som står i `.gitignore` hoppas över.
- **Commit-filen** `.Gitta-commit` hålls utanför historiken.

## Så uppdaterar ni programmet

1. **Hämta senaste versionen.** Välj `gitta` i Gitta och tryck **pull**. Har ni
   inte projektet på datorn än, tryck **clone**.
2. **Ändra koden** i mappen (knappen **Visa mappen**). Provkör med
   `python run_gitta.py` (eller dubbelklicka `Starta-Gitta.bat`).
3. **Titta efter innan ni sparar.** Gitta listar ändrade filer under
   projektet. Känner du inte igen en fil, eller är det en inställningsfil,
   nyckel eller lösenord: spara inte den.
4. **Beskriv ändringen** i commit-rutan och tryck **commit and push**.
5. **Bygg ny exe** (bara om ni delar ut en ny version):
   `.\build.ps1`, höj `__version__` i `gitta/__init__.py` och skapa en ny
   release (se [00-for-utvecklare.md](00-for-utvecklare.md)). `Gitta.exe`
   committas inte till historiken, den bifogas bara på Releases.

## Jobbar ni två på samma projekt?

- Börja alltid med **pull**, och avsluta med **commit and push**.
- Ändrar ni samma rader samtidigt kan Gitta inte slå ihop dem och visar ett
  felmeddelande. Då väntar den som fick felet och ber den andre pusha först,
  eller ber någon som kan git om hjälp.
- Din vän behöver skrivrättigheter. Lägg till hen under repot på GitHub:
  **Settings > Collaborators > Add people**.

## Checklista innan du trycker commit and push

- [ ] Inga lösenord, nycklar eller `.env`-filer bland de ändrade filerna.
- [ ] Inga filer från min egen dator som inte hör till programmet.
- [ ] Beskrivningen säger vad jag ändrat.
