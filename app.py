from flask import Flask, request
from utils.decorators import load_decorator
from geo_logic.geo_actions import get_images_from_polygon_id, \
    get_polygons_from_image_name, at_least_one_image_in_polygon


app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/load_images', methods=['GET'])
@load_decorator(images=True)
def load_images():
    return 'Images metadata file was loaded successfully'


@app.route('/load_polygons', methods=['GET'])
@load_decorator(polygons=True)
def load_polygons():
    return 'Polygons metadata file was loaded successfully'


@app.route('/get_polygons', methods=['GET', 'POST'])
@load_decorator(images=True, polygons=True)
def get_polygon():
    image_name = request.args.get('image_name')
    containing_polygons = get_polygons_from_image_name(image_name)
    if containing_polygons is None:
        return f'No image {image_name} in images metadata'
    return f"{containing_polygons.to_html()}"


@app.route('/get_images', methods=['GET', 'POST'])
@load_decorator(images=True, polygons=True)
def get_images():
    polygon_name = request.args.get('polygon_name')
    images_within = get_images_from_polygon_id(polygon_name)
    if images_within is None:
        return f'No polygon {polygon_name} in polygons metadata'
    return f"{images_within.to_html()}"


@app.route('/get_all_polygons', methods=['GET', 'POST'])
@load_decorator(images=True, polygons=True)
def get_all_polygons():
    polygons_with_at_least_one_image = at_least_one_image_in_polygon()
    return f"{polygons_with_at_least_one_image.to_html()}"


if __name__ == '__main__':
    app.run()
