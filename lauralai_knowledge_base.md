# 250PROUD™ Company Knowledge Base & Support Guide

Welcome to the official internal guide for LauralAI. Use these verified details to assist business partners, real estate professionals, and consumers.

---

## 1. Platform Mission & Vision
*   **What is 250PROUD™?** It's a premium, automated marketing and co-branding platform built to celebrate the upcoming 250th anniversary of the United States (America 250).
*   **The B2B Value Proposition:** We help local business operators (real estate agents, brokers, mortgage lenders, and insurance agencies) generate warm leads and build deep local relationships by co-branding high-quality patriotic materials.
*   **The Core Philosophy:** Move away from cold digital outreach and focus on evergreen, relationship-driven marketing through physical assets that stay in client homes for years.

---

## 2. Core Products & Pricing

### A. Co-Branded Coloring Book: "250 Strong: Built By Hand"
*   **Description:** A premium, beautifully illustrated historical coloring book telling the stories of American builders, pioneers, and historic moments.
*   **Co-Branding Features:** Partners get their logo, headshot, contact info, brokerage details, and a custom Call-to-Action (CTA) printed directly on the front cover, spine, and back cover.
*   **Fulfillment:** Print-on-demand. Once ordered via the configurator, we compile the custom PDF and route it directly to our print partner, Lulu, who prints and ships it directly to the customer.
*   **Sales Focus:** High-margin B2B tool. Agents buy boxes of 50 or 100 books to hand out at open houses, community events, or closing gifts.

### B. Custom Acrylic Magnets
*   **Description:** High-durability, clear acrylic patriotic magnets featuring historic American flags, eagles, and liberty symbols co-branded with the partner's business card info.
*   **Visualizer:** Partners can upload their logo and see a live preview of the layout on `magnet-configurator.html`.
*   **Value:** Stays on a client’s refrigerator for years, keeping the partner's contact info top-of-mind.

### C. The America 250 Celebration Bundle
*   **Description:** A complete promotional pack featuring co-branded books, custom magnets, decals, and digital sharing assets. Designed to provide maximum touchpoints for a single local marketing campaign.

---

## 3. The B2B Configurator Workflow
*   **Where is it?** Located at `b2b-configurator.html` (digitally accessible under the "Digital Marketing Tool" menu).
*   **How it works:**
    1.  Partner fills in their contact card information (brokerage name, phone, email, and social links).
    2.  They write a custom call-to-action (e.g., "Scan here to find your dream home!").
    3.  They upload their transparent logo (PNG/JPG) and high-res headshot.
    4.  They preview the cover spread in real-time.
    5.  Upon clicking "Submit & Order", they are redirected to a secure Shopify checkout session.
    6.  The backend builds the custom book PDF and fires the print order automatically.

---

## 4. Shipping & Fulfillment FAQs
*   **The $29 Celebration Bundle:** The digital coloring book and Resource Center access are delivered instantly upon purchase. Custom physical magnets and stickers are delivered in 3 to 8 business days.
*   **Swag, Clothing & Apparel:** Swag, clothing, and apparel items take an average of 4 to 8 business days to arrive.
*   **Co-Branded Books (B2B):** Automated physical printing via the Lulu API connector is temporarily paused while we finalize the connection (scheduled for Saturday/Sunday). Currently, partners receive their custom, print-ready co-branded PDFs instantly via email, and physical print distributions can be coordinated manually by contacting our team.
*   **Can we print in bulk?** Yes! For custom bulk print distributions (500+ units), suggest they book a call on our calendar to coordinate details.

---

## 5. Proactive Support Directives & Lead Conversion
*   **If a user asks about co-branding or how to start:** Give them a quick overview of the 3-step configurator process, then explicitly direct them: *"Head over to our B2B Configurator at b2b-configurator.html to upload your logo and preview your cover!"*
*   **If a user asks about custom designs or bulk discounts (500+ units):** Recommend scheduling a call: *"We do custom bulk licensing for larger brokerages. Let's schedule a 10-minute strategy call on our calendar to get that sorted out."*
*   **If a user has a complex billing issue, shipping delay, or custom technical problem:** Instruct them to email support: *"For order modifications or deep technical help, please drop a line to our team at info@250proud.net and we will sort it out immediately."*

---

## 6. Today In History Customizable Widget Integration & DIY Support Guide
This section contains verified instructions for licensing and embedding the customizable, white-labeled "Today in History" widget. The widget is served from our platform and can be configured with custom themes (dark/light), custom accent colors, and a single custom CTA button.

### A. Core Embedding Options
1.  **Option 1: 1-Line Script Embed (Recommended)**
    *   *HTML Snippet:* `<div id="tih-widget-container"></div><script src="https://250proud.net/tih-widget-loader.js" data-color="#D4AF37" data-cta-text="Find Your Home" data-cta-link="https://mybrokerage.com" data-theme="dark"></script>`
    *   *Value:* Auto-resizes the height dynamically so the widget fits the host container on both desktop and mobile without cut-off margins or scrollbars.
2.  **Option 2: HTML IFrame Embed**
    *   *HTML Snippet:* `<iframe src="https://250proud.net/tih-widget.html?primaryColor=%23D4AF37&ctaText=Find%20Your%20Home&ctaLink=https%3A%2F%2Fmybrokerage.com&theme=dark" style="width:100%; height:550px; border:none; overflow:hidden; border-radius:16px;" scrolling="no"></iframe>`
    *   *Value:* Useful for editors that block external script tags. Requires manual height adjustments if the layout content overflows.
3.  **Option 3: Direct Standalone Link (Alternative Page)**
    *   *URL:* `https://250proud.net/tih-widget.html?primaryColor=%23D4AF37&ctaText=Find%20Your%20Home&ctaLink=https%3A%2F%2Fmybrokerage.com&theme=dark`
    *   *Value:* Used to create a dedicated link on a navigation menu or external button.

### B. Platform-Specific Integration Steps
*   **Wix Integration:**
    1.  In the Wix Editor, click the **Add Elements (+)** button.
    2.  Select **Embed Code** > choose **HTML Embed**.
    3.  Click **Enter Code**, select **Code**, paste the *1-Line Script snippet*, and click **Update**.
    4.  Stretch or resize the container box to fit the layout (recommended height: 550px).
*   **GoDaddy Integration:**
    1.  Edit your GoDaddy site.
    2.  Scroll to the page section and click **Add Section**.
    3.  Select **HTML** or **Custom Code** from the category list.
    4.  Paste either the *1-Line Script snippet* or *HTML IFrame snippet* directly into the Custom Code field.
    5.  Set height parameters to 600px, click **Done**, and Publish.
*   **Squarespace Integration:**
    1.  Edit a section on your Squarespace page and click **Add Block**.
    2.  Select **Code** or **Embed** from the block options menu.
    3.  Paste the *1-Line Script snippet* into the block settings.
    4.  Ensure 'Display Source Code' is turned **off**.

### C. Troubleshooting & Support Flow Directives (For Ask Lauralai Agent)
*   **If a user complains the widget is cut off or shows scrollbars:**
    *   Explain that this happens when the host container height is smaller than the widget layout (especially on mobile).
    *   Direct them to use the **1-Line Script Embed (Option 1)** which handles auto-resizing.
    *   If their platform restricts script tags and forces an iframe, instruct them to increase the `height` attribute in their iframe tag to `650px` or `700px` for mobile spacing.
*   **If the button link does not work or loops back:**
    *   Instruct them to verify that their `data-cta-link` or `ctaLink` parameter contains the full URL path, including `https://` (e.g. `https://mybrokerage.com` instead of just `mybrokerage.com`).
*   **Support Escalation Policy:**
    *   Do **NOT** offer email support (`support@250proud.net` or `info@250proud.net`) immediately. 
    *   Walk the user through the Wix, GoDaddy, or Squarespace step-by-step instructions first.
    *   Ask if they are using one of our three embedding options.
    *   Only if the user indicates they have completed the steps and are still experiencing a system-level bug, provide the email contact: *"If you have followed these setup steps and the widget is still not loading, please email our support team at support@250proud.net with a link to your page and we will review the network logs."*

---

## 7. Liberty Ledger™ Widget Non-Technical FAQs
Use these answers to assist non-technical users in understanding, deploying, and customizing the widget:
*   **What is Liberty Ledger™ - Today in History?**
    *   It is a premium, white-labeled web widget that displays a daily historical fact and illustration (e.g. July 6, 1854 - founding of the Republican Party). It includes a customizable call-to-action button (like "Find Your Home") that directs visitors back to your personal landing page or MLS search.
*   **Do I need to know how to write code to use it?**
    *   No. We built a self-serve Widget Builder that handles all the configuration. Once you customize your theme and colors, it outputs a single line of script. You just copy and paste it into Wix, GoDaddy, Squarespace, or WordPress.
*   **How do I customize the widget's style?**
    *   Go to `tih-widget-builder.html` where you can pick a Light or Dark theme, enter any hex color code for the accents/buttons to match your brand, and customize the text and link for the Call-to-Action button.
*   **How much does the license cost?**
    *   We offer a full-featured sandbox builder to customize and preview the widget for free. To embed the live widget on your production website, you must purchase a lifetime **Forge Press Digital License** for a one-time fee of $29.
*   **What happens if a date doesn't have a custom drawing?**
    *   If a specific date does not have a custom drawing pre-loaded, the widget automatically searches public databases (like Wikipedia) to fetch an accurate, high-quality public domain image or portrait for that historical event, ensuring it always looks professional.
*   **Will it slow down my website?**
    *   Not at all. The script loads asynchronously, meaning it won't delay your website's text or images from rendering, and it has a zero footprint on page load performance.


