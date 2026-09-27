# PiPresent - Installatiehandleiding voor collega’s

## Doel
PiPresent maakt een Raspberry Pi om tot een plug-and-play presentatiescherm. Op een USB-stick geplaatste presentaties worden automatisch geïmporteerd en fullscreen afgespeeld in een lus.

## Vereisten

- Raspberry Pi 4 of nieuwer
- Raspberry Pi OS 64-bit Desktop
- HDMI-scherm aangesloten
- USB-stick met presentatiebestand
- Desktopgebruiker account op de Pi
- Internetverbinding voor installatie

## Ondersteunde bestanden

- `.pptx`
- `.pdf`
- `.mp4`
- `.mkv`
- `.mov`

> Opmerking: PowerPoint-animaties en interactieve content worden niet volledig ondersteund in deze versie.

---

## 1. Project ophalen
Open een terminal op de Raspberry Pi en voer uit:

```bash
git clone https://github.com/YOUR_GITHUB_OWNER/pipresent.git
cd pipresent
```

Vervang `YOUR_GITHUB_OWNER` door de juiste GitHub-owner of gebruik de juiste lokale checkout.

---

## 2. Installatie uitvoeren
Voer de installer uit als de desktopgebruiker, zonder `sudo`:

```bash
./scripts/install.sh --autostart
```

De installer:
- installeert de benodigde pakketten (`python3`, `mpv`, `libreoffice-impress`, `poppler-utils`)
- maakt een virtuele omgeving aan
- zet de launcher op in `~/.local/bin/pipresent`
- configureert autostart voor de desktop

Controleer daarna of het commando werkt:

```bash
~/.local/bin/pipresent --help
```

Als je het kort wilt kunnen aanroepen:

```bash
export PATH="$HOME/.local/bin:$PATH"
pipresent --help
```

---

## 3. USB-stick voorbereiden
Zet de presentatie op de root van de USB-stick, niet in een submap.

Voorbeeld:

```text
USB/
├── presentation.pptx
└── presentation.json
```

Voorbeeld `presentation.json`:

```json
{
  "content": "presentation.pptx",
  "slide_duration": 8
}
```

Belangrijk:
- `content` is exact de bestandsnaam
- extensies zijn niet hoofdlettergevoelig
- geen submap gebruiken
- alleen bestanden in de root worden herkend
- bij meerdere supported bestanden moet je `presentation.json` gebruiken

---

## 4. Presentatie starten
Steek de USB-stick in de Pi en start vanuit de desktop:

```bash
~/.local/bin/pipresent start
```

PiPresent zal:
- de USB detecteren
- de presentatie importeren
- lokaal opslaan
- fullscreen afspelen in lus

Zodra playback begint, kun je de USB-stick veilig verwijderen.

---

## 5. Autostart controleren
Na installatie met `--autostart` start PiPresent automatisch na het inloggen op de desktop.
Controleer het volgende:

- desktop auto-login is ingeschakeld
- schermblanking staat uit
- `~/.config/labwc/autostart` bevat het PiPresent-blok

Als de app niet automatisch start:

```bash
~/.local/bin/pipresent doctor
```

---

## 6. Diagnose bij problemen
Gebruik samen met de collega’s deze snelle checks:

```bash
~/.local/bin/pipresent doctor
~/.local/bin/pipresent start --wait 7
tail -n 100 ~/.local/state/pipresent/pipresent.log
```

Typische oorzaken:
- USB niet gevonden
- meerdere USB-bronnen tegelijk
- bestandsnaam in `presentation.json` klopt niet
- mpv, LibreOffice of Poppler ontbreekt
- schermblanking staat aan
- Wayland/desktop sessie ontbreekt

Zie ook: `docs/troubleshooting.md`

---

## 7. Verlies van scherm of display
Zet schermblanking uit via:

- Raspberry Pi OS → Control Centre → Display → Screen Blanking
- of Raspberry Pi Configuration → Display

Dit is essentieel voor een stabiele presentatieweergave.

---

## 8. Stoppen / verwijderen
Om de presentatie te stoppen:

- druk op `q` in het mpv-venster, of
- gebruik Ctrl+C in de terminal

Om PiPresent te verwijderen:

```bash
./scripts/uninstall.sh
```

Voor volledige verwijdering inclusief data:

```bash
./scripts/uninstall.sh --purge
```

---

## 9. Checklijst voor een eerste test

- [ ] Pi draait op Raspberry Pi OS Desktop
- [ ] `pipresent doctor` draait zonder fatale fouten
- [ ] USB-stick met een correcte `presentation.json` werkt
- [ ] een PPTX presenteert correct
- [ ] een PDF presenteert correct
- [ ] video afgespeeld in loop zonder duidelijke onderbreking
- [ ] scherm blijft actief en blanking is uit
- [ ] autostart werkt na reboot
- [ ] logs tonen succesvolle import en playback

---

## Belangrijkste waarschuwing
Dit project is nog niet volledig hardware-geverifieerd op echte Raspberry Pi-apparatuur. De projectdocumentatie noemt expliciet dat een handmatige Raspberry Pi-test nog verplicht is voordat het als productievere klaar kan worden beschouwd.

Gebruik dit document daarom als installatietool voor een pilot / testomgeving, niet als gegarandeerde productie-setup.
