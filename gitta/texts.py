"""User-facing help texts (Swedish; git terms stay in English)."""

LOGIN_INTRO = (
    "Gitta hjälper dig att spara och dela dina projekt på GitHub utan att "
    "behöva kommandoraden.\n\n"
    "Tryck på knappen nedan. Gitta visar en kod som du skriver in på GitHubs "
    "hemsida. Då kopplas ditt konto till programmet. Ditt lösenord lämnas "
    "aldrig till Gitta."
)

OAUTH_GUIDE = """\
ENGÅNGSINSTÄLLNING: skapa en OAuth App på GitHub
(görs en gång av den som delar ut Gitta, inte av varje användare)

1. Logga in på github.com. Klicka på din profilbild uppe till höger >
   Settings (dina personliga inställningar, inte ett projekts).
2. I menyn till vänster, längst ned: Developer settings > OAuth Apps.
   Genväg: github.com/settings/developers
3. Tryck "New OAuth App" (eller "Register a new application") och fyll i:
     Application name:           Gitta
     Homepage URL:               https://github.com
     Redirect URIs:              http://localhost
     Allow wildcard matching:    låt vara tom
     Enable Device Flow:         kryssa i
     Expire user access tokens:  ta bort kryssen om rutan finns
4. Tryck "Register application".
5. Kopiera "Client ID". Client ID är inte hemligt. Skapa ingen
   Client secret.
6. Klistra in det i rutan här intill, eller skriv in det i
   gitta/defaults.py innan du bygger .exe-filen.
"""

HELP_START = """\
KOM IGÅNG

Gitta har tre huvudsakliga knappar för dina projekt:

  pull               Hämtar nyheter från GitHub till din dator.
  commit and push    Sparar dina ändringar: en commit är ett sparat steg
                     med en beskrivning, push skickar det till GitHub.
  clone              Hämtar ett projekt från GitHub till din dator första
                     gången. "clone - hämta flera projekt" hämtar många på
                     en gång till en rotmapp, bra på en ny dator.

README            Fliken README i projektvyn visar projektets förstasida från
                    GitHub, även innan du hämtat projektet.

Rutiner som fungerar bra:
  1. Börja arbetet med pull.
  2. Arbeta som vanligt i dina filer.
  3. När du kommit en bit: skriv en kort beskrivning av vad du gjort och
     tryck "commit and push".
"""

HELP_COMMIT = """\
COMMIT-FILEN (.Gitta-commit)

Varje projekt kan ha en fil som heter .Gitta-commit i projektmappen. Där
ligger beskrivningen av dina ändringar. Verktyg som Claude Code kan skriva
dit åt dig medan de arbetar. Gitta visar innehållet när du väljer projektet,
och du kan ändra texten innan du sparar.

När du trycker "commit and push" används texten som commit-meddelande, och
filen tas bort automatiskt efter att det lyckats.

Bra meddelande: en kort rad om vad som ändrats, gärna följd av en tom rad
och några punkter.
"""

HELP_GLOSSARY = """\
ORDLISTA

repository (repo)   Ett projekt med full historik. Bor både på din dator
                    och på GitHub.
commit              Ett sparat steg i historiken, med en beskrivning.
push                Skickar dina commits till GitHub.
pull                Hämtar andras (eller dina egna från en annan dator)
                    commits från GitHub.
clone               Gör en kopia av ett GitHub-projekt på din dator.
branch              En gren av projektet. Gitta arbetar på huvudgrenen
                    (oftast "main").
private / public    Private: bara du (och de du bjuder in) ser projektet.
                    Public: alla på internet kan se det.
README              Projektets förstasida på GitHub (README.md).
"""

PRIVATE_EXPLAIN = (
    "Private (standard): bara du och de du bjuder in kan se projektet.\n"
    "Public: vem som helst på internet kan se projektet och dess kod. "
    "Lägg aldrig lösenord eller nycklar i ett public projekt."
)

PULL_EXPLAIN = "Hämtar nyheter från GitHub till din dator."
CLONE_EXPLAIN = "Hämtar projektet från GitHub till en mapp på din dator."
LINK_EXPLAIN = "Har du redan projektet på datorn? Peka ut mappen så kopplas den ihop."
COMMIT_EXPLAIN = (
    "En commit sparar ett steg i historiken med din beskrivning. Push "
    "skickar det vidare till GitHub. Gitta gör båda i ett svep."
)

EXISTING_FILES_WARNING = (
    "Om mappen redan innehåller filer läggs alla med i första commit. "
    "Gitta kontrollerar filerna efter nycklar och lösenord innan något "
    "skickas, men kolla själv också - särskilt om du gör projektet public."
)

CLONE_MANY_EXPLAIN = (
    "Hämtar flera projekt från GitHub till din dator på en gång, till exempel "
    "när du sitter vid en ny dator. Gitta kopplar ihop varje mapp med rätt "
    "projekt så att de dyker upp som 'på datorn' i listan."
)
