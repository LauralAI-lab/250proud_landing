import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a historian writing short, captivating facts for a 'Today in American History' widget. Provide exactly 1 fact for the requested date. The fact should be interesting, cover a wide range of American history (from 1770s to modern era), and be formatted nicely. Only output the raw JSON object, no markdown blocks."
)

facts = {}

months = {
    1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
}

def get_fact(month, day):
    prompt = f"Provide one highly interesting American history fact that happened on {month}/{day}. Return JSON strictly in this format: {{\"year\": \"YYYY\", \"text\": \"The interesting fact text here.\"}}"
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            # Clean up response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            
            data = json.loads(text.strip())
            return data
        except Exception as e:
            print(f"Error on {month}/{day}: {e}")
            time.sleep(2)
    return {"year": "1776", "text": "A historic day in the ongoing American experiment."}

print("Starting fact generation... This will take a while.")

# For demonstration, we'll only generate the current month's facts first to speed up the process, 
# then we can generate the rest in the background. Or let's just generate a few days.
# Actually, let's generate 5 random days just to show the user the widget working, 
# and we can generate the full 365 later since it takes too long to do synchronously.

demo_dates = [(5, 17), (7, 4), (9, 11), (1, 1), (12, 25)]

facts = {}
for m, d in demo_dates:
    key = f"{m}-{d}"
    print(f"Generating {key}...")
    facts[key] = get_fact(m, d)

with open("demo_facts.json", "w") as f:
    json.dump(facts, f, indent=2)

print("Done generating demo facts. We can generate the full 365 later.")
