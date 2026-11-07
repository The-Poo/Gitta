# Känslig information: så undviker du att läcka den

Det du pushar till GitHub kan kopieras av andra så fort det legat där, särskilt
i publika projekt. Även om du raderar det efteråt finns det kvar i historiken.
Därför gäller det att aldrig skicka upp känsliga saker från början.

## Vad räknas som känsligt?

- Lösenord och inloggningsuppgifter
- API-nycklar och tokens (till exempel `ghp_...`, `sk-...`, `AKIA...`)
- Privata nycklar (`.pem`, `.key`, `id_rsa`, `.pfx`, `.p12`)
- `.env`-filer och andra inställningsfiler med hemligheter
- Databasfiler och exporter med personuppgifter eller kunddata
- Filer från din egen dator som inte hör till projektet (dokument, bilder,
  lösenordshanterarens fil `.kdbx`)

## Så gör du

1. **Lägg hemligheter i en `.env`-fil** (eller miljövariabler) som koden läser,
   aldrig direkt i koden.
2. **Lägg `.env` i `.gitignore` innan du skapar den.**
3. **Titta på listan över ändrade filer** innan du trycker commit and push.
   Känner du inte igen en fil: spara den inte.
4. **Gitta varnar** innan du pushar, och när du lägger upp ett nytt projekt
   eller en befintlig mapp, om en fil har ett namn som `.env` eller innehåller
   något som liknar en nyckel, token eller `password = "..."`. Du ser filnamn
   och radnummer. Svara Nej om du är osäker. Kontrollen är ett skyddsnät och
   hittar inte allt.
5. **Claude Code varnar** (om `CLAUDE.md` från den här mappen ligger i
   projektet). Lyssna på varningen.
6. **Gör projektet private** om du är osäker. Det är standard i Gitta. Public
   gör du först när du har kontrollerat allt.

## Mall för `.gitignore`

Skapa en fil som heter `.gitignore` i projektets rotmapp med minst detta:

```
# Hemligheter
.env
.env.*
*.pem
*.key
*.pfx
*.p12
*.kdbx
*.token
id_rsa*
id_ed25519*
config.json

# Gitta
.Gitta-commit

# Genererat
__pycache__/
*.pyc
node_modules/
build/
dist/
.venv/
```

Lägg till egna rader för andra filer som inte ska med. Filer som redan
committats påverkas inte av `.gitignore`.

## Om det redan hänt

Radera inte bara filen och hoppas på det bästa. Historiken sparar den.

1. **Anta att hemligheten är läckt.**
2. **Byt ut den** hos tjänsten den hör till: skapa ny nyckel, byt lösenord,
   återkalla den gamla.
3. Först därefter kan du ta bort filen och lägga den i `.gitignore`.
4. Gäller det din GitHub-inloggning via Gitta: öppna
   <https://github.com/settings/applications>, ta bort Gitta under
   *Authorized OAuth Apps* och logga in på nytt.
