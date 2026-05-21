import os
import uuid
import mimetypes

from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
print("SUPABASE URL:", SUPABASE_URL)
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# PDF UPLOAD
# PDF UPLOAD
def upload_file_to_supabase(
    local_file_path,
    original_filename
):

    unique_filename = (
        f"{uuid.uuid4()}_{original_filename}"
    )

    mime_type = mimetypes.guess_type(
        original_filename
    )[0] or "application/pdf"

    with open(local_file_path, "rb") as f:

        file_bytes = f.read()

    supabase.storage.from_(
        "documents"
    ).upload(

        path=unique_filename,

        file=file_bytes,

        file_options={
            "content-type": mime_type
        }

    )

    public_url = supabase.storage.from_(
        "documents"
    ).get_public_url(
        unique_filename
    )

    return public_url

# ATTEMPT PHOTO UPLOAD
def upload_attempt_photo_to_supabase(
    local_file_path,
    original_filename
):

    unique_filename = (
        f"{uuid.uuid4()}_{original_filename}"
    )

    mime_type = mimetypes.guess_type(
        original_filename
    )[0] or "image/png"

    with open(local_file_path, "rb") as f:

        file_bytes = f.read()

    supabase.storage.from_(
        "attempt-photos"
    ).upload(

        path=unique_filename,

        file=file_bytes,

        file_options={
            "content-type": mime_type
        }

    )

    public_url = supabase.storage.from_(
        "attempt-photos"
    ).get_public_url(
        unique_filename
    )

    return public_url

# AFFIDAVIT PDF UPLOAD
def upload_affidavit_to_supabase(
    local_file_path,
    original_filename
):

    unique_filename = (
        f"{uuid.uuid4()}_{original_filename}"
    )

    with open(local_file_path, "rb") as f:

        file_bytes = f.read()

    supabase.storage.from_(
        "affidavits"
    ).upload(

        path=unique_filename,

        file=file_bytes,

        file_options={
            "content-type": "application/pdf"
        }

    )

    public_url = supabase.storage.from_(
        "affidavits"
    ).get_public_url(
        unique_filename
    )

    return public_url