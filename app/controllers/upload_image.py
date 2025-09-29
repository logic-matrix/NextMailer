import os
from werkzeug.utils import secure_filename
from app.models import Uploads  
from app.extensions import db

UPLOAD_FOLDER = "app/static/images"

def save_image(file):
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        file.save(filepath)

        upload = Uploads(filename=filename, filepath=filepath)
        db.session.add(upload)
        db.session.commit()

        return upload
    return None
