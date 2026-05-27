import urllib.request
import json
import concurrent.futures
import time

months = {
    1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
}

dates = []
for m in range(1, 13):
    for d in range(1, months[m] + 1):
        dates.append((m, d))

def fetch_fact(m, d):
    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{m:02d}/{d:02d}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                events = data.get('events', [])
                
                # Try to find American history event
                for event in events:
                    text = event.get('text', '')
                    lower_text = text.lower()
                    if any(keyword in lower_text for keyword in ['american', 'united states', 'u.s.', 'washington', 'lincoln', 'congress', 'new york', 'california']):
                        return f"{m}-{d}", {"year": str(event.get('year', 'Unknown')), "text": text}
                        
                # Fallback to the first event
                if events:
                    return f"{m}-{d}", {"year": str(events[0].get('year', 'Unknown')), "text": events[0].get('text')}
        except Exception as e:
            time.sleep(1)
            continue
    return f"{m}-{d}", {"year": "1776", "text": "A historic moment in time."}

facts = {}
print("Fetching 366 facts from Wikipedia...")
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch_fact, m, d): (m, d) for (m, d) in dates}
    for future in concurrent.futures.as_completed(futures):
        key, fact = future.result()
        facts[key] = fact

with open('historyFacts.json', 'w') as f:
    json.dump(facts, f, indent=2)
print("Done!")
