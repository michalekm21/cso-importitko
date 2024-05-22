#!/bin/env python3
"""Generate SQL query based on YAML config"""

import yaml
import argparse
import logging


class GenerateQuery:
    """Generate query based on YAML config"""
    def __init__(self, logger):
        self.logger = logger
        self.parser = None

    def load_config(self, path):
        """Gets Config from YAML"""
        with open(path, 'r', encoding="utf-8") as file:
            return yaml.safe_load(file)

    def create_parser(self, config):
        """Creates cmd line args"""
        self.parser = argparse.ArgumentParser(
            description='Run a SQL query based on provided parameters.')
        for param in config['parameters']:
            self.parser.add_argument(
                f"--{param['name']}", type=eval(param['type']),
                help=param['help'])
        return self.parser

    def add_to_parser(self, config, parser):
        """Creates cmd line args"""
        for param in config['parameters']:
            try:
                parser.add_argument(
                    f"--{param['name']}", type=eval(param['type']),
                    help=param['help'])
            except Exception as e:
                self.logger.error(e)

        return parser

    def build_query(self, config, args):
        """Creates SQL query based on YAML config"""
        conditions = []
        for param in config['parameters']:
            value = getattr(args, param['name'], None)
            if value is not None:
                if param['type'] == 'str':
                    conditions.append(f"{param['name']} = '{value}'")
                else:
                    conditions.append(f"{param['name']} = {value}")
        where_clause = " AND ".join(conditions)
        return config['query_template'].format(conditions=where_clause)


def setup_logging():
    """Set up logging."""
    logger = logging.getLogger('QueryBuilderLogger')
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
    generate_query = GenerateQuery(logger)
    config = generate_query.load_config('query_config.yaml')
    generate_query.create_parser(config)
    args = generate_query.parser.parse_args()
    query = generate_query.build_query(config, args)
    print(f"Generated Query: {query}")