import functools
import utils.cache_manager as cm
from utils.metadata_loaders import ImagesMetadata, PolygonsLoader


def load_decorator(images: bool = False, polygons: bool = False):
    def decorator(f):
        @functools.wraps(f)
        def wrapper():
            if images and cm.images_cache is None:
                cm.images_cache = ImagesMetadata().load()
            if polygons and cm.polygons_cache is None:
                cm.polygons_cache = PolygonsLoader().load()
        return wrapper
    return decorator
