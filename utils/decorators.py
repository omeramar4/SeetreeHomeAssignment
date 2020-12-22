from functools import wraps
import utils.cache_manager as cm
from utils.metadata_loaders import ImagesMetadata, PolygonsLoader


def load_decorator(images: bool = False, polygons: bool = False):
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
