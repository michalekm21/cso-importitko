#!/usr/bin/env python3
"""Filter """

import argparse
from lsdImport.mongodump_reader import LSDMongoZipLocReader


def get_cmdline_args():
    """Adds args"""
    parser = argparse.ArgumentParser(
        description='Vyfiltruje ze zazipovaného json dumpu '
        + 'vybrané záznamy do csv')

    parser.add_argument(
        '-f', '--filename', required=True, help='mongo json dump v zip')
    parser.add_argument(
        '-o', '--output', required=True, help='výstup v CSV')

    args = parser.parse_args()

    return args


def main():
    """Main"""
    args = get_cmdline_args()

    rdr = LSDMongoZipLocReader(args.filename)
    rdr.save_data_csv(args.output, lambda x: x["path2"] is not None)


if __name__ == '__main__':
    main()
