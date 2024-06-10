Toto je program, který stahuje geografická data a dopočítává potřebné vzdálenosti pro lsd.
## Instalace závislostí
Knihovny, potřebné pro spuštění nástroje doinstalujete pomocí tohoto příkazu:
```shell
python -m pip install halo pyyaml
```
## Výpis parametrů
Tímto příkazem si můžete vypsat všechny možné paramnetry nástroje (filtrování, výstupy):
```shell
python lsd_vzdalenosti.py -h
```
## Ukládání přihlašovacích údajů
Pokud si nepřejete muset při každém spuštění nástroje zadávat své přihlašovací údaje, můžete je uložit do konfiguračního souboru *login.yaml*. Obsah tohoto souboru by měl mít takovýto formát:
```yaml
hostname: <ADRESA SERVERU S DATY>
database: <JMÉNO DATABÁZE V NÍŽ BUDEME OPEROVAT>
username: <UŽIVATELSKÉ JMÉNO>
password: <HESLO UŽIVATELE>
```
Příklad takovéhoto nastavení se nachází v souboru *login.yaml.example*.
> [!WARNING]
> Tento soubor musí být ve stejné jako soubor *lsd_vzdalenosti.py*, jinak nebude využit.