from typing import Optional
from utils import constants
import utils.cache_manager as cm
from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon
from pandas import DataFrame as PandasDataFrame

# 1/401
# 1/403
# 1/302
#
# 1/506
# 1/109
# 1/111

def images_in_polygon(polygon: Polygon) -> PandasDataFrame:
    cm.images_cache['is_image_inside'] = (cm.images_cache[constants.image_coords_cols]
                                          .apply(lambda coords: polygon.contains(Point(*coords)), axis=1))
    return cm.images_cache[cm.images_cache['is_image_inside']]


def get_images_from_polygon_id(polygon_id: str) -> Optional[PandasDataFrame]:
    polygon_row = cm.polygons_cache.loc[cm.polygons_cache[constants.polygon_id_col] == polygon_id]
    if polygon_row.empty:
        return
    polygon = Polygon(*polygon_row[constants.polygon_coords_cols].values)
    images_within = images_in_polygon(polygon)
    return images_within[constants.images_return_schema]


def get_polygons_from_image_name(image_name: str) -> Optional[GeoDataFrame]:
    image_row = cm.images_cache.loc[cm.images_cache[constants.image_id_col] == image_name]
    if image_row.empty:
        return
    image_coords = Point(*image_row[constants.image_coords_cols].values)
    cm.polygons_cache['is_polygon_contains'] = (cm.polygons_cache[constants.polygon_coords_cols]
                                                .apply(lambda poly: image_coords.within(poly)))
    polygons_of_point = cm.polygons_cache[cm.polygons_cache['is_polygon_contains']]
    return polygons_of_point[constants.polygon_return_schema]


def at_least_one_image_in_polygon() -> GeoDataFrame:
    all_polygons = cm.polygons_cache
    all_polygons['number of images inside'] = (all_polygons[constants.polygon_coords_cols]
                                               .apply(lambda poly: len(images_in_polygon(poly))))
    non_empty_polygons = all_polygons.loc[all_polygons['number of images inside'] > 0]
    return non_empty_polygons[constants.polygon_return_schema]
