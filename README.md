# Gitta

Ett grafiskt program för Windows som låter dig använda GitHub utan
kommandoraden:

- se alla dina projekt på ett ställe,
- hämta nyheter (**pull**),
- spara och skicka dina ändringar (**commit and push**),
- skapa nya projekt, både på datorn och på GitHub.

Git-termerna är kvar på engelska med en svensk förklaring vid varje knapp,
så att du lär dig dem medan du använder programmet.

## Installation

Du behöver ett **GitHub-konto** (gratis: <https://github.com/signup>) och
**Git** på datorn. Gitta hjälper dig installera Git om det saknas.

### Alternativ A: ladda ner färdigt program (enklast)

1. Gå till **Releases** (i högerkanten på den här sidan) och ladda ner
   **`Gitta.exe`**.
2. Lägg filen var du vill, till exempel på skrivbordet, och dubbelklicka.
3. Windows kan varna ("Windows skyddade din dator") eftersom programmet inte
   är signerat. Tryck **Mer information** och sedan **Kör ändå**.
4. Saknas Git frågar Gitta om det ska installeras åt dig. Svara **Ja**, vänta
   tills det svarta fönstret är klart och starta Gitta igen.
5. Tryck **Koppla GitHub-konto**, skriv in koden som visas på GitHubs sida och
   tryck **Authorize**. Klart!

### Alternativ B: köra från källkoden

1. Installera Python 3.11 eller nyare från <https://www.python.org/downloads/>
   (kryssa i **Add python.exe to PATH** i installationsprogrammet).
2. Tryck på den gröna knappen **Code > Download ZIP** på den här sidan och
   packa upp mappen.
3. Dubbelklicka på **`Starta-Gitta.bat`**.

Inget mer behöver installeras, Gitta använder bara det som följer med Python.

## Kom igång

Se mappen [docs](docs/) för guider på svenska:

| Fil | Innehåll |
|---|---|
| [01-installation.md](docs/01-installation.md) | Mer detaljer om installationen och felsökning |
| [03-readme-guide.md](docs/03-readme-guide.md) | Skapa och uppdatera en README på GitHub |
| [04-commit-filer.md](docs/04-commit-filer.md) | Commit-filer och när man ska committa |
| [05-ordlista.md](docs/05-ordlista.md) | Git-termer förklarade |
| [06-instruktioner-for-ai.md](docs/06-instruktioner-for-ai.md) | Text att klistra in för Claude Code och liknande |
| [07-uppdatera-programmet.md](docs/07-uppdatera-programmet.md) | Uppdatera Gitta utan att känslig information läggs upp |

Programmet har också en **Hjälp**-meny.

Vill du att Claude Code ska skriva commit-filer och påminna dig i dina egna
projekt? Kopiera mappen [kopiera-till-nya-projekt](kopiera-till-nya-projekt/)
till projektet, se [LÄS-MIG](kopiera-till-nya-projekt/LÄS-MIG.md).

## För dig som delar ut eller bygger programmet

Se [docs/00-for-utvecklare.md](docs/00-for-utvecklare.md) och
[docs/02-skapa-oauth-app.md](docs/02-skapa-oauth-app.md).

## Kända begränsningar

- Access-token ligger i klartext i `%APPDATA%\Gitta\config.json`.
- Pull är bara fast-forward. Går historiken isär visar Gitta ett felmeddelande
  i stället för att slå ihop ändringarna.
- Om skapandet av ett nytt projekt avbryts efter att repot skapats på GitHub
  får man ta bort det repot på github.com innan man försöker igen.
