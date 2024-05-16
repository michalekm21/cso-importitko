#!/usr/bin/env python3
from lsdImport.mongodumpReader import LSDMongoZipLocReader
import argparse


def get_cmdline_args():
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
    args = get_cmdline_args()

    rdr = LSDMongoZipLocReader(args.filename)
    rdr.save_data_csv(args.output, lambda x: x["geom_p"] is not None)


if __name__ == '__main__':
    main()
