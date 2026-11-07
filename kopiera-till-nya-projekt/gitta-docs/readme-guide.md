# README: projektets förstasida

En **README** är filen `README.md` i projektets rotmapp. GitHub visar den
som förstasida när någon öppnar projektet. Filen är skriven i *Markdown*, ett
enkelt sätt att formatera text.

## Skapa en README

Gitta skapar en minimal `README.md` (bara projektets namn och beskrivning)
när du skapar ett nytt projekt. Bygg ut den så här:

1. Öppna `README.md` i projektmappen (Gitta: **Visa mappen**) med Anteckningar
   eller en kodeditor.
2. Skriv enligt mallen nedan.
3. Öppna Gitta, välj projektet, skriv en commit-beskrivning, till exempel
   `Uppdatera README med installationsinstruktioner`, och tryck
   **commit and push**.
4. Öppna projektet på GitHub (**Öppna på GitHub**) och kontrollera sidan.

## Mall

```markdown
# Projektnamn

En eller två meningar om vad projektet är och vem det är till för.

## Installation

1. Ladda ner ...
2. Kör ...

## Användning

Så här startar du programmet och gör de vanligaste sakerna.

## Beroenden

- Python 3.11 eller nyare
- ...

## Licens

Skriv vilken licens som gäller, eller "Alla rättigheter förbehållna".
```

## Markdown på 30 sekunder

| Du skriver | Du får |
|---|---|
| `# Rubrik` | Stor rubrik (`##` mindre, `###` ännu mindre) |
| `**fet**` | **fet** |
| `*kursiv*` | *kursiv* |
| `- punkt` | punktlista |
| `1. steg` | numrerad lista |
| `` `kod` `` | kod i text |
| ```` ``` ```` före och efter ett block | kodblock |
| `[text](https://adress)` | länk |
| `![bild](bild.png)` | bild från projektmappen |

## Uppdatera README

Uppdatera README när du:

- lägger till en funktion eller ändrar hur man använder projektet,
- ändrar installationsstegen eller vilka program som krävs,
- upptäcker att något i den är fel eller gammalt.

Tumregel: **ändrar du hur andra installerar eller använder projektet, ändra
README i samma commit.** Då hänger beskrivning och kod ihop i historiken.

## Redigera direkt på GitHub (alternativ)

Det går också att trycka på pennan på `README.md` på github.com och spara där.
Gör du det: kör **pull** i Gitta innan du jobbar vidare på datorn, annars
får du ett felmeddelande vid nästa push.
