from functools import wraps
import utils.cache_manager as cm
from utils.metadata_loaders import ImagesMetadata, PolygonsLoader


def load_decorator(images: bool = False, polygons: bool = False):
    """
        This decorator loads the images and polygons metadata files.
        If the requested file is already in the cache, the decorator skips its load.

        :param images: a flag indicates if the images metadata is required.
        :param polygons: a flag indicates if the polygons metadata is required.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if images and cm.images_cache is None:
                cm.images_cache = ImagesMetadata().load()
            if polygons and cm.polygons_cache is None:
                cm.polygons_cache = PolygonsLoader().load()
            return f(*args, **kwargs)
        return wrapper
    return decorator


def cache_decorator(image: bool = False, polygon: bool = False):
    """
        This decorator saves found elements (images or polygons) in
        the cache for future requests.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(name: str):
            cache_manager = None
            if image and not polygon:
                cache_manager = cm.PolygonCache()
            elif polygon and not image:
                cache_manager = cm.ImagesCache()

            if cache_manager is None:
                return f(name)

            if name in cache_manager.cached_ids.keys():
                ids = list(cache_manager.cached_ids[name])
                relevant_df = cache_manager.metadata_df.loc[cache_manager.metadata_df[cache_manager.id_col].isin(ids)]
                return relevant_df[cache_manager.return_cols]

            return_value = f(name)

            if len(return_value) > 0:
                if name not in cache_manager.cached_ids.keys():
                    cache_manager.cached_ids[name] = set()
                cache_manager.cached_ids[name] = (cache_manager.cached_ids[name]
                                                  .union(set(return_value[cache_manager.id_col])))
            else:
                if polygon:
                    cm.polygon_indexes_without_images.add(name)

            return return_value
        return wrapper
    return decorator
