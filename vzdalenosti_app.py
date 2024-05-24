#!/bin/env python3
"""Aplikace pro výpočet vzdálenosti pro LSD"""

import os
import logging
import argparse
import yaml
from osgeo import osr, ogr
from dotenv import load_dotenv

os.environ['SHAPE_ENCODING'] = "utf-8"
osr.UseExceptions()


class GeometryDistanceCalculator:
    """Počítá vzdálenosti z Geometrie"""
    def __init__(self, database, hostname, username, password):
        self.dsn = (
            f"MYSQL:{database},host={hostname},user={username},"
            f"password={password},port=3306"
        )
        self.ds = None
        self.layer = None

        self.out_layer = None
        self.out_ds = None

        self.output_path = None
        self.driver_name = None

        # Nastavení logování
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Definice transformace na SRID 5514
        self.source_srs = osr.SpatialReference()
        # Prohozené souřadnice
        self.source_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        # Předpokládáme, že původní souřadnice jsou ve WGS84
        self.source_srs.ImportFromEPSG(4326)

        self.target_srs = osr.SpatialReference()

        self.target_srs.ImportFromProj4(
            "+proj=krovak +lat_0=49.5 +lon_0=24.8333333333333 "
            "+alpha=30.2881397527778 +k=0.9999 +x_0=0 +y_0=0 +ellps=bessel "
            "+towgs84=589,76,480,0,0,0,0 +units=m +no_defs +type=crs"
            )

        self.transform = osr.CoordinateTransformation(
            self.source_srs, self.target_srs)

    def connect(self):
        """Připojení k DB"""
        try:
            self.ds = ogr.Open(self.dsn, 0)
            if not self.ds:
                self.logger.error("Nelze se připojit k databázi.")
                raise ConnectionError("Nelze se připojit k databázi.")
            self.logger.info("Připojeno k databázi.")
        except Exception as e:
            self.logger.exception("Chyba při připojování k databázi: %s", e)
            raise

    def fetch_data(self, sql):
        """Stahuje data z DB"""
        try:
            self.layer = self.ds.ExecuteSQL(sql)
            self.logger.info("Data načtena z databáze.")
            return self.layer
        except Exception as e:
            self.logger.exception("Chyba při načítání dat: %s", e)
            raise

    def save_data(self, driver_name, output_path):
        """Ukládá stažená data"""
        self.driver_name = driver_name
        self.output_path = output_path
        try:
            driver = ogr.GetDriverByName(self.driver_name)
            if os.path.exists(self.output_path):
                driver.DeleteDataSource(self.output_path)

            self.out_ds = driver.CreateDataSource(self.output_path)
            self.out_layer = self.out_ds.CopyLayer(
                self.layer, self.layer.GetName())
        except Exception as e:
            self.logger.exception("Chyba při ukládání ustažených dat: %s", e)
            raise
        finally:
            self.release()

    def calculate_distance(self):
        """ Počítá vzdálenost ze stažených dat"""
        self.out_layer.CreateField(ogr.FieldDefn("obs2line", ogr.OFTReal))
        self.out_layer.CreateField(ogr.FieldDefn("item2line", ogr.OFTReal))
        self.out_layer.CreateField(ogr.FieldDefn("obs2item", ogr.OFTReal))

        try:
            for feature in self.out_layer:
                # Získání geometrií
                geom_l = feature.GetGeomFieldRef(0)
                if geom_l is None:
                    continue    # !!přeskočit pokud schází geometrie linie

                # obs
                geom_obs = ogr.Geometry(ogr.wkbPoint)
                geom_obs.AddPoint(float(feature.GetField("LonObs")),
                                  float(feature.GetField("LatObs")))
                # item
                geom_item = ogr.Geometry(ogr.wkbPoint)
                geom_item.AddPoint(float(feature.GetField("LonItem")),
                                   float(feature.GetField("LatItem")))

                # Transformace geometrií
                geom_l.Transform(self.transform)
                geom_obs.Transform(self.transform)
                geom_item.Transform(self.transform)

                # Výpočet vzdálenosti mezi linií a bodem
                obs2line = geom_l.Distance(geom_obs)
                item2line = geom_l.Distance(geom_item)
                obs2item = geom_item.Distance(geom_obs)

                feature.SetField('obs2line', obs2line)
                feature.SetField('item2line', item2line)
                feature.SetField('obs2item', obs2item)

                self.out_layer.SetFeature(feature)

                # self.logger.info(
                #     "Vzdálenost mezi obs a line: %s metrů", obs2line)

        except Exception as e:
            self.logger.exception("Chyba při výpočtu vzdálenosti: %s", e)
            raise

        del self.out_ds  # Finish and save data
        del self.out_layer
        self.logger.info(
            "Data exported to %s : %s ", self.driver_name, self.output_path)

    def release(self):
        """Uvolnit připojení k DB"""
        try:
            if self.layer:
                self.ds.ReleaseResultSet(self.layer)
                self.logger.info("Připojení k databázi bylo uzavřeno.")
        except Exception as e:
            self.logger.exception("Chyba při uvolňování zdrojů: %s", e)
            raise


def build_query(query_template, min_date, species_name, limit=50):
    """Sestaví dotaz"""
    where_clause = ""

    if not (min_date is not None or species_name is not None):
        return query_template.format(conditions="")

    where_clause = "WHERE "
    clause_conds = []
    if min_date is not None:
        clause_conds.append(f"ObsDate >= '{min_date}'")
    if min_date is not None:
        clause_conds.append(f"(LOWER(NameCS) LIKE LOWER('%{species_name}%'))OR"
                            f"(LOWER(NameLA) LIKE LOWER('%{species_name}%'))")
    where_clause = " AND ".join(clause_conds) + "LIMIT 50"

    print(query_template.format(conditions=where_clause))
    return query_template.format(conditions=where_clause)


def main():
    """main"""
    # údaje z .env < config.yaml
    load_dotenv(".env")
    with open('config.yaml', 'r', encoding="utf-8") as file:
        config = yaml.safe_load(file)
    # podmíněné přiřazení proměnných
    conf_hostname = (
        config['hostname'] if 'hostname' in config
        else os.environ.get("DB_HOST"))
    conf_database = (
        config['database'] if 'database' in config
        else os.environ.get("DB_NAME"))
    conf_username = (
        config['username'] if 'username' in config
        else os.environ.get("DB_USER"))
    conf_password = (
        config['password'] if 'password' in config
        else os.environ.get("DB_PASS"))
    conf_query = (
        config['query_template'] if 'query_template' in config
        else os.environ.get("DB_QUERY"))

    # Parametry příkazu
    parser = argparse.ArgumentParser(
        description="Export LSD data with distances to SHP and GeoJSON.")
    # group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("--hostname",
                        required=True if conf_hostname is None else False,
                        default=conf_hostname,
                        help="Hostname of the MariaDB server.")
    parser.add_argument("--database",
                        required=True if conf_database is None else False,
                        default=conf_database,
                        help="Database name.")
    parser.add_argument("--username",
                        required=True if conf_username is None else False,
                        default=conf_username,
                        help="Username for the database.")
    parser.add_argument("--password",
                        required=True if conf_password is None else False,
                        default=conf_password,
                        help="Password for the database.")
    parser.add_argument("--shp-output", "-shp", required=True,
                        help="Path to output the SHP file.")
    parser.add_argument("--min-date",
                        help="Filter by date - either Year or YYYY-MM-DD")
    parser.add_argument("--species",
                        help="Filter by species name - either latin or czech")
    # group.add_argument("--geojson_output", "-geojs",
    #                    help="Path to output the GeoJSON file.")

    args = parser.parse_args()

    calculator = GeometryDistanceCalculator(
        'michalek', args.hostname, args.username, args.password)

    try:
        calculator.connect()
        calculator.fetch_data(
            build_query(conf_query, args.min_date, args.species, limit=50))
        if args.shp_output is not None:
            calculator.save_data("ESRI Shapefile", "vzdalenosti.shp")
        # if args.geojson_output is not None:
        #     calculator.save_data("GeoJSON", "vzdalenosti.geojson")
        calculator.calculate_distance()
    except Exception as ex:
        calculator.logger.error(ex)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
