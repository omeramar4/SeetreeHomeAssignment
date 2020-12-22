import pandas as pd
from typing import Optional
from utils import constants
import utils.cache_manager as cm
from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon
from pandas import DataFrame as PandasDataFrame


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

    if len(images_within) > 0:
        cm.polygon_indexes_with_images.add(polygon_id)
    else:
        cm.polygon_indexes_without_images.add(polygon_id)

    return images_within[constants.images_return_schema]


def get_polygons_from_image_name(image_name: str) -> Optional[GeoDataFrame]:
    image_row = cm.images_cache.loc[cm.images_cache[constants.image_id_col] == image_name]
    if image_row.empty:
        return
    image_coords = Point(*image_row[constants.image_coords_cols].values)
    cm.polygons_cache['is_polygon_contains'] = (cm.polygons_cache[constants.polygon_coords_cols]
                                                .apply(lambda poly: image_coords.within(poly)))
    polygons_of_point = cm.polygons_cache[cm.polygons_cache['is_polygon_contains']]
    cm.polygon_indexes_with_images = (cm.polygon_indexes_with_images
                                      .union(set(polygons_of_point[constants.polygon_id_col])))

    return polygons_of_point[constants.polygon_return_schema]


def at_least_one_image_in_polygon() -> GeoDataFrame:
    if cm.polygons_with_images is not None:
        return cm.polygons_with_images

    checked_polygons = list(cm.polygon_indexes_with_images.union(cm.polygon_indexes_without_images))
    not_checked_polygons = cm.polygons_cache[~cm.polygons_cache[constants.polygon_id_col].isin(checked_polygons)]
    not_checked_polygons['number of images inside'] = (not_checked_polygons[constants.polygon_coords_cols]
                                                       .apply(lambda poly: len(images_in_polygon(poly))))
    non_empty_polygons = not_checked_polygons.loc[not_checked_polygons['number of images inside'] > 0]

    polygons_indexes_with_images = list(cm.polygon_indexes_with_images)
    if polygons_indexes_with_images:
        non_empty_polygons = pd.DataFrame(non_empty_polygons)
        checked_non_empty_polygons = pd.DataFrame(cm.polygons_cache[cm.polygons_cache[constants.polygon_id_col]
                                                  .isin(polygons_indexes_with_images)])
        non_empty_polygons = GeoDataFrame(pd.concat([non_empty_polygons, checked_non_empty_polygons]))

    cm.polygons_with_images = non_empty_polygons[constants.polygon_return_schema]
    return cm.polygons_with_images
