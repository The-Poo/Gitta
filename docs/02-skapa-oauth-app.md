# Engångssteg: skapa en OAuth App på GitHub

Detta görs **en gång av den som delar ut Gitta**. Användarna (din vän) behöver
aldrig göra det.

En OAuth App är bara ett namn som GitHub känner igen, så att användaren kan
godkänna "Gitta" utan att lämna ut sitt lösenord. Vem som helst med ett
GitHub-konto kan godkänna appen, även om den ägs av någon annan.

## Steg

1. Logga in på <https://github.com>.
2. Klicka på din **profilbild uppe till höger** och välj **Settings**.
   Det ska vara dina *personliga* inställningar, inte inställningarna för ett
   projekt (repository) eller en organisation. De har en annan meny som
   saknar Developer settings.
3. I menyn till vänster: **Developer settings**. Den ligger längst ned i
   menyn, så du kan behöva scrolla. Genväg som går direkt dit:
   <https://github.com/settings/developers>
4. Välj **OAuth Apps**.
5. Tryck **New OAuth App**. Har du aldrig skapat någon heter knappen
   **Register a new application**.
6. Fyll i formuläret **Register a new OAuth app**:

   | Fält | Värde |
   |---|---|
   | Application name | `Gitta` |
   | Homepage URL | `https://github.com` |
   | Application description | lämna tomt (valfritt) |
   | Redirect URIs | `http://localhost`. Adressen används inte av Gitta, men fyll i något. Vägrar GitHub den, skriv `https://github.com`. |
   | Allow wildcard matching | **inte ikryssad** |
   | Enable Device Flow | **ikryssad**. Utan detta fungerar inte inloggningen. |
   | Expire user access tokens | **inte ikryssad**. Gitta kan inte förnya tokens som slutar gälla efter några timmar. |
7. Tryck **Register application**.
8. Kopiera **Client ID** från sidan som visas. Det är inte hemligt. Skapa
   **inte** någon Client secret, den behövs inte.

Hittar du ändå inte Developer settings: öppna direktlänken i punkt 3. Om
även den ger "404" är du inloggad på fel konto eller så saknar kontot
rättigheten (t.ex. ett skolkonto/organisationskonto). Använd då ditt egna
personliga konto.

> Fältnamnen i punkt 6 är hämtade från GitHubs formulär (november 2026) och
> menynamnen från
> [GitHubs dokumentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app).
> GitHub ändrar sitt utseende ibland, så avvikelser kan förekomma.

## Lägg in Client ID i programmet

Alternativ A (rekommenderas, så att vännen slipper se det):

1. Öppna `gitta/defaults.py` och skriv in:
   `CLIENT_ID = "Ov23...ditt-id..."`
2. Bygg om med `.\build.ps1`.

Alternativ B: starta Gitta utan inbyggt ID. Då visas en ruta där ID:t
klistras in en gång (sparas på den datorn).

## Rättigheter

Gitta ber om scope `repo`, som ger åtkomst till användarens projekt (även
privata). Det är det som krävs för att kunna lista, skapa och pusha.
Användaren ser detta på godkännandesidan och kan när som helst ta bort
åtkomsten på <https://github.com/settings/applications>.
