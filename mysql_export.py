#!/bin/env python3
"""Export from mysql"""

import argparse
import os
import logging
from query_app import GenerateQuery
from osgeo import ogr
from dotenv import load_dotenv


class DatabaseToShapefile:
    """Convert data from Database"""
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
        del out_layer
        self.logger.info(f"Data exported to SHP: {output_path}")

    def export_to_geojson(self, layer, output_path):
        """Export data to GeoJSON file."""
        driver = ogr.GetDriverByName('GeoJSON')
        if os.path.exists(output_path):
            os.remove(output_path)

        out_ds = driver.CreateDataSource(output_path)
        out_layer = out_ds.CopyLayer(layer, layer.GetName())

        del out_ds  # Finish and save data
        del out_layer
        self.logger.info(f"Data exported to GeoJSON: {output_path}")


def setup_logging():
    """Set up logging."""
    logger = logging.getLogger('DatabaseToShapefileLogger')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def main():
    """main function"""
    logger = setup_logging()

    load_dotenv(".env")
    hostname = os.environ.get("DB_HOST")
    database = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASS")
    query = os.environ.get("DB_QUERY")

    # query_app = GenerateQuery(logger)
    # query_config = query_app.load_config('query_config.yaml')

    parser = argparse.ArgumentParser(
        description="Export data from MariaDB to SHP and GeoJSON.")
    # group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("--hostname",
                        required=True if hostname is None else False,
                        default=hostname, help="Hostname of the MariaDB server.")
    parser.add_argument("--database",
                        required=True if database is None else False,
                        default=database, help="Database name.")
    parser.add_argument("--username",
                        required=True if username is None else False,
                        default=username, help="Username for the database.")
    parser.add_argument("--password",
                        required=True if password is None else False,
                        default=password, help="Password for the database.")
    parser.add_argument("--sql",
                        required=True if query is None else False, 
                        default=query, help="SQL query to execute.")
    parser.add_argument("--output", "-o",
                        required=True, help="Path to output the SHP file.")
    # group.add_argument(
    #     "--geojson_output", help="Path to output the GeoJSON file.")

    # parser = query_app.add_to_parser(query_config, parser)

    args = parser.parse_args()

    db_to_shp = DatabaseToShapefile(
        args.hostname, args.database, args.username, args.password, logger
    )

    # query = args.sql if args.sql is not None else query_app.build_query(
    #   query_config, args)
    try:
        db_to_shp.connect()
        data_layer = db_to_shp.download_data(args.sql)
        print(data_layer)
        if args.shp_output is not None:
            db_to_shp.export_to_shapefile(data_layer, args.shp_output)
        if args.geojson_output is not None:
            db_to_shp.export_to_geojson(data_layer, args.geojson_output)
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
