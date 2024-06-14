Pole, o nichž tyto nástroje předpokládají, že budou ve vstupních datech. Dotazy můžete změnit v *query.yaml*.
## výpočet vzdálenosti (*distance_calculator.py*):
- Souřadnice pozorovatele a pozorovaného v WGS84: *LatObs, LonObs, LatItem, LonItem*
- Jeden sloupek s geometrií linie
> [!WARNING]
> Tento nástroj umožňuje práci s pouze jedním polem geometrie.
## Filtrování (*query-builder.py*):
- Název druhu – *NameCS* a *NameLA* – český a latinský
- Datum pozorování *ObsDate*
- Sloupec Sitename obsahující v prvních 6 místech KFME ID
### Filtrování jménem uživatele:
Z důvodu výkonu používá tento nástroj rozdílný dotaz (template_user) v případě filtrování dle uživatele. Pokud už toto rozdělení není nutné, mohou oba dotazy být totožné.
- *Observer* – Jméno pozorovatele
- *ObserversEmail* – e-mail pozorovatele
