from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def rewrite_attempt_note(raw_note):

    prompt = f"""
You are a professional legal operations assistant.

Rewrite the contractor's field note into a short,
professional update.

STRICT RULES:

- NEVER invent facts
- NEVER assume service was completed
- NEVER add legal conclusions
- NEVER add investigation language
- NEVER mention documents unless explicitly stated
- Preserve original meaning exactly
- Keep response very short
- Use simple professional language
- If input is vague, keep output vague
- Output only one sentence

Examples:

Input: "done"
Output: "Service attempt completed."

Input: "no one home"
Output: "Attempted service but no one answered the door."

Input: "called no answer"
Output: "Attempted phone contact but received no answer."

Input: "wrong address"
Output: "Attempted service at the provided address but address information may be incorrect."

Raw Note:
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