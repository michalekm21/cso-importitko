#!/bin/env python3

import os
from osgeo import osr, ogr
import logging
from dotenv import load_dotenv


class GeometryDistanceCalculator:
    def __init__(self, dbname, host, user, password, table):
        self.dsn = (
            f"MYSQL:{dbname},host={host},user={user},"
            f"password={password},port=3306"
        )
        self.table = table
        self.ds = None
        self.layer = None
       
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
        try:
            self.ds = ogr.Open(self.dsn, 0)
            if not self.ds:
                self.logger.error("Nelze se připojit k databázi.")
                raise Exception("Nelze se připojit k databázi.")
            self.logger.info("Připojeno k databázi.")
        except Exception as e:
            self.logger.exception("Chyba při připojování k databázi: %s", e)
            raise

    def fetch_data(self):
        try:
            sql = f"SELECT Path1Geometry, Path2Geometry FROM {self.table}"
            self.layer = self.ds.ExecuteSQL(sql)
            self.logger.info("Data načtena z databáze.")
        except Exception as e:
            self.logger.exception("Chyba při načítání dat: %s", e)
            raise

    def calculate_distance(self):
        try:
            for feature in self.layer:
                geom_l = feature.GetGeomFieldRef(0)
                geom_p = feature.GetGeomFieldRef(1)

                # Transformace geometrií
                geom_l.Transform(self.transform)
                geom_p.Transform(self.transform)

                # Výpočet vzdálenosti mezi linií a bodem
                distance = geom_l.Distance(geom_p)
                self.logger.info(
                    "Vzdálenost mezi linií a bodem: %s metrů", distance)

        except Exception as e:
            self.logger.exception("Chyba při výpočtu vzdálenosti: %s", e)
            raise

    def release(self):
        try:
            if self.layer:
                self.ds.ReleaseResultSet(self.layer)
                self.logger.info("Připojení k databázi bylo uzavřeno.")
        except Exception as e:
            self.logger.exception("Chyba při uvolňování zdrojů: %s", e)
            raise


# Použití třídy
if __name__ == "__main__":
    load_dotenv(".env")
    hostname = os.environ.get("DB_HOST")
    database = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASS")
    
    calculator = GeometryDistanceCalculator(
        dbname='michalek',
        host=hostname,
        user=username,
        password=password,
        # table='vw_lsd_oi oi LEFT JOIN vw_lsd_ol ol ON oi.ObsListId = Id'
        table='project.LSD_Square'
    )

    try:
        calculator.connect()
        calculator.fetch_data()
        calculator.calculate_distance()
    finally:
        calculator.release()
