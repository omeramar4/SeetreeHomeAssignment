import os
from utils.loaders import PandasCsvLoader, GeoPandasLoader


class ImagesMetadata(PandasCsvLoader):

    def __init__(self):
        super().__init__(path=os.path.join(os.getcwd(), 'data/images/'),
                         schema=['ImageName', 'latitude', 'longitude',
                                 'Z(High)', 'yaw', 'pitch', 'roll'])


class PolygonsLoader(GeoPandasLoader):

    def __init__(self):
        super().__init__(path=os.path.join(os.getcwd(), 'data/polygons/'),
                         schema=['createdAt', 'farmID', 'id', 'index', 'zone_id', 'geometry'])
