import os
import json
import re

from groq import Groq
from dotenv import load_dotenv


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def safe_json_parse(content):

    try:
        return json.loads(content)

    except:

        match = re.search(
            r"\{[\s\S]*?\}",
            content
        )

        if match:

            try:
                return json.loads(
                    match.group()
                )

            except:
                pass

        print(
            "❌ RAW AI OUTPUT:\n",
            content
        )

        raise Exception(
            "AI did not return valid JSON"
        )


def extract_job_data(
    email_text,
    pdf_text
):

    prompt = f"""
You are a strict JSON generator.

Return ONLY valid JSON.
Do NOT add explanation or extra text.

Schema:
{{
  "client_name": string|null,
  "client_email": string|null,
  "defendant_name": string|null,
  "address": string|null,
  "county": string|null,
  "instructions": string|null
}}

EMAIL:
{email_text}

DOCUMENT:
{pdf_text}
"""

    print("CALLING GROQ")

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[

            {
                "role": "system",
                "content": (
                    "You only output valid JSON."
                )
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0

    )

    content = (
        response.choices[0]
        .message.content
    )

    print(
        "🧠 RAW AI OUTPUT:\n",
        content
    )

    return safe_json_parse(content)