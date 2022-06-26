import os
import secrets
from PIL import Image
from flask import current_app
from flask_login import current_user
from werkzeug.utils import secure_filename



def save_image(user, form_image):
    user_avatar_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], str(user.id))

    # define access rights
    access_rights = 0o755

    if not os.path.exists(user_avatar_folder):
        os.makedirs(user_avatar_folder, access_rights)

    random_hex = secrets.token_hex(12)
    fn, f_ext = os.path.splitext(secure_filename(form_image.filename))
    image_fn = random_hex + f_ext
    image_path = os.path.join(user_avatar_folder, image_fn)
    output_size = (50, 50)
    img = Image.open(form_image)
    img.thumbnail(output_size)
    img.save(image_path)

    return image_fn
