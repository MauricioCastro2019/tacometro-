import io
import os
import uuid

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}


def _resize_and_encode(file_storage, max_width=1200):
    """Resize to max_width and encode as JPEG or WebP. Returns (bytes, ext)."""
    from PIL import Image
    img = Image.open(file_storage)
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    if img.mode in ('RGBA', 'P'):
        img.save(buf, format='WEBP', quality=85)
        return buf.getvalue(), 'webp'
    img = img.convert('RGB')
    img.save(buf, format='JPEG', quality=85)
    return buf.getvalue(), 'jpg'


def upload_image(file_storage):
    """Upload an image. Returns URL string or None on failure.

    Priority: Cloudflare R2 > Cloudinary > local static/uploads/
    """
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return None

    r2_account_id = os.environ.get('R2_ACCOUNT_ID')
    r2_access_key = os.environ.get('R2_ACCESS_KEY_ID')
    r2_secret_key = os.environ.get('R2_SECRET_ACCESS_KEY')
    r2_bucket = os.environ.get('R2_BUCKET_NAME')

    if r2_account_id and r2_access_key and r2_secret_key and r2_bucket:
        try:
            import boto3
            from botocore.client import Config as BotocoreConfig

            s3 = boto3.client(
                's3',
                endpoint_url=f'https://{r2_account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=r2_access_key,
                aws_secret_access_key=r2_secret_key,
                config=BotocoreConfig(signature_version='s3v4'),
                region_name='auto',
            )

            image_bytes, out_ext = _resize_and_encode(file_storage)
            key = f"uploads/{uuid.uuid4().hex}.{out_ext}"
            content_type = 'image/webp' if out_ext == 'webp' else 'image/jpeg'

            s3.put_object(Bucket=r2_bucket, Key=key, Body=image_bytes, ContentType=content_type)

            public_url = os.environ.get('R2_PUBLIC_URL', '').rstrip('/')
            if public_url:
                return f"{public_url}/{key}"
            return f"https://{r2_bucket}.{r2_account_id}.r2.cloudflarestorage.com/{key}"
        except Exception:
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

    from flask import current_app
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.static_folder, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    file_storage.save(os.path.join(upload_dir, filename))
    return f"/static/uploads/{filename}"
