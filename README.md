Toto je program, který stahuje geografická data a dopočítává potřebné vzdálenosti pro lsd.
# Použití
Příkazy spouštíme z programu OSGeo4W Shell – ten by měl být přibalený s programem [QGIS](https://www.qgis.org/en/site/).
## Instalace závislostí
Knihovny, potřebné pro spuštění nástroje doinstalujete pomocí tohoto příkazu:
```shell
pip install halo
```
## Spuštení nástroje
Nástroj spouštíme následujícím příkazem.
```
python <CESTA K SOUBORU lsd_vzdalenosti.py>
```
> [!INFO]
> Bez předešlého nastavení po vás bude tento nástroj požadovat kredence serveru a přihlašovací údaje.
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
