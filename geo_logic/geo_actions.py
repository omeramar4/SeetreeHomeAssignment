import pandas as pd
from typing import Optional
from utils import constants
from functools import reduce
import utils.cache_manager as cm
from geopandas import GeoDataFrame
from shapely.geometry import Point, Polygon
from pandas import DataFrame as PandasDataFrame


def images_in_polygon(polygon: Polygon) -> PandasDataFrame:
    """
        Get image rows inside a given polygon.

        :param polygon: The polygon index in which the images are searched.

        :return: pandas dataframe of all relevant image rows
    """
    cm.images_cache['is_image_inside'] = (cm.images_cache[constants.image_coords_cols]
                                          .apply(lambda coords: polygon.contains(Point(*coords)), axis=1))
    return cm.images_cache[cm.images_cache['is_image_inside']]


def get_images_from_polygon_id(polygon_id: str) -> Optional[PandasDataFrame]:
    """
        Get images rows inside a given polygon.
        This function stores the polygons found for future use.

        :param polygon_id: The polygon index in which the images are searched.

        :return: pandas dataframe of all relevant image rows. If the polygon index is
                 not in the polygons metadata, the function returns None.
    """
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
    """
        Get polygon rows containing a given image.
        This function stores the polygons found for future use.

        :param image_name: The image name for which the containing polygons are searched.

        :return: geopandas dataframe of all relevant polygon rows. If the image name is
                 not in the images metadata, the function returns None.
    """

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
    """
        Get all polygon which have at least one image inside.
        The function computes the number of images inside every polygon and return
        all polygon with numbre_of_images > 0.

        :return: geopandas dataframe of all polygons with at least one image inside.
    """
    if cm.polygons_with_images is not None:
        return cm.polygons_with_images

    checked_polygons = list(cm.polygon_indexes_with_images.union(cm.polygon_indexes_without_images))
    not_checked_polygons = cm.polygons_cache[~cm.polygons_cache[constants.polygon_id_col].isin(checked_polygons)]
    not_checked_polygons['number_of_images_inside'] = (not_checked_polygons[constants.polygon_coords_cols]
                                                       .apply(lambda poly: len(images_in_polygon(poly))))
    non_empty_polygons = not_checked_polygons.loc[not_checked_polygons['number_of_images_inside'] > 0]

    polygons_indexes_with_images = list(cm.polygon_indexes_with_images)
    if polygons_indexes_with_images:
        non_empty_polygons = pd.DataFrame(non_empty_polygons)
        checked_non_empty_polygons = pd.DataFrame(cm.polygons_cache[cm.polygons_cache[constants.polygon_id_col]
                                                  .isin(polygons_indexes_with_images)])
        non_empty_polygons = GeoDataFrame(pd.concat([non_empty_polygons, checked_non_empty_polygons]))

    cm.polygons_with_images = non_empty_polygons[constants.polygon_return_schema]
    return cm.polygons_with_images


def polygons_in_images():
    """
        Get all polygon which have at least one image inside.
        The function iterates through every image and finds the polygons containing it.
        At each iteration, the found polygon indices are stored and removed from the
        searched data for the following iterations.

        :return: geopandas dataframe of all polygons with at least one image inside.
    """
    polygons_found = set()
    num_of_polygons = len(cm.polygons_cache)
    polygons_data = cm.polygons_cache
    for _, image in cm.images_cache.iterrows():
        image_coords = Point(*image[constants.image_coords_cols].values)
        polygons_data['is_polygon_contains'] = (polygons_data[constants.polygon_coords_cols]
                                                .apply(lambda poly: image_coords.within(poly)))
        polygons_contains = polygons_data[polygons_data['is_polygon_contains']]
        polygons_found = polygons_found.union(set(polygons_contains[constants.polygon_id_col]))
        polygons_data = polygons_data[~polygons_data[constants.polygon_id_col].isin(list(polygons_found))]
        if len(polygons_found) == num_of_polygons:
            break
    polygons_to_return = cm.polygons_cache[cm.polygons_cache[constants.polygon_id_col].isin(polygons_found)]
    return polygons_to_return[constants.polygon_return_schema]


def remove_images_inside_at_least_one_polygon():
    """
        Unions all polygons and filter out images that don't appear in the union.

        :return: pandas dataframe of imaged inside at least one polygon.
    """
    merged_polygon = reduce(lambda p1, p2: p1.union(p2),
                            cm.polygons_cache[constants.polygon_coords_cols])
    return images_in_polygon(merged_polygon)
