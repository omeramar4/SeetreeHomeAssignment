from utils import constants
from typing import List, Union
from geopandas import GeoDataFrame
from typing import Set, Optional, Dict
from pandas import DataFrame as PandasDataFrame


images_cache: Optional[PandasDataFrame] = None
polygons_cache: Optional[GeoDataFrame] = None
polygons_with_images: Optional[GeoDataFrame] = None

image_to_polygons: Dict[str, Set[str]] = dict()
polygon_to_images: Dict[str, Set[str]] = dict()
polygon_indexes_without_images: Set[str] = set()


class CacheManager:

    def __init__(self, name: str, id_col: str,
                 return_cols: Union[str, List[str]],
                 coords_cols: Union[str, List[str]],
                 metadata_df: Union[PandasDataFrame, GeoDataFrame],
                 cached_ids: Dict[str, Set[str]]):
        self.name = name
        self.id_col = id_col
        self.return_cols = return_cols
        self.coords_cols = coords_cols
        self.metadata_df = metadata_df
        self.cached_ids = cached_ids


class ImagesCache(CacheManager):

    def __init__(self):
        super().__init__(name='image',
                         id_col=constants.image_id_col,
                         return_cols=constants.images_return_schema,
                         coords_cols=constants.polygon_coords_cols,
                         metadata_df=images_cache,
                         cached_ids=polygon_to_images)


class PolygonCache(CacheManager):

    def __init__(self):
        super().__init__(name='polygon',
                         id_col=constants.polygon_id_col,
                         return_cols=constants.polygon_return_schema,
                         coords_cols=constants.polygon_coords_cols,
                         metadata_df=polygons_cache,
                         cached_ids=image_to_polygons)
