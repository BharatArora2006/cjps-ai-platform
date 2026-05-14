import pdfplumber


def extract_text_from_pdf(path):
    text = ""

    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

    except Exception as e:
        print(f"❌ Error reading PDF {path}: {e}")

    return text