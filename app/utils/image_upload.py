import os
import uuid

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}


def upload_image(file_storage):
    """Upload an image file. Returns URL string or None on failure.

    Uses Cloudinary if CLOUDINARY_URL env var is set, otherwise saves to static/uploads/.
    Note: static/uploads/ is ephemeral on Railway — configure Cloudinary for production.
    """
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return None

    if os.environ.get('CLOUDINARY_URL'):
        try:
            import cloudinary.uploader
            result = cloudinary.uploader.upload(
                file_storage,
                folder='tacometro',
                transformation=[{'width': 1200, 'crop': 'limit', 'quality': 'auto', 'fetch_format': 'auto'}]
            )
            return result['secure_url']
        except Exception:
            return None
    else:
        from flask import current_app
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_dir = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_storage.save(os.path.join(upload_dir, filename))
        return f"/static/uploads/{filename}"
