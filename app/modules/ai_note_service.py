from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def rewrite_attempt_note(raw_note):

    prompt = f"""
Convert this contractor field note into a short,
clear, professional sentence.

Rules:
- Keep original meaning
- Keep factual details
- Do not add legal language
- Do not write affidavit text
- Do not use placeholders
- Do not invent information
- Maximum 2 sentences

Field note:
{raw_note}
"""

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[

            {
                "role": "system",
                "content": "You clean and rewrite contractor field notes professionally and concisely"
            },

            {
                "role": "user",
                "content": prompt
            }

        ]

    )

    return response.choices[0].message.content