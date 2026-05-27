import re

with open("shopify_theme_assets/today_in_history.liquid", "r") as f:
    content = f.read()

updates = {
    "5-19": {
        "year": "1780",
        "text": "The sky over New England went dark by mid-morning. Candles burned at noon, roosters returned to roost, and many believed Judgment Day had arrived. Modern science traces it to massive wildfires in Ontario combined with thick fog — but the awe stuck with a generation.",
        "image": "{{ '1780-05-19_dark-day.png' | file_url }}"
    },
    "5-20": {
        "year": "1862",
        "text": "Lincoln signed the Homestead Act, opening 160 acres of public land to any citizen willing to settle and improve it for five years. Between 1863 and 1900, roughly 400,000 claims moved 80 million acres into private hands — and reshaped the American West, for better and worse.",
        "image": "{{ '1862-05-20_homestead-act.png' | file_url }}"
    },
    "5-21": {
        "year": "1881",
        "text": "After watching the Civil War chew through soldiers without organized relief, Clara Barton spent twelve years lobbying for an American chapter of the Red Cross. On May 21, 1881, she founded it in Washington. Today it runs on roughly 300,000 volunteers — the system she built by refusing to be told no.",
        "image": "{{ '1881-05-21_clara-barton.png' | file_url }}"
    },
    "5-22": {
        "year": "1872",
        "text": "Seven years after Appomattox, President Grant signed the Amnesty Act, restoring full civil and political rights to nearly all former Confederates. The intent was to stitch the country back together. The reality was more complicated — but the act marked a deliberate national choice to choose reconciliation over permanent punishment.",
        "image": "{{ '1872-05-22_amnesty-act.png' | file_url }}"
    },
    "5-23": {
        "year": "1788",
        "text": "South Carolina became the eighth state to ratify the U.S. Constitution, leaving just one more needed to make it the law of the land. The vote came after weeks of hard debate in Charleston — proof that the document survived by argument, not consensus. New Hampshire would push it over the line a month later.",
        "image": "{{ '1788-05-23_sc-ratification.png' | file_url }}"
    },
    "5-24": {
        "year": "1844",
        "text": "Samuel Morse sat in the Capitol and tapped out a message in code. Forty miles away in Baltimore, his partner received it: \\\"What hath God wrought.\\\" The telegraph turned distance into a non-issue and rewired how America did business, war, and news. The world got smaller that morning.",
        "image": "{{ '1844-05-24_morse.png' | file_url }}"
    },
    "5-25": {
        "year": "1868",
        "text": "Three years after the Civil War ended, General John A. Logan called for a national day to decorate the graves of the Union dead. On the first Decoration Day, May 30, 1868, flowers were laid at Arlington for both Union and Confederate soldiers. The name became Memorial Day. The duty didn't change.",
        "image": "{{ '1868-05-25_decoration-day.png' | file_url }}"
    }
}

for date, data in updates.items():
    # regex to replace the dictionary entry
    pattern = r'("' + date + r'":\s*\{)(.*?)(^\s*\})'
    
    # new inner content
    inner = f'\n    "year": "{data["year"]}",\n    "text": "{data["text"]}",\n    "image": "{data["image"]}"\n  '
    
    content = re.sub(pattern, r'\g<1>' + inner + r'}', content, flags=re.DOTALL | re.MULTILINE)

# Also update the HTML to support dynamic images
html_old = """      <div class="tih-visual">
        {% if section.settings.default_image %}
          <img src="{{ section.settings.default_image | image_url: width: 800 }}" alt="Historical Event">
        {% else %}
          <!-- Fallback image if none selected in Shopify -->
          <img src="https://images.unsplash.com/photo-1555899434-94d1368aa7af?auto=format&fit=crop&w=800&q=80" alt="Historical Event Placeholder">
        {% endif %}
      </div>"""

html_new = """      <div class="tih-visual">
        {% if section.settings.default_image %}
          <img id="tih-fact-image" src="{{ section.settings.default_image | image_url: width: 800 }}" alt="Historical Event" data-fallback="{{ section.settings.default_image | image_url: width: 800 }}">
        {% else %}
          <!-- Fallback image if none selected in Shopify -->
          <img id="tih-fact-image" src="https://images.unsplash.com/photo-1555899434-94d1368aa7af?auto=format&fit=crop&w=800&q=80" alt="Historical Event Placeholder" data-fallback="https://images.unsplash.com/photo-1555899434-94d1368aa7af?auto=format&fit=crop&w=800&q=80">
        {% endif %}
      </div>"""

content = content.replace(html_old, html_new)

# Update Javascript to swap the image
js_old = """    document.getElementById('tih-year-label').innerText = "On this day in " + factData.year;
    document.getElementById('tih-fact-text').innerText = factData.text;
  });"""

js_new = """    document.getElementById('tih-year-label').innerText = "On this day in " + factData.year;
    document.getElementById('tih-fact-text').innerText = factData.text;
    
    const factImage = document.getElementById('tih-fact-image');
    if (factImage) {
      if (factData.image) {
        factImage.src = factData.image;
      } else {
        factImage.src = factImage.getAttribute('data-fallback');
      }
    }
  });"""

content = content.replace(js_old, js_new)

with open("shopify_theme_assets/today_in_history.liquid", "w") as f:
    f.write(content)

print("Updated today_in_history.liquid with new Batch 1 data and dynamic image support.")
