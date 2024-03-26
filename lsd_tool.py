#!/usr/bin/env python3
import re
from osgeo import ogr
import json
import argparse
import pymongo
import logging
import mariadb ## možná bude snazší to tahat přes ogr
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

class mongo_conn:

    def __init__(self, **kwargs):
        connstring = ', '.join(
                [
                    k+'='+v for k, v in kwargs if k in (
                        'dbname',
                        'username',
                        'port',
                        'passwor',
                        'host',
                        #....
                        )])

                
        # conn možná hodíme ven a bude to parametr
        try:
            self.conn = None
        except:
            self.logger.exception('Nepovedlo se připojit do db')

    def set_filter(self, query, **kvargs):
        """
        nastav filtr
        """
        pass

    def get_records(self):
        """
        generátor záznamů
        """
        for r in ():
            yield self.format_rec(r)

    def format_rec(self, rec):
        """
        udělá z rekordu pyobjekt
        """
        return 

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

def generuj_vystup(
        ....):
    dwr = csv.DictWriter(....)
    mgc = mongo_conn(...)
    mdbc = mariadb_connect(...)

    for l in dwr.get_records(filtr):
        lnm = l['linenum']
        drw.writerows(mdbc.get_birds(linenum))


