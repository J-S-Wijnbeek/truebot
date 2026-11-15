# Vertaalbot voor Discord

Een Discord-bot die een server met meerdere talen laat voelen als één gesprek. Iedereen kiest een taal met een vlag, ziet alleen het kanaal van die taal, en leest en schrijft daar in zijn eigen taal. De bot vertaalt elk bericht met Claude en zet het in de kanalen van de andere talen, met de naam en profielfoto van de echte afzender.

> **Status:** de code staat in `bot.py`. De losse onderdelen zijn getest met `python -m unittest`; de bot is nog niet op een echte Discord-server uitgeprobeerd.

## Wat de bot doet

- **Taal kiezen:** in een welkomstkanaal klik je op een vlagknop (🇷🇺 of 🇬🇧) en krijg je de bijbehorende rol. Nog een keer klikken haalt de rol weer weg.
- **Een kanaal per taal:** `#chat-ru` en `#chat-en`. Je rol bepaalt welk kanaal je ziet.
- **Spiegelen:** een bericht in het ene kanaal verschijnt vertaald in de andere kanalen, via een webhook met de naam en avatar van de afzender.
- **Context:** de laatste berichten gaan mee naar Claude, zodat slang, grappen en verwijzingen goed vertaald worden.
- **Synchroon:** bewerk je een bericht, dan wordt de vertaling bijgewerkt. Verwijder je het, dan verdwijnt het overal.
- **Antwoorden:** boven een vertaald antwoord staat een citaat met een link naar het bericht in je eigen kanaal.
- **Pings:** `@persoon` en `@rol` blijven werken. `@everyone` en `@here` alleen als de afzender dat recht heeft.
- **Bijlagen:** afbeeldingen en bestanden gaan mee. Berichten met alleen emoji's of links worden niet vertaald maar wel doorgezet.
- **Reacties:** onder een vertaald bericht staat een regeltje met reacties uit de andere kanalen, bijvoorbeeld `👍 Ivan, Olga · 😂 Dmitri`.
- **Log:** een logkanaal voor beheerders met originelen, vertalingen, bewerkingen, verwijderingen, rolwissels en fouten.

## Wat Discord niet toelaat

- Naast de naam van een vertaald bericht staat een **APP-label**. Dat kan niet weg.
- Klikken op de naam opent niet het echte profiel, en de rolkleur van de naam ontbreekt.
- De echte antwoordbalk en echte reacties namens iemand anders kunnen niet. Daarom het citaat en het reactieregeltje.
- Een vertaling kan maximaal 2000 tekens zijn. Langere tekst wordt afgekapt.
- Het reactieregeltje staat alleen onder vertaalde berichten. Het oorspronkelijke bericht is van de afzender en kan de bot niet aanpassen, dus de afzender ziet reacties uit andere kanalen niet.

## Wat je nodig hebt

- Python 3.10 of nieuwer
- Een Discord-account met beheerrechten op je server
- Een API-sleutel van Anthropic (https://console.anthropic.com)

## Stap 1: de bot aanmaken in Discord

1. Ga naar https://discord.com/developers/applications en klik **New Application**.
2. Open **Bot** in het menu links en klik **Reset Token**. Kopieer het token en bewaar het.
3. Zet op dezelfde pagina **Message Content Intent** aan.
4. Open **OAuth2 → URL Generator**. Vink bij *Scopes* `bot` en `applications.commands` aan.
5. Vink bij *Bot Permissions* aan:
   - Manage Roles
   - Manage Channels
   - Manage Webhooks
   - Manage Messages
   - View Channels
   - Send Messages
   - Read Message History
   - Add Reactions
   - Embed Links
   - Attach Files
6. Open de link onderaan de pagina en voeg de bot toe aan je server.
7. Ga in je server naar **Serverinstellingen → Rollen** en sleep de rol van de bot naar boven. Hij moet boven de taalrollen staan, anders mag hij ze niet uitdelen.

## Stap 2: de bestanden klaarzetten

Zet deze bestanden in één map:

```
vertaalbot/
├── bot.py
├── test_bot.py
├── requirements.txt
├── .env.example
├── .env
└── README.md
```

`requirements.txt`:

```
discord.py>=2.4
anthropic
python-dotenv
```

Kopieer `.env.example` naar `.env` en vul de twee sleutels in (deel `.env` nooit en zet het niet op GitHub; `.gitignore` houdt het al buiten de repo):

```
DISCORD_TOKEN=plak-hier-je-discord-token
ANTHROPIC_API_KEY=plak-hier-je-anthropic-sleutel
CLAUDE_MODEL=claude-haiku-5-5
CONTEXT_MESSAGES=30
WELCOME_CHANNEL_ID=1544331201664520192
LANGUAGE_CHANNELS=en:1571606720235446423,ru:1571606767924809909
RATE_LIMIT_PER_MINUTE=30
DAILY_LIMIT=2000
MAX_MESSAGE_LENGTH=1500
```

| Instelling | Betekenis |
| --- | --- |
| `DISCORD_TOKEN` | Het token uit stap 1 |
| `ANTHROPIC_API_KEY` | Je sleutel van Anthropic |
| `CLAUDE_MODEL` | Het model dat vertaalt. `claude-haiku-5-5` is snel en goedkoop, `claude-sonnet-5-5` is sterker in nuance |
| `CONTEXT_MESSAGES` | Hoeveel eerdere berichten als context meegaan |
| `WELCOME_CHANNEL_ID` | Bestaand kanaal voor de vlagknoppen. Leeg = de bot maakt `#kies-je-taal` aan |
| `LANGUAGE_CHANNELS` | Bestaande taalkanalen als `code:kanaal-id`, gescheiden door komma's. Leeg = de bot maakt `#chat-ru` en `#chat-en` aan |
| `RATE_LIMIT_PER_MINUTE` | Maximaal aantal vertalingen per persoon per minuut |
| `DAILY_LIMIT` | Maximaal aantal vertalingen per dag voor de hele bot |
| `MAX_MESSAGE_LENGTH` | Berichten langer dan dit aantal tekens worden niet vertaald |

## Stap 3: installeren en starten

Open een terminal in de map `vertaalbot`.

**Windows:**

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

**Mac of Linux:**

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

De bot is online zolang dit venster open staat. Stoppen doe je met `Ctrl+C`. De volgende keer hoef je alleen de omgeving te activeren en `python bot.py` te draaien.

## Stap 4: de server inrichten

Typ in je server (alleen beheerders kunnen dit):

```
/setup
```

De bot maakt dan de rollen, de taalkanalen, de webhooks, het logkanaal en een welkomstkanaal met de vlagknoppen. Staan er kanalen in `WELCOME_CHANNEL_ID` en `LANGUAGE_CHANNELS`, dan gebruikt hij die in plaats van nieuwe aan te maken. Let op: bestaande taalkanalen worden daarbij verborgen voor iedereen zonder de bijbehorende taalrol. Wil je de knoppen in een bestaand kanaal, geef dat kanaal dan mee:

```
/setup kanaal:#welkom
```

Zorg dat gewone leden in dat kanaal niet kunnen typen, zodat het keuzebericht bovenaan blijft.

## Commando's

| Commando | Wat het doet |
| --- | --- |
| `/setup [kanaal]` | Maakt rollen, kanalen, webhooks, logkanaal en het keuzebericht |
| `/taal-toevoegen code naam vlag` | Voegt een taal toe, bijvoorbeeld `es` `Spaans` `🇪🇸` |
| `/log niveau` | `alles`, `belangrijk` (bewerkingen, verwijderingen, rollen, fouten) of `uit` |

## Het log

Het logkanaal is alleen zichtbaar voor beheerders. Standaard staat het op `alles`. Verwijderde berichten blijven in het log staan, dus vermeld in je serverregels dat er wordt meegelogd.

## Beveiliging

- **Sleutels:** het token en de API-sleutel staan alleen in `.env`, dat niet in de repo komt. De bot logt ze nergens.
- **Alleen beheerders:** de commando's zijn verborgen voor gewone leden en controleren het beheerdersrecht nog een keer zelf.
- **Rem op spam en kosten:** per persoon maximaal `RATE_LIMIT_PER_MINUTE` vertalingen per minuut, voor de hele bot maximaal `DAILY_LIMIT` per dag, en geen vertaling boven `MAX_MESSAGE_LENGTH` tekens. Zulke berichten worden wel doorgezet, met het regeltje "niet vertaald", en gemeld in het log.
- **Pings:** de bot pingt alleen wie de afzender zelf mocht pingen. Een vertaling kan dus geen `@everyone` toevoegen.
- **Misleiden van de vertaler:** Claude krijgt de opdracht om berichten alleen te vertalen en instructies in een bericht te negeren.
- **Geen lussen:** berichten van bots en webhooks worden niet gespiegeld.
- **Opslag:** `vertaalbot.db` bevat berichtteksten van de laatste 30 dagen (nodig voor bewerken, verwijderen en citaten). Oudere berichten worden bij het starten gewist. Deel dit bestand niet.

## Kosten

- **Discord:** gratis.
- **Claude:** je betaalt per vertaald bericht. Met Haiku is dat voor een normale groep naar verwachting hooguit een paar euro per maand.
- **Je eigen computer:** gratis, maar de bot werkt alleen als je computer aan staat.

## Als het niet werkt

| Probleem | Oplossing |
| --- | --- |
| Onder een bericht staat "niet vertaald" | De spamrem of daglimiet is geraakt, of het bericht is te lang. Zie het logkanaal en de instellingen onder Beveiliging |
| De bot reageert nergens op | Controleer of **Message Content Intent** aan staat en of het token klopt |
| `/setup` verschijnt niet | Wacht een paar minuten en herstart Discord. Nieuwe commando's hebben soms even nodig |
| De vlagknop geeft geen rol | Sleep de rol van de bot boven de taalrollen |
| Berichten worden niet vertaald | Controleer `ANTHROPIC_API_KEY` en kijk in het logkanaal naar foutmeldingen |
| Berichten verschijnen dubbel | Er draaien twee exemplaren van de bot. Sluit er één |

## Later: altijd online

Om de bot dag en nacht te laten draaien kun je hem op een server zetten, bijvoorbeeld Fly.io (ongeveer $2 per maand voor de kleinste machine). Let dan op drie dingen: automatisch stoppen uitzetten, precies één machine draaien, en de sleutels als secrets instellen in plaats van in `.env`.
