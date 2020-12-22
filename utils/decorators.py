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
