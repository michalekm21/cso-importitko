#!/usr/bin/env python3
"""Reads mongo dump from zip"""

import json
import zipfile
# import os
# import logging
from csv import DictWriter
from datetime import datetime
from inspect import getsource
from lsdImport.tools import LoggerConfig
from osgeo import ogr


class LSDMongoZipLocReader:
    """Read zip dump from mongo db"""
    fields = ['_id',
              'key',
              'name',
              'square',
              'closed',
              # 'latitude',
              # 'longitude',
              # 'circleLat',
              # 'circleLon',
              'geom_p',
              'permissions',
              'created',
              'current',
              'path2',
              'path1',
              'projects',
              '__v',
              'geoLocationName',
              'locked',
              ]

    def __init__(self, zip_path):
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.zip_path = zip_path
        self.data = []
        self.load_data()

    def load_data(self, file='localities.json'):
        """Open zip file and extract json files"""
        archive = zipfile.ZipFile(self.zip_path)
        for r in archive.open(file):
            self.data.append(
                self.format_record(json.loads(r)))

        # Convert to pandas DataFrame if needed
        # self.data[filename] = pd.DataFrame(self.data[filename])

    def format_record(self, record):
        """Format record"""
        geom_p = None
        x = (record.get('latitude') or record.get('circleLat'))
        y = (record.get('longitude') or record.get('circleLon'))
        if x is not None and y is not None:
            geom_p = ogr.Geometry(ogr.wkbPoint)
            geom_p.FlattenTo2D()
            geom_p.AddPoint(x, y)

        return {
            '_id': record['_id'][r'$oid'],
            'key': record.get('key'),
            'name': record.get('name'),
            'square': record.get('square'),
            'closed': record.get('closed'),
            # 'latitude': record.get('latitude') or record.get('circleLat'),
            # 'longitude': record.get('longitude') or record.get('circleLon'),
            'geom_p': geom_p.ExportToWkt() if geom_p is not None else None,
            'permissions': record['permissions']['owners'][0],
            'created': datetime.fromisoformat(record['created']['$date']),
            'current': record.get('current'),
            'path2': self.create_line(record.get('path2')),
            'path1': self.create_line(record.get('path1')),
            'projects': record.get('projects'),
            '__v': record.get('__v'),
            'geoLocationName': record.get('geoLocationName'),
            'locked': record.get('locked'),
        }

    def create_line(self, path):
        """Creates line"""
        if path is None:
            self.logger.warning('Path není zadáno')
            return

        line = ogr.Geometry(ogr.wkbLineString)

        for pnt in path:
            line.AddPoint(pnt['longitude'],
                          pnt['latitude'])

        line.FlattenTo2D()

        return line.ExportToWkt()

    def filter_data(self, filter_function):
        """Filtr"""
        return filter(filter_function, self.data)

    def save_data_csv(self, filename, filter_function=None):
        """Save to CSV"""
        with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.fields)
            writer.writeheader()
            if filter_function is None:
                writer.writerows(self.data)
            else:
                try:
                    for r in self.filter_data(filter_function):
                        writer.writerow(r)
                except KeyError:
                    self.logger.exception(
                        "jeden z klíčů použitých ve funkci %s chybí",
                        getsource(filter_function))
                except BaseException:
                    self.logger.exception(
                        "filtrovací funkce %s selhala",
                        getsource(filter_function))
        return
