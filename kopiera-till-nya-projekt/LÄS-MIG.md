# Kopiera till nya projekt

Den här mappen gör att Claude Code (eller liknande) sköter commit-filer och
påminner dig om att spara, i ett nytt projekt.

## Så här gör du

1. Kopiera **innehållet** i den här mappen till projektets rotmapp:
   - `CLAUDE.md`: instruktionerna som Claude Code läser automatiskt
   - `gitta-docs/`: guider som instruktionerna hänvisar till
2. **Finns redan en `CLAUDE.md` i projektet?** Kopiera inte över den. Klistra
   in texten från den här `CLAUDE.md` längst ned i den befintliga.
3. Du behöver inte kopiera den här `LÄS-MIG.md`.
4. Starta Claude Code i projektmappen. Därefter skriver den
   `.Gitta-commit` efter varje ändring, och du trycker **commit and push** i
   Gitta.

## Skydd mot att läcka nycklar och lösenord

`CLAUDE.md` får Claude Code att varna dig, med filnamn, innan något som
liknar en nyckel eller ett lösenord committas, och att skapa en `.gitignore`
om den saknas. Guiden `gitta-docs/kanslig-information.md` innehåller en
färdig mall och förklarar vad man gör om något ändå har läckt.

## Vad händer sedan?

- Claude Code skriver beskrivningen av ändringarna i `.Gitta-commit`.
- Gitta visar den när du väljer projektet. Du läser, justerar och sparar.
- Filen hålls utanför historiken och tas bort efter en lyckad commit.
