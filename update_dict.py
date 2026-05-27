import json

months = {
    1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
}

facts = {}

for m in range(1, 13):
    for d in range(1, months[m] + 1):
        key = f"{m}-{d}"
        facts[key] = {
            "year": "1776",
            "text": "A defining moment in the ongoing American experiment. Our history is full of courage and conviction—celebrate 250 years of freedom today."
        }

# A few specific dates to show it works
facts["5-19"] = {
    "year": "1780",
    "text": "New England's Dark Day: A mysterious darkening of the sky over New England prompted many to believe Judgment Day had arrived, though it was likely caused by forest fires."
}
facts["7-4"] = {
    "year": "1776",
    "text": "The Continental Congress officially adopted the Declaration of Independence, proclaiming the American colonies' separation from Great Britain."
}
facts["12-25"] = {
    "year": "1776",
    "text": "George Washington and the Continental Army crossed the icy Delaware River in a daring nighttime maneuver to attack Hessian forces at Trenton."
}
facts["1-1"] = {
    "year": "1863",
    "text": "President Abraham Lincoln issued the Emancipation Proclamation, declaring that all persons held as slaves within the rebellious states are, and henceforward shall be free."
}

# format facts into a multi-line string
lines = []
for k, v in facts.items():
    year = v['year']
    # escape quotes just in case
    text = v['text'].replace('"', '\\"')
    lines.append(f'  "{k}": {{\n    "year": "{year}",\n    "text": "{text}"\n  }}')

dict_str = "{\n" + ",\n".join(lines) + "\n}"

with open("shopify_theme_assets/today_in_history.liquid", "r") as f:
    content = f.read()

start = content.find("const historyFacts = {")
end = content.find("};\n\n    const months")
if start != -1 and end != -1:
    new_content = content[:start] + "const historyFacts = " + dict_str + content[end:]
    with open("shopify_theme_assets/today_in_history.liquid", "w") as f:
        f.write(new_content)
    print("Updated today_in_history.liquid")
else:
    print("Could not find insertion points")
