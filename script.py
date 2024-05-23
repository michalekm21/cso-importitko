#!/bin/env python3
import os
import logging
from osgeo import ogr
from mysql_export import DatabaseToShapefile
from vzdalenosti_app import GeometryDistanceCalculator
from dotenv import load_dotenv


def setup_logging():
    """Set up logging."""
    logger = logging.getLogger('LSDScript')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    logger = setup_logging()

    load_dotenv(".env")
    hostname = os.environ.get("DB_HOST")
    database = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASS")
    query = os.environ.get("DB_QUERY")

    db_to_shp = DatabaseToShapefile(
        hostname, database, username, password, logger
    )

    try:
        db_to_shp.connect()
        data_layer = db_to_shp.download_data(query)
    except Exception as e:
        logger.error(e)
        
    calculator = GeometryDistanceCalculator(
        dbname='michalek',
        host=hostname,
        user=username,
        password=password,
        table='project.LSD_Square'
    )

    calculator.connect()

    try:
        for feature in data_layer:
            obs_point = ogr.Geometry(ogr.wkbPoint)
            obs_point.AddPoint(feature.GetField("LatObs"),
                               feature.GetField("LonObs"))
            
            item_point = ogr.Geometry(ogr.wkbPoint)
            item_point.AddPoint(feature.GetField("LatItem"),
                                feature.GetField("LonItem"))
                        
            square = feature.GetField("SiteName").split("-")[0]
            pasmo = feature.GetField("SiteName").split("-")[2]
            v = feature.GetField("SiteName").split("-")[4]
            
            linie = calculator.fetch_data(pasmo, square)
            
            obs_distance = calculator.calculate_distance(
                linie[0].GetGeomFieldRef(0), obs_point)
            
            logger.info("dist %s", obs_distance)
    except Exception as e:
        logger.exception("Chyba při výpočtu bodu: %s", e)
        raise
    
    calculator.release()
   