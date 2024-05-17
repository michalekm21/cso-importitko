#!/bin/env python3
"""Generate SQL query based on YAML config"""

import yaml
import argparse


def load_config(path):
    """Gets Config from YAML"""
    with open(path, 'r') as file:
        return yaml.safe_load(file)


def create_parser(config):
    """Creates cmd line args"""
    parser = argparse.ArgumentParser(
        description='Run a SQL query based on provided parameters.')
    for param in config['parameters']:
        parser.add_argument(
            f"--{param['name']}", type=eval(param['type']), help=param['help'])
    return parser


def build_query(config, args):
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


def main():
    """main"""
    config = load_config('query_config.yaml')
    parser = create_parser(config)
    args = parser.parse_args()
    query = build_query(config, args)
    print(f"Generated Query: {query}")


if __name__ == "__main__":
    main()
