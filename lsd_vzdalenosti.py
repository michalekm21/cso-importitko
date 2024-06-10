#!/bin/env python3
"""Aplikace pro výpočet LSD vzdálenosti pro příkazovou řádku"""

import os
import sys
import argparse
import yaml

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
    try:
        with open('login.yaml', 'r', encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        config = []

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

    # Parametry příkazu
    parser = argparse.ArgumentParser(
        description="Export LSD data with distances to SHP, GeoJSON and CSV.")
    # Kredence
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
    parser.add_argument("--user",
                        help="Filter by user's Name or e-mail - accepts regex")
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
                build_query(args.min_date, args.species,
                            args.square, args.limit, args.user))

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
        except RuntimeError as ex:
            calculator.logger.error(ex)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
