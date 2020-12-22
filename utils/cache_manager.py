from typing import Set, Optional
from geopandas import GeoDataFrame
from pandas import DataFrame as PandasDataFrame


images_cache: Optional[PandasDataFrame] = None
polygons_cache: Optional[GeoDataFrame] = None
polygons_with_images: Optional[GeoDataFrame] = None

polygon_indexes_with_images: Set[str] = set()
polygon_indexes_without_images: Set[str] = set()
