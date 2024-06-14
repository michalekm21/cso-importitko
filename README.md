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
> [!NOTE]
> Bez předešlého nastavení po vás bude tento nástroj požadovat kredence serveru a přihlašovací údaje.
## Výpis parametrů
Tímto příkazem si můžete vypsat všechny možné paramnetry nástroje (filtrování, výstupy):
```shell
python <CESTA K SOUBORU lsd_vzdalenosti.py> -h
```
## Data se jmény pozorovatel
Ve výchozím nastavení nebudou výstupní data obstahovat Jména pozorovatel, pokud nejsou vyžadována k filtrování – z výkonnostních důvodů. Pokud si přejete, aby data obsahovala jména, i přez to, že se jimy nefiltruje, můžete toto omezení obejít takto:
```
python <CESTA K SOUBORU lsd_vzdalenosti.py> --user '.*'
```
Neboť filtrování pomocí jmen umožňuje použití regexu, můžeme použít takovou podmínku, jíž budou vyhovovat všechna jména.
> [!WARNING]
> Filtrovani pomocí jmen může značně zvýšit čas stahování dat.
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
## Změna dotazu vstupních dat
Pokud si přejete změnit dotaz, jímž se získávají vstupní data, přečtěte si dokumentaci v tomto souboru:
[QUERY.md](utils/QUERY.md)
