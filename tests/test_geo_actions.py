import pandas as pd
import geopandas as gpd
from unittest import TestCase
import utils.cache_manager as cm
from geo_logic import geo_actions
from shapely.geometry import Point, Polygon


class TestGeoActions(TestCase):

    _images = pd.DataFrame({'ImageName': ['A', 'B'],
                            'longitude': [24.976567, 24.952242],
                            'latitude': [60.1612500, 60.1696017]})

    _polygons = gpd.GeoDataFrame({'index': ['Poly1', 'Poly2'],
                                  'geometry': [Polygon([(24.950899, 60.169158),
                                                        (24.953492, 60.169158),
                                                        (24.953510, 60.170104),
                                                        (24.950958, 60.169990)]),
                                               Polygon([Point(0.5, 0), Point(1, 0),
                                                        Point(0, -1), Point(1, -1)])],
                                  'id': [1, 2],
                                  'farmID': ['farm', 'farm'],
                                  'zoneID': ['zone', 'zone']
                                  })

    def test_images_in_polygon(self):
        actual = geo_actions.images_in_polygon(Polygon([(24.950899, 60.169158),
                                                        (24.953492, 60.169158),
                                                        (24.953510, 60.170104),
                                                        (24.950958, 60.169990)]),
                                               self._images)
        expected = pd.DataFrame({'ImageName': ['B'],
                                 'longitude': [24.952242],
                                 'latitude': [60.1696017],
                                 'is_image_inside': [True]},
                                index=actual.index)

        self.assertTrue(actual.equals(expected))

    def test_get_images_from_polygon_id(self):
        cm.images_cache = self._images
        cm.polygons_cache = self._polygons

        actual = geo_actions.get_images_from_polygon_id('Poly1')
        expected = pd.DataFrame({'ImageName': ['B']}, index=actual.index)

        self.assertTrue(actual.equals(expected))

    def test_get_polygons_from_image_name(self):
        cm.images_cache = self._images
        cm.polygons_cache = self._polygons

        actual = geo_actions.get_polygons_from_image_name('B')
        expected = gpd.GeoDataFrame({'id': [1],
                                     'farmID': ['farm'],
                                     'index': ['Poly1'],
                                     'zoneID': ['zone']
                                     }, index=actual.index)
        self.assertTrue(actual.equals(expected))

        actual = geo_actions.get_polygons_from_image_name('A')
        self.assertEqual(len(actual), 0)

    def test_get_all_polygons(self):
        cm.images_cache = self._images
        cm.polygons_cache = self._polygons

        actual = geo_actions.at_least_one_image_in_polygon()
        expected = gpd.GeoDataFrame({'id': [1],
                                     'farmID': ['farm'],
                                     'index': ['Poly1'],
                                     'zoneID': ['zone']
                                     }, index=actual.index)
        self.assertTrue(actual.equals(expected))

