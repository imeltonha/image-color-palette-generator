from flask import Flask, render_template, url_for, send_from_directory
from flask_bootstrap import Bootstrap5
from flask_uploads import IMAGES, UploadSet, configure_uploads
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed
import os
from PIL import Image
from werkzeug.utils import secure_filename
from collections import Counter

# How to load image and display it: https://www.youtube.com/watch?v=dP-2NVUgh50

app = Flask(__name__)
bootstrap = Bootstrap5(app) # initialise bootstrap-flask
app.config["SECRET_KEY"] = os.urandom(24)
app.config["UPLOADED_PHOTOS_DEST"] = "uploads"

# create an UploadSet
photos = UploadSet("photos", IMAGES)
# configure Flask app and this extension
configure_uploads(app, photos)


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, message="Only images are allowed."),
                                  FileRequired(message="File field should not be empty.")]
                      )
    submit = SubmitField(label='Upload Image')


@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(directory=app.config["UPLOADED_PHOTOS_DEST"], path=filename)


@app.route('/', methods=["GET", "POST"])
def home():
    upload_form = UploadForm()

    if upload_form.validate_on_submit():
        filename = secure_filename(upload_form.photo.data.filename)
        file_path = photos.path(filename)
        upload_form.photo.data.save(file_path)

        # filename = photos.save(upload_form.photo.data)
        file_url = url_for('get_file', filename=filename)
        # print(f"filename: {filename}")
        # print(f"file_path: {file_path}")
        # print(f"file_url: {file_url}")

        if os.path.exists(file_path):
            # Open an image file and convert image to RGB (if not already in this mode)
            image = Image.open(file_path)
            image = image.convert('RGB')
            # Get pixel data
            pixels = list(image.getdata())
            # Get pixel amount
            pixel_count = len(pixels)
            # print(f"pixel_count: {pixel_count}")

            # Count the frequency of each color
            color_counts = Counter(pixels)
            # Get the 10 most common colors
            most_common_colors = color_counts.most_common(10)

            ## Display the results
            # for color, count in most_common_colors:
            #     print(f"Color: {color}, Count: {count}, Percentage: {round(count/len(pixels)*100, 2)}%")

        else:
            most_common_colors = None
            pixel_count = None
    else:
        file_url = None
        most_common_colors = None
        pixel_count = None
    return render_template('index.html', form=upload_form, file_url=file_url, most_common_colors=most_common_colors, pixel_count=pixel_count)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
