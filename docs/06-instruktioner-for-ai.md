# Instruktioner till AI-verktyg (Claude Code m.fl.)

Använder du ett AI-verktyg som Claude Code för att programmera? Då kan det
sköta commit-filen åt dig och påminna dig om att spara.

## Så gör du i ett nytt projekt

I Gittas mapp finns **`kopiera-till-nya-projekt/`** med allt som behövs:

| Fil | Vad den gör |
|---|---|
| `CLAUDE.md` | Instruktioner som Claude Code läser automatiskt: skriv `.Gitta-commit`, påminn om att committa, kolla `git status`, uppdatera README, håll nycklar utanför |
| `gitta-docs/` | Guider som instruktionerna hänvisar till: commit-filer, README, ordlista och känslig information (med `.gitignore`-mall) |
| `LÄS-MIG.md` | Kort beskrivning av stegen (behöver inte kopieras) |

1. Kopiera **innehållet** i `kopiera-till-nya-projekt/` (utom `LÄS-MIG.md`) till
   projektets rotmapp.
2. Har projektet redan en `CLAUDE.md`: klistra in texten längst ned i den i
   stället för att skriva över.
3. Starta Claude Code i projektmappen. Klart.

## Så fungerar det

1. Du ber AI-verktyget ändra något.
2. Det skriver `.Gitta-commit` med en beskrivning.
3. Du öppnar Gitta, väljer projektet och ser beskrivningen i rutan.
4. Du läser, justerar vid behov och trycker **commit and push**.
5. Gitta tar bort filen, och nästa omgång börjar på ett rent blad.

## Påminnelser utan AI

Gitta visar **● N ändringar** i projektlistan för projekt med osparat arbete,
och en orange text i projektvyn när du har ändringar men ingen beskrivning.
Titta i listan innan du stänger av datorn.

## Underhåll

Guiderna i `kopiera-till-nya-projekt/gitta-docs/` är kopior av
`docs/03-readme-guide.md`, `docs/04-commit-filer.md` och
`docs/05-ordlista.md`. Ändrar du en av dem, ändra båda. Guiden
`kanslig-information.md` finns bara i `kopiera-till-nya-projekt/`; Gittas egna
regler står i [07-uppdatera-programmet.md](07-uppdatera-programmet.md).
