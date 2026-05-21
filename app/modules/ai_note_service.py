from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def rewrite_attempt_note(raw_note):

    prompt = f"""
Rewrite this process server field note
into one short professional factual sentence.

Rules:
- Output ONLY the rewritten note
- Do NOT create affidavit templates
- Do NOT add signatures
- Do NOT add headings
- Do NOT add dates unless provided
- Do NOT invent facts
- Keep under 40 words
- Sound like a professional service attempt note

Field Note:
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