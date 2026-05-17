import os
import uuid

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def upload_file_to_supabase(
    local_file_path,
    original_filename
):

    unique_filename = (
        f"{uuid.uuid4()}_{original_filename}"
    )

    with open(local_file_path, "rb") as f:
        file_bytes = f.read()
        print("PDF SIZE:", len(file_bytes))
        
        supabase.storage.from_(
            "documents"
        ).upload(

            path=unique_filename,

            file=file_bytes,

            file_options={
                "content-type": "application/pdf",
                "upsert": "true"
            }

        )

    public_url = supabase.storage.from_(
        "documents"
    ).get_public_url(
        unique_filename
    )

    return public_url