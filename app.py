from flask import Flask, request, url_for
from utils.decorators import load_decorator
from geo_logic.geo_actions import get_images_from_polygon_id, \
    get_polygons_from_image_name, at_least_one_image_in_polygon, polygons_in_images


app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def home():
    messages = [
        f"<h1>SeeTree Home Assignment REST API</h1>"
        f"This page describes all accessible endpoint provided by this REST API",

        f"<h2>General Info</h2>"
        f"<h3>Actions on images and polygons</h3>"

        "<h2>Available Endpoints</h2>"
    ]

    # describe all available endpoints
    for rule in app.url_map.iter_rules():
        if ('GET' in rule.methods or 'POST' in rule.methods) and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            func = globals().get(rule.endpoint)
            doc = getattr(func, '__doc__')
            msg = f"""
                    <b><u>{url}</u></b>
                    <b>Function name:</b> {rule.endpoint}
                    <b>Accepted methods:</b> {', '.join(rule.methods)}
                    <b>Docstring:</b> {doc}
                """.replace('\n', '<br>')
            messages.append(msg)
    return '<br>'.join(messages)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route('/load_images', methods=['GET'])
@load_decorator(images=True)
def load_images():
    """
        Loading the image metadata csv to pandas dataframe and store it in the app cache.
        If the cache already holds this data then the loading is skipped.
    """
    return '<h1>Images metadata file was loaded successfully<h1>'


@app.route('/load_polygons', methods=['GET'])
@load_decorator(polygons=True)
def load_polygons():
    """
        Loading the polygon metadata csv to geopandas dataframe and store it in the app cache.
        If the cache already holds this data then the loading is skipped.
    """
    return '<h1>Polygons metadata file was loaded successfully<h1>'


@app.route('/get_polygons', methods=['GET', 'POST'])
@load_decorator(images=True, polygons=True)
def get_polygons():
    """
        Get all polygons containing a given image.
        :param: image name.
        :return: geopandas dataframe of all polygons in a polygons output format.
    """
    image_name = request.args.get('image_name')
    containing_polygons = get_polygons_from_image_name(image_name)
    if containing_polygons is None:
        return f'No image {image_name} in images metadata'
    num_of_polygons = len(containing_polygons)
    return f"<h1>Found {num_of_polygons} polygon{'s' if num_of_polygons == 1 else ''} " \
           f"containing image {image_name}</h1>"\
           f"{containing_polygons.to_html() if num_of_polygons else ''}"


@app.route('/get_images', methods=['GET', 'POST'])
@load_decorator(images=True, polygons=True)
def get_images():
    """
        Get all images inside a given polygon index.
        :param: image name (index).
        :return: pandas dataframe of all images in an images output format.
    """
    polygon_name = request.args.get('polygon_name')
    images_within = get_images_from_polygon_id(polygon_name)
    if images_within is None:
        return f'No polygon {polygon_name} in polygons metadata'
    num_of_images = len(images_within)
    return f"<h1>Found {num_of_images} image{'s' if num_of_images == 1 else ''} " \
           f"inside polygon {polygon_name}</h1>"\
           f"{images_within.to_html() if num_of_images else ''}"


@app.route('/get_all_polygons', methods=['GET', 'POST'])
@load_decorator(images=True, polygons=True)
def get_all_polygons():
    """
        Get all polygons containing at least one image.
    """
    polygons_with_at_least_one_image = at_least_one_image_in_polygon()
    num_of_polygons = len(polygons_with_at_least_one_image)
    return f"<h1>Found {num_of_polygons} polygons containing at least one image</h1>"\
           f"{polygons_with_at_least_one_image.to_html() if num_of_polygons else ''}"


if __name__ == '__main__':
    app.run()
