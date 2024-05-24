#!/bin/env python3

import os
from osgeo import osr, ogr
import logging
from dotenv import load_dotenv


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
        
        self.output_path = "vzdalenosti"
        self.driver_name = 'GeoJSON'

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

    def fetch_data(self, sql):
        """Stahuje data z DB"""
        try:
            self.layer = self.ds.ExecuteSQL(sql)
            self.logger.info("Data načtena z databáze.")
            return self.layer
        except Exception as e:
            self.logger.exception("Chyba při načítání dat: %s", e)
            raise
        
    def save_data(self):
        """Ukládá stažená data"""
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
                # obs
                geom_obs = ogr.Geometry(ogr.wkbPoint)
                geom_obs.AddPoint(feature.GetField("LonObs"),
                                  feature.GetField("LatObs"))
                # item
                geom_item = ogr.Geometry(ogr.wkbPoint)
                geom_item.AddPoint(feature.GetField("LonObs"),
                                   feature.GetField("LatObs"))
                
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
            f"Data exported to {self.driver_name}: {self.output_path}")

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
    osr.UseExceptions()
    load_dotenv(".env")
    hostname = os.environ.get("DB_HOST")
    database = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASS")
    query = os.environ.get("DB_QUERY")
    
    calculator = GeometryDistanceCalculator(
        'michalek', hostname, username, password)

    try:
        calculator.connect()
        calculator.fetch_data(query)
        calculator.save_data()
        calculator.calculate_distance()
    except Exception as ex:
        calculator.logger.error(ex)