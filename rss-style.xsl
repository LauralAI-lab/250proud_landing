<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
      <head>
        <title>RSS Feed - <xsl:value-of select="rss/channel/title"/></title>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet" />
        <style>
          body {
            font-family: 'Inter', sans-serif;
            background-color: #F5F0E8;
            color: #071E3D;
            margin: 0;
            padding: 0;
            line-height: 1.6;
          }
          .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
          }
          header {
            background: linear-gradient(135deg, #071E3D 0%, #0A3161 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 40px;
          }
          h1 {
            font-family: 'Outfit', sans-serif;
            margin: 0 0 10px 0;
            font-size: 2.2rem;
            color: #FFFFFF;
          }
          .desc {
            font-size: 1.1rem;
            opacity: 0.9;
            margin: 0 0 20px 0;
          }
          .feed-notice {
            background-color: rgba(231, 201, 126, 0.15);
            border: 1px dashed #B8922A;
            padding: 20px;
            border-radius: 8px;
            font-size: 0.95rem;
            margin-bottom: 30px;
            color: #0A3161;
            text-align: left;
          }
          .feed-notice strong {
            color: #B31942;
          }
          .item {
            background: white;
            border: 1px solid #E0E0E0;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
          }
          .item:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
          }
          .item h2 {
            font-family: 'Outfit', sans-serif;
            margin: 0 0 10px 0;
            font-size: 1.5rem;
          }
          .item h2 a {
            color: #0A3161;
            text-decoration: none;
            transition: color 0.2s;
          }
          .item h2 a:hover {
            color: #B31942;
          }
          .meta {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 15px;
          }
          .item-desc {
            color: #333;
          }
          .btn {
            display: inline-block;
            background: #B31942;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.9rem;
            transition: background 0.2s;
          }
          .btn:hover {
            background: #D31A47;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <header>
            <h1>250Proud Journal</h1>
            <p class="desc"><xsl:value-of select="rss/channel/description"/></p>
            <a href="https://250proud.net/blog.html" class="btn" style="background:#B8922A; color:#071E3D; margin-right:10px;">← Back to Journal</a>
            <a href="/rss.xml" class="btn">Copy RSS Feed Link</a>
          </header>
          
          <div class="feed-notice">
            <strong>What is this page?</strong> This is the official RSS feed for the 250Proud Journal. 
            To subscribe, copy the URL of this page and paste it into your favorite RSS reader (like Feedly, Reeder, or NetNewsWire).
          </div>
          
          <xsl:for-each select="rss/channel/item">
            <div class="item">
              <h2>
                <a href="{link}"><xsl:value-of select="title"/></a>
              </h2>
              <div class="meta">
                Published on: <xsl:value-of select="pubDate"/>
              </div>
              <div class="item-desc">
                <xsl:value-of select="description" disable-output-escaping="yes"/>
              </div>
              <a href="{link}" style="display:inline-block; margin-top:15px; color:#B31942; text-decoration:none; font-weight:600; font-size:0.9rem;">Read Full Post →</a>
            </div>
          </xsl:for-each>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
