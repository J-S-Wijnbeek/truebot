"""Maakt het .env-bestand aan: python maak_env.py

Vraagt om het Discord-token en de Anthropic-sleutel en zet ze in .env,
samen met de overige instellingen uit .env.example. Het .env-bestand
blijft op deze computer; git negeert het.
"""

import getpass
import pathlib
import sys

FOLDER = pathlib.Path(__file__).parent
EXAMPLE = FOLDER / ".env.example"
TARGET = FOLDER / ".env"


def fill_in(template: str, values: dict[str, str]) -> str:
    """Vervangt de regels van de gegeven instellingen in de tekst van .env.example."""
    lines = []
    for line in template.splitlines():
        key = line.split("=", 1)[0]
        lines.append(f"{key}={values[key]}" if key in values else line)
    return "\n".join(lines) + "\n"


def ask(label: str, prefix: str = "") -> str:
    while True:
        # getpass verbergt wat je plakt, zodat de sleutel niet op het scherm blijft staan.
        value = getpass.getpass(f"{label} (plakken en Enter, de invoer blijft onzichtbaar): ").strip()
        if value and value.startswith(prefix):
            return value
        print(f"  Dat lijkt niet te kloppen{f' (moet beginnen met {prefix})' if prefix else ''}. Probeer opnieuw.")


def main() -> None:
    if TARGET.exists():
        answer = input(".env bestaat al. Overschrijven? (j/n): ").strip().lower()
        if answer != "j":
            sys.exit("Niets gewijzigd.")
    values = {
        "DISCORD_TOKEN": ask("Discord-token"),
        "ANTHROPIC_API_KEY": ask("Anthropic-sleutel", "sk-ant-"),
    }
    TARGET.write_text(fill_in(EXAMPLE.read_text(encoding="utf-8"), values), encoding="utf-8")
    print(f"Klaar: {TARGET.name} is aangemaakt. Start de bot met: python bot.py")


if __name__ == "__main__":
    main()
