import email
from email import policy
import os

UPLOAD_DIR = "temp_files"


def read_email(file_path):
    if not os.path.exists(file_path):
        raise Exception(f"Email file not found: {file_path}")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    with open(file_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    body = ""
    attachments = []

    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body += part.get_payload(decode=True).decode(errors="ignore")

        if part.get_filename():
            filename = part.get_filename()
            content = part.get_payload(decode=True)

            path = os.path.join(UPLOAD_DIR, filename)

            with open(path, "wb") as f:
                f.write(content)

            attachments.append(path)

    print("📎 ATTACHMENTS FOUND:", attachments)

    return body, attachments