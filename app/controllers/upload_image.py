import os
from werkzeug.utils import secure_filename
from flask import url_for
from app.models import Uploads  
from app.extensions import db

UPLOAD_FOLDER = "app/static/images"

def save_image(file, name):
    if file:

        filename = name if name else secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        file.save(filepath)

        # Build URL accessible from browser
        file_url = url_for("static", filename=f"images/{filename}", _external=True)

        upload = Uploads(filename=filename, filepath=file_url)
        db.session.add(upload)
        db.session.commit()

        return upload
    return None
