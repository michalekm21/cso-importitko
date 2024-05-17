#!/usr/bin/env python3
from osgeo import ogr
import json
import argparse
import logging
import csv

class LSDError(Exception):
    """Ukázka chyby

    Attributes:
        param -- nejakej atr
        message -- explanation of the error
    """

    def __init__(self, jvffile, message = "Čtení vstupního souboru selhalo"):
        self.param = param
        self.message = f"Čtení vstupního souboru {param} selhalo"
        super().__init__(self.message)

class mariadb_connect:
    def __init__(self, conn):
        self.conn = conn
        self.cur = conn.cursor()
        return

    def get_birds(self, linenum, linegeom = None, maxdist = None):
        """
        vrátí ptáky podle zadaných kritérií
        """
        self.cur.execute(f"SELECT * FROM birds where linenum = '{linenum}'")

        for r in self.cur:
            yield r

def generuj_vystup():
    dwr = csv.DictWriter(....)
    mdbc = mariadb_connect(...)

    for l in dwr.get_records(filtr):
        lnm = l['linenum']
        drw.writerows(mdbc.get_birds(linenum))


