#!/bin/env python3
import argparse
import os
from osgeo import ogr
from dotenv import load_dotenv
import logging


class DatabaseToShapefile:
    def __init__(self, hostname, database, username, password, logger):
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password
        self.logger = logger

        self.connection_string = (
            f"MYSQL:{database},host={hostname},user={username},"
            f"password={password},port=3306"
        )
        self.conn = None

    def connect(self):
        """Connect to MariaDB using OGR."""
        self.conn = ogr.Open(self.connection_string)
        if self.conn is None:
            self.logger.error("Failed to connect to the database.")
            raise ConnectionError("Failed to connect to the database.")
        self.logger.info("Successfully connected to the database.")

    def download_data(self, sql_query):
        """Download data using an SQL query."""
        if self.conn is None:
            self.connect()

        layer = self.conn.ExecuteSQL(sql_query)
        if layer is None:
            self.logger.error(f"SQL query failed: {sql_query}")
            raise ValueError("SQL query returned no data.")
        self.logger.info("Data successfully downloaded.")
        return layer

    def export_to_shapefile(self, layer, output_path):
        """Export data to SHP file."""
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(output_path):
            driver.DeleteDataSource(output_path)

        out_ds = driver.CreateDataSource(output_path)
        out_layer = out_ds.CopyLayer(layer, layer.GetName())

        del out_ds  # Finish and save data
        self.logger.info(f"Data exported to SHP: {output_path}")

    def export_to_geojson(self, layer, output_path):
        """Export data to GeoJSON file."""
        driver = ogr.GetDriverByName('GeoJSON')
        if os.path.exists(output_path):
            os.remove(output_path)

        out_ds = driver.CreateDataSource(output_path)
        out_layer = out_ds.CopyLayer(layer, layer.GetName())

        del out_ds  # Finish and save data
        self.logger.info(f"Data exported to GeoJSON: {output_path}")


def setup_logging():
    """Set up logging."""
    logger = logging.getLogger('DatabaseToShapefileLogger')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def main():
    env = load_dotenv(".env")
    hostname = os.environ.get("DB_HOST")
    database = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASS")

    parser = argparse.ArgumentParser(description="Export data from MariaDB to SHP and GeoJSON.")
    parser.add_argument(
        "--hostname", required=True if hostname is None else False, default=hostname, help="Hostname of the MariaDB server.")
    parser.add_argument(
        "--database", required=True if database is None else False, default=database, help="Database name.")
    parser.add_argument(
        "--username", required=True if username is None else False, default=username, help="Username for the database.")
    parser.add_argument(
        "--password", required=True if password is None else False, default=password, help="Password for the database.")
    parser.add_argument(
        "--sql", required=True, help="SQL query to execute.")
    parser.add_argument(
        "--shp_output", required=True, help="Path to output the SHP file.")
    parser.add_argument(
        "--geojson_output", required=True, help="Path to output the GeoJSON file.")

    args = parser.parse_args()

    logger = setup_logging()

    db_to_shp = DatabaseToShapefile(
        args.hostname, args.database, args.username, args.password, logger
    )
    try:
        db_to_shp.connect()
        data_layer = db_to_shp.download_data(args.sql)
        db_to_shp.export_to_shapefile(data_layer, args.shp_output)
        db_to_shp.export_to_geojson(data_layer, args.geojson_output)
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
