from flask import Flask, send_file, request, abort
from flask_swagger_ui import get_swaggerui_blueprint
from PIL import Image
from io import BytesIO
import base64
from requests import get
import os
import zipfile
from time import strftime, localtime
from flask_httpauth import HTTPBasicAuth


app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify(username, password):
    if (username in user) and (user[username] == password):
        return username

user = {"user": "password"}

SWAGGER_URL = '/swagger'
API_URL = r'/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "watermark"
    },
)
app.register_blueprint(swaggerui_blueprint)
margin_size = 20 # Index is pixels

def is_valid_image(file):
    try:
        Image.open(file)
        return True
    except Exception :
        return False


@app.route("/photo/upload/downLeft", methods=["POST"])
@auth.login_required
def upload():
    file = request.files["image"]
    
    if not is_valid_image(file):
        print("Uploaded file is not an image")

    main_image = Image.open(file)
    watermark = Image.open("watermark.png")
    watermark_width = int(.2 * main_image.size[0])
    watermark_height = int(watermark_width * .28)
    
    watermark_size = (watermark_width, watermark_height)

    watermark = watermark.resize(watermark_size)

    position = (margin_size, main_image.size[1] - watermark.size[1] - margin_size)

    main_image.paste(watermark, position, mask=watermark)

    output_buffer = BytesIO()
    main_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)

    return send_file(output_buffer, mimetype="image/png")


@app.route('/photos/upload/downLeft', methods=['POST'])
@auth.login_required
def upload_photos():
    watermark = Image.open("watermark.png")
    images = []

    image_files = request.files.getlist('files')

    for image_file in image_files:

        if not is_valid_image(image_file):
            print("Uploaded file is not an image")
            continue

        main_image = Image.open(image_file)
        filename = image_file.filename
        image_format = filename.split('.')[-1]

        watermark_width = int(.2 * main_image.size[0])
        watermark_height = int(watermark_width * .28)
        watermark_size = (watermark_width, watermark_height)

        watermark = watermark.resize(watermark_size)

        position = (margin_size, main_image.size[1] - watermark.size[1] - margin_size)

        main_image.paste(watermark, position, mask=watermark)

        output_buffer = BytesIO()

        if image_format.lower() == "jpg":
            image_format = 'jpeg'

        main_image.save(output_buffer, format=image_format.upper())
        output_buffer.seek(0)
        images.append((filename, output_buffer))

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for image in images:
            zip_file.writestr(image[0], image[-1].getvalue())

    zip_buffer.seek(0)

    current_time = strftime("%H,%M,%S", localtime())
    zip_name = f"{current_time}.zip"

    with open(zip_name, 'wb') as file:
        file.write(zip_buffer.getvalue())

    return send_file(zip_name, mimetype='application/zip', as_attachment=True)


@app.route("/photo/upload/center", methods=["POST"])
@auth.login_required
def upload_center():
    file = request.files["image"]
    
    if not is_valid_image(file):
        print("Uploaded file is not an image")

    main_image = Image.open(file)
    watermark = Image.open("watermark.png")
    watermark_width = int(.2 * main_image.size[0])
    watermark_height = int(watermark_width * .28)
    
    watermark_size = (watermark_width, watermark_height)

    watermark = watermark.resize(watermark_size)

    margin_size = int(main_image.size[1] * .1)

    position = ((int(main_image.size[0] * .5) - int(watermark_size[0] * .6)), main_image.size[1] - watermark.size[1] - margin_size)

    main_image.paste(watermark, position, mask=watermark)

    output_buffer = BytesIO()
    main_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)

    return send_file(output_buffer, mimetype="image/png")

@app.route('/photos/upload/center', methods=['POST'])
@auth.login_required
def upload_photos_center():
    watermark = Image.open("watermark.png")
    images = []

    image_files = request.files.getlist('files')

    for image_file in image_files:

        if not is_valid_image(image_file):
            print("Uploaded file is not an image")
            continue

        main_image = Image.open(image_file)
        filename = image_file.filename
        image_format = filename.split('.')[-1]

        watermark_width = int(.2 * main_image.size[0])
        watermark_height = int(watermark_width * .28)
        watermark_size = (watermark_width, watermark_height)

        margin_size = int(main_image.size[1] * .1)

        watermark = watermark.resize(watermark_size)

        position = ((int(main_image.size[0] * .5) - int(watermark_size[0] * .6)), main_image.size[1] - watermark.size[1] - margin_size)

        main_image.paste(watermark, position, mask=watermark)

        output_buffer = BytesIO()

        if image_format.lower() == "jpg":
            image_format = 'jpeg'

        main_image.save(output_buffer, format=image_format.upper())
        output_buffer.seek(0)
        images.append((filename, output_buffer))

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for image in images:
            zip_file.writestr(image[0], image[-1].getvalue())

    zip_buffer.seek(0)

    current_time = strftime("%H,%M,%S", localtime())
    zip_name = f"{current_time}.zip"

    with open(zip_name, 'wb') as file:
        file.write(zip_buffer.getvalue())

    return send_file(zip_name, mimetype='application/zip', as_attachment=True)

if __name__ == "__main__":
    app.run()