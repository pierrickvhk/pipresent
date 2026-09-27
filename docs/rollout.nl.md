# PiPresent — eerste uitrol op een vergaderscherm

Gebruik de [Nederlandse gebruikershandleiding](../README.nl.md) voor installatie,
USB-voorbereiding, autostart en verwijdering. Deze checklist helpt bij de overdracht aan
collega's zonder die instructies op meerdere plaatsen bij te houden.

**MANUAL RASPBERRY PI TEST REQUIRED.** Dit is een pilotchecklist; echte hardwarevalidatie
is nog niet uitgevoerd.

## Voorbereiden

- Raspberry Pi 4 of nieuwer met Raspberry Pi OS 64-bit Desktop en HDMI-scherm.
- Desktopgebruiker met internettoegang voor de installatie.
- USB-stick met een eigen testpresentatie en de juiste lettertypen op de Pi.
- Desktop auto-login ingeschakeld en schermblanking uitgeschakeld.

De broncode staat op [pierrickvhk/pipresent](https://github.com/pierrickvhk/pipresent).
PowerPoint wordt als statische slides afgespeeld: animaties, Morph en interactieve content
worden niet ondersteund.

## Samen controleren

- [ ] `~/.local/bin/pipresent doctor` geeft geen fouten; waarschuwingen zijn onderzocht.
- [ ] USB-import werkt en logs tonen dat de presentatie lokaal is opgeslagen.
- [ ] PPTX en PDF tonen de verwachte inhoud, lettertypen en slidevolgorde.
- [ ] Video loopt herhaaldelijk met hetzelfde mpv-proces; eventuele zwarte bronframes zijn apart beoordeeld.
- [ ] De USB-stick is via de desktop veilig uitgeworpen; de presentatie blijft spelen.
- [ ] Na een reboot zonder USB verschijnt de laatst geïmporteerde presentatie.
- [ ] Autostart werkt na desktop-login en het scherm blijft actief.
- [ ] Collega's weten hoe ze met `q` stoppen en waar ze de logs vinden.

## Overdragen

Noteer Pi-model, OS-image, toolversies, testbestanden en bevindingen in het
[validatierecord](validation.md). Rond ook de volledige [hardwarechecklist](acceptance.md) af.

Bij problemen:

```bash
~/.local/bin/pipresent doctor
tail -n 100 ~/.local/state/pipresent/pipresent.log
```

Zie [troubleshooting](troubleshooting.md). Claim geen gegarandeerd onderbrekingsvrije
videoweergave: bronmateriaal, decoder en scherm kunnen het resultaat beïnvloeden.
