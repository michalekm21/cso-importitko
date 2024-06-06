"""Nástroj pro výpočet vzdálenosti a export dat"""

import os
import warnings
import logging
from osgeo import osr, ogr
try:
    from halo import Halo
except ModuleNotFoundError:
    pass


os.environ['SHAPE_ENCODING'] = "utf-8"
osr.UseExceptions()


class GeometryDistanceCalculator:
    """Počítá vzdálenosti z Geometrie"""
    def __init__(self, database, hostname, username, password):
        self.dsn = (
            f"MYSQL:{database},host={hostname},user={username},"
            f"password={password},port=3306"
        )
        self.ds = None
        self.layer = None

        self.out_layer = None
        self.out_ds = None

        self.work_layer = None
        self.work_ds = None

        self.output_path = None
        self.driver_name = None

        # Nastavení logování
        logging.basicConfig(level=logging.WARNING,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Definice transformace na SRID 5514
        self.source_srs = osr.SpatialReference()
        self.source_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        # Předpokládáme, že původní souřadnice jsou ve WGS84
        self.source_srs.ImportFromEPSG(4326)

        self.target_srs = osr.SpatialReference()

        self.target_srs.ImportFromProj4(
            "+proj=krovak +lat_0=49.5 +lon_0=24.8333333333333 "
            "+alpha=30.2881397527778 +k=0.9999 +x_0=0 +y_0=0 +ellps=bessel "
            "+towgs84=570.8,85.7,462.8,4.998,1.587,5.261,3.56 +units=m "
            "+no_defs +type=crs"
        )

        self.transform = osr.CoordinateTransformation(
            self.source_srs, self.target_srs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def connect(self):
        """Připojení k DB"""
        spinner = Halo(text='Connecting to DB -', spinner='dots')
        spinner.start()
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.ds = ogr.Open(self.dsn, 0)
                if not self.ds:
                    self.logger.error("Nelze se připojit k databázi.")
                    raise ConnectionError("Nelze se připojit k databázi.")
                self.logger.info("Připojeno k databázi.")
                spinner.succeed("DB connected")
        except Exception as e:
            spinner.fail("Failed connecting to DB")
            self.logger.exception("Chyba při připojování k databázi: %s", e)
            raise

    def fetch_data(self, sql):
        """Stahuje data z DB"""
        spinner = Halo(text='Fetching data', spinner='dots')
        spinner.start()
        try:
            self.layer = self.ds.ExecuteSQL(sql)
            self.logger.info("Data načtena z databáze.")
            spinner.succeed("Data downloaded")
            return self.layer
        except Exception as e:
            spinner.fail("Fetching data failed")
            self.logger.exception("Chyba při načítání dat: %s", e)
            raise

    def load_layer(self):
        """Ukládá stažená data do mezipaměti"""
        spinner = Halo(text='Loading data', spinner='dots')
        spinner.start()

        try:
            driver = ogr.GetDriverByName('MEMORY')

            self.work_ds = driver.CreateDataSource('memData')
            self.work_layer = self.work_ds.CopyLayer(
                self.layer, self.layer.GetName())
            spinner.succeed("Data saved")
        except Exception as e:
            spinner.fail("Failed isaving the data to disk")
            self.logger.exception("Chyba při načtení ustažených dat: %s", e)
            raise

    def save_data(self, driver_name, output_path):
        """Ukládá stažená data"""
        spinner = Halo(text='Saving data', spinner='dots')
        spinner.start()
        self.driver_name = driver_name
        self.output_path = output_path
        try:
            driver = ogr.GetDriverByName(self.driver_name)
            if os.path.exists(self.output_path):
                driver.DeleteDataSource(self.output_path)

            self.out_ds = driver.CreateDataSource(self.output_path)
            self.out_layer = self.out_ds.CopyLayer(
                self.work_layer, self.layer.GetName())
            spinner.succeed("Data saved")
        except Exception as e:
            spinner.fail("Failed saving the data to disk")
            self.logger.exception("Chyba při ukládání ustažených dat: %s", e)
            raise
        finally:
            pass
            # self.release()

    def _calculate_distance(self):
        """ Počítá vzdálenost ze stažených dat"""
        spinner = Halo(text='Calculating the distances', spinner='dots')
        spinner.start()

        self.out_layer.CreateField(ogr.FieldDefn("obs2line", ogr.OFTReal))
        self.out_layer.CreateField(ogr.FieldDefn("item2line", ogr.OFTReal))
        self.out_layer.CreateField(ogr.FieldDefn("obs2item", ogr.OFTReal))

        try:
            for feature in self.out_layer:
                # Získání geometrií
                geom_l = feature.GetGeomFieldRef(0)
                if geom_l is None:
                    # print(feature.GetField("kfme"))
                    continue    # !!přeskočit pokud schází geometrie linie

                # obs
                geom_obs = ogr.Geometry(ogr.wkbPoint)
                geom_obs.AddPoint(float(feature.GetField("LonObs")),
                                  float(feature.GetField("LatObs")))
                # item
                geom_item = ogr.Geometry(ogr.wkbPoint)
                geom_item.AddPoint(float(feature.GetField("LonItem")),
                                   float(feature.GetField("LatItem")))

                # Transformace geometrií
                geom_l.Transform(self.transform)
                geom_obs.Transform(self.transform)
                geom_item.Transform(self.transform)

                # Výpočet vzdálenosti mezi linií a bodem
                obs2line = geom_l.Distance(geom_obs)
                item2line = geom_l.Distance(geom_item)
                obs2item = geom_item.Distance(geom_obs)

                feature.SetField('obs2line', obs2line)
                feature.SetField('item2line', item2line)
                feature.SetField('obs2item', obs2item)

                self.out_layer.SetFeature(feature)

                # self.logger.info(
                #     "Vzdálenost mezi obs a line: %s metrů", obs2line)

        except Exception as e:
            spinner.fail("Failed calculating the distances")
            self.logger.exception("Chyba při výpočtu vzdálenosti: %s", e)
            raise

        spinner.succeed("Distances calculated")
        del self.out_ds  # Finish and save data
        del self.out_layer
        self.logger.info(
            "Data exported to %s : %s ", self.driver_name, self.output_path)
        spinner.succeed(f"Data exported to {self.driver_name}")

    def calculate_distance(self):
        """ Počítá vzdálenost ze stažených dat"""
        spinner = Halo(text='Calculating the distances', spinner='dots')
        spinner.start()
        try:
            self.work_layer.CreateField(
                ogr.FieldDefn("obs2line", ogr.OFTReal))
            self.work_layer.CreateField(
                ogr.FieldDefn("item2line", ogr.OFTReal))
            self.work_layer.CreateField(
                ogr.FieldDefn("obs2item", ogr.OFTReal))
        except RuntimeError:
            self.logger.exception('Nezdařilo se přidat sloupce')

        try:
            for feature in self.work_layer:
                # Získání geometrií
                geom_l = feature.GetGeomFieldRef(0)
                if geom_l is None:
                    # print(feature.GetField("kfme"))
                    continue    # !!přeskočit pokud schází geometrie linie

                # obs
                geom_obs = ogr.Geometry(ogr.wkbPoint)
                geom_obs.AddPoint(float(feature.GetField("LonObs")),
                                  float(feature.GetField("LatObs")))
                # item
                geom_item = ogr.Geometry(ogr.wkbPoint)
                geom_item.AddPoint(float(feature.GetField("LonItem")),
                                   float(feature.GetField("LatItem")))

                # Transformace geometrií
                geom_l.Transform(self.transform)
                geom_obs.Transform(self.transform)
                geom_item.Transform(self.transform)

                # Výpočet vzdálenosti mezi linií a bodem
                obs2line = geom_l.Distance(geom_obs)
                item2line = geom_l.Distance(geom_item)
                obs2item = geom_item.Distance(geom_obs)

                feature.SetField('obs2line', obs2line)
                feature.SetField('item2line', item2line)
                feature.SetField('obs2item', obs2item)

                self.work_layer.SetFeature(feature)

                # self.logger.info(
                #     "Vzdálenost mezi obs a line: %s metrů", obs2line)

        except Exception as e:
            spinner.fail("Failed calculating the distances")
            self.logger.exception("Chyba při výpočtu vzdálenosti: %s", e)
            raise

        spinner.succeed("Distances calculated")

    def release(self):
        """Uvolnit připojení k DB"""
        spinner = Halo(text='Releasing the DB connection', spinner='dots')
        spinner.start()
        try:
            if self.layer:
                self.ds.ReleaseResultSet(self.layer)
                self.logger.info("Připojení k databázi bylo uzavřeno.")
                spinner.succeed("DB connection released")
        except Exception as e:
            spinner.fail("Failed releasing the connection")
            self.logger.exception("Chyba při uvolňování zdrojů: %s", e)
            raise

    def prepare_work_layer(self):
        """Připraví pracovní vrstvu"""
        # Získání názvu vrstvy
        layer_name = self.layer.GetName()

        # Vytvoření nového driveru pro paměťový datový zdroj
        driver = ogr.GetDriverByName('MEMORY')
        if driver is None:
            raise RuntimeError("OGR driver 'MEMORY' not available")

        # Vytvoření nového paměťového datového zdroje
        self.work_ds = driver.CreateDataSource('memData')
        if self.work_ds is None:
            raise RuntimeError("Failed to create data source")

        # Vytvoření nové vrstvy s typem geometrie 'wkbPoint'
        self.work_layer = self.work_ds.CreateLayer(
            layer_name, geom_type=ogr.wkbPoint)
        if self.work_layer is None:
            raise RuntimeError("Failed to create new layer")

        # Přidání stejných polí do nové vrstvy
        layer_defn = self.layer.GetLayerDefn()
        for i in range(layer_defn.GetFieldCount()):
            field_defn = layer_defn.GetFieldDefn(i)
            self.work_layer.CreateField(field_defn)

        spinner = Halo(text='Calculating the distances', spinner='dots')

        spinner.start()
        self.work_layer.CreateField(ogr.FieldDefn("obs2line", ogr.OFTReal))
        self.work_layer.CreateField(ogr.FieldDefn("item2line", ogr.OFTReal))
        self.work_layer.CreateField(ogr.FieldDefn("obs2item", ogr.OFTReal))

        # Přidání bodové geometrie do nové vrstvy
        try:
            for feature in self.layer:
                geom = feature.GetGeometryRef()
                if geom is None:
                    continue

                # Vytvoření nového prvku s bodovou geometrií
                new_feature = ogr.Feature(self.work_layer.GetLayerDefn())

                # Kopírování hodnot polí z původního prvku
                for i in range(feature.GetFieldCount()):
                    new_feature.SetField(i, feature.GetField(i))

                geom_l = feature.GetGeomFieldRef(0)
                if geom_l is None:
                    # print(feature.GetField("kfme"))
                    continue    # !!přeskočit pokud schází geometrie linie

                # obs
                geom_obs = ogr.Geometry(ogr.wkbPoint)
                geom_obs.AddPoint(float(feature.GetField("LonObs")),
                                  float(feature.GetField("LatObs")))
                # item
                geom_item = ogr.Geometry(ogr.wkbPoint)
                geom_item.AddPoint(float(feature.GetField("LonItem")),
                                   float(feature.GetField("LatItem")))

                # Transformace geometrií
                geom_l.Transform(self.transform)
                geom_obs.Transform(self.transform)
                geom_item.Transform(self.transform)

                # Výpočet vzdálenosti mezi linií a bodem
                obs2line = geom_l.Distance(geom_obs)
                item2line = geom_l.Distance(geom_item)
                obs2item = geom_item.Distance(geom_obs)

                new_feature.SetField('obs2line', obs2line)
                new_feature.SetField('item2line', item2line)
                new_feature.SetField('obs2item', obs2item)

                new_feature.SetGeometry(geom_item)

                self.logger.info(
                    "Vzdálenost mezi obs a line: %s metrů", obs2line)

                # Přidání nového prvku do nové vrstvy
                self.work_layer.CreateFeature(new_feature)
                new_feature = None

        except Exception as e:
            spinner.fail("Failed calculating the distances")
            self.logger.exception("Chyba při výpočtu vzdálenosti: %s", e)
            raise

        spinner.succeed(f"Data exported to {self.driver_name}")
