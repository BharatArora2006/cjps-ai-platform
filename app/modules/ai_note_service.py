from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def rewrite_attempt_note(raw_note):

    prompt = f"""
You are a legal process service assistant.

Rewrite the following process server attempt note
into a short, professional, legally appropriate
service attempt summary.

IMPORTANT RULES:

- NEVER invent facts
- NEVER assume service completed unless explicitly stated
- NEVER add legal conclusions
- NEVER mention another party unless explicitly written
- Keep the meaning extremely close to the original note
- If the note is short or vague, keep it simple and factual
- Use one sentence only
- Professional legal tone
- Correct obvious typos and grammatical mistakes.
- Do NOT hallucinate names, identities, or events.
- If the meaning is unclear, keep the summary conservative.
- Never invent facts not present in the original note.
- If the note says:
  "No opened the door"
  interpret it as:
  "No one opened the door."
- Keep responses realistic for legal process serving.
- Use concise professional language.
- Do NOT use quotation marks.
- Return ONLY the rewritten note.


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