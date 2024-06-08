#!/bin/env python3
"""Aplikace pro výpočet LSD vzdálenosti pro příkazovou řádku"""

import os
import sys
import argparse
import utils.lib.yaml as yaml

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass

from utils.distance_calculator import GeometryDistanceCalculator
from utils.query_builder import build_query


def main():
    """main"""
    # údaje z .env < config.yaml
    conf_hostname = None
    conf_database = None
    conf_username = None
    conf_password = None
    conf_query = None

    with open('config.yaml', 'r', encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if 'dotenv' in sys.modules:
        load_dotenv(".env")

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
    # group = parser.add_argument_group(required=True)
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
    # Filtr
    parser.add_argument("--min-date",
                        help="Filter by date - either Year or YYYY-MM-DD")
    parser.add_argument("--species", "-sp",
                        help="Filter by species name - either latin or czech")
    parser.add_argument("--square", "-sq",
                        help="Filter by KFME id - accepts regex")
    parser.add_argument("--limit", "-l",
                        help="Maximum number of records")
    # Výstup
    parser.add_argument("--shp-output", "-shp",
                        help="Path to output the SHP file.")
    parser.add_argument("--geojson-output", "-geojson",
                        help="Path to output the GeoJSON file.")
    parser.add_argument("--csv-output", "-csv",
                        help="Path to output the csv file.")

    args = parser.parse_args()

    if not (args.csv_output or args.geojson_output or args.csv_output):
        parser.error('Prosím, zadejte alespoň jeden výstupový soubor.')

    with GeometryDistanceCalculator(
            'michalek', args.hostname, args.username, args.password
            ) as calculator:

        try:
            calculator.connect()
            calculator.fetch_data(
                build_query(
                    conf_query, args.min_date,
                    args.species, args.square, args.limit))

            # calculator.load_layer()

            # calculator.calculate_distance()

            calculator.prepare_work_layer()

            if args.shp_output is not None:
                calculator.save_data("ESRI Shapefile",
                                     f"{args.shp_output}.shp")
            if args.geojson_output is not None:
                calculator.save_data("GeoJSON",
                                     f"{args.geojson_output}.geojson")
            if args.csv_output is not None:
                calculator.save_data("CSV",
                                     f"{args.csv_output}.csv")
            # calculator.calculate_distance()
        except RuntimeError as ex:
            calculator.logger.error(ex)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
