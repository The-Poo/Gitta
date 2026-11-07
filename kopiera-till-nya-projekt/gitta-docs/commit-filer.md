# Commit-filer och när man ska committa

## Vad är en commit?

En **commit** är ett sparat steg i ditt projekts historik: "så här såg allt
ut just nu, och det här var vad jag gjorde". Du kan alltid gå tillbaka till
ett tidigare steg. En commit skickas till GitHub med **push**.

Gitta gör båda i ett svep med knappen **commit and push - Spara ändringar**.

## Commit-filen `.Gitta-commit`

Varje commit behöver en beskrivning. I stället för att skriva den i en
dialogruta varje gång kan den ligga i en fil i projektmappen:

```
mitt-projekt/
  .Gitta-commit     <- beskrivningen
  README.md
  ...
```

- Gitta **visar innehållet** när du väljer projektet, och du kan ändra det
  direkt i rutan. Det du skriver i rutan sparas som filen automatiskt.
- När du trycker **commit and push** blir hela texten commit-meddelandet.
- Efter en lyckad commit **tas filen bort** automatiskt, så nästa omgång börjar
  med ett rent blad.
- Filen hålls utanför historiken (Gitta lägger den i `.git/info/exclude`),
  så den hamnar aldrig på GitHub.

### Så skriver du ett bra meddelande

```
Lägg till inloggningssida

**Vad:** Användare kan nu logga in med e-post och lösenord.

- **Formulär** med e-post och lösenord
- **Felmeddelande** vid fel lösenord
- README uppdaterad med hur man startar

**Varför:** Utan inloggning kunde ingen spara sina inställningar.
```

- **Första raden:** kort (helst under 60 tecken), utan formatering. Den blir
  commitens rubrik.
- **Tom rad**, sedan en text där du gärna använder **fet text**
  (`**så här**`), punktlistor (`- punkt`) och rubriker (`# Rubrik`).
- Skriv vad som ändrats och gärna varför, inte bara "ändringar" eller "fix".
- Gitta visar texten formaterad i en förhandsvisning under rutan, medan du
  skriver. På GitHub visas commit-texten som vanlig text, så där syns
  stjärnorna, men punkterna är fortfarande lätta att läsa.

### Flera filer (för verktyg)

Filen kan också vara en **mapp** med samma namn, där varje fil är en del av
meddelandet (sorteras på filnamn). Gitta visar då texten skrivskyddad. Det
är mest användbart för verktyg som skriver flera delar. Börjar du enkelt
räcker en vanlig fil.

## När ska man committa?

Committa ofta, i små steg. Några bra lägen:

- ✅ En funktion eller en liten del fungerar.
- ✅ Innan du provar något riskabelt eller stort (då kan du gå tillbaka).
- ✅ När du fixat ett fel.
- ✅ När du ändrat README eller instruktioner.
- ✅ Innan du stänger datorn för dagen. Då ligger arbetet säkert på GitHub.
- ❌ Vänta inte i flera dagar. En stor, rörig commit är svår att reda ut.

Tumregel: **hellre för ofta än för sällan.** Visar Gitta "● N ändringar" vid
projektet har du osparat arbete.

## Rutin

1. **pull** när du börjar (hämtar nyheter, särskilt om du jobbar från flera datorer).
2. Arbeta.
3. Skriv/uppdatera `.Gitta-commit` (eller i Gitta-rutan).
4. **commit and push**.

Låt verktyget som hjälper dig kod (t.ex. Claude Code) göra steg 3 åt dig: se
[CLAUDE.md](../CLAUDE.md).
