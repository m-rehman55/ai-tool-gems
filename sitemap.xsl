<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" 
    xmlns:html="http://www.w3.org/TR/REC-html40"
    xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html lang="en">
      <head>
        <title>XML Sitemap — AI Tool Gems Pakistan</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #f7faf6;
            color: #173c35;
            padding: 40px 20px;
            line-height: 1.6;
          }
          .container {
            max-width: 1000px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            border: 1px solid rgba(43, 91, 74, 0.12);
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            overflow: hidden;
            padding: 32px;
          }
          .header {
            border-bottom: 2px solid #eef5ef;
            padding-bottom: 24px;
            margin-bottom: 24px;
          }
          .brand-badge {
            display: inline-block;
            background: #eef5ef;
            color: #2f9f88;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 12px;
          }
          h1 {
            font-size: 28px;
            color: #173c35;
            margin-bottom: 8px;
          }
          p.lead {
            color: #61766e;
            font-size: 15px;
          }
          .meta-info {
            display: flex;
            gap: 16px;
            margin-top: 16px;
            flex-wrap: wrap;
          }
          .stat-pill {
            background: #f7faf6;
            border: 1px solid rgba(43, 91, 74, 0.12);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
          }
          .stat-pill b {
            color: #2f9f88;
            font-size: 15px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
          }
          th {
            background: #f7faf6;
            color: #173c35;
            text-align: left;
            padding: 12px 16px;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid rgba(43, 91, 74, 0.12);
          }
          td {
            padding: 12px 16px;
            border-bottom: 1px solid #eef5ef;
            font-size: 14px;
          }
          tr:hover td {
            background: #fbfdfb;
          }
          a {
            color: #2f9f88;
            text-decoration: none;
            font-weight: 500;
            word-break: break-all;
          }
          a:hover {
            text-decoration: underline;
          }
          .date {
            color: #7c8d86;
            font-size: 13px;
            white-space: nowrap;
          }
          .footer {
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #eef5ef;
            font-size: 13px;
            color: #7c8d86;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <span class="brand-badge">AIToolGems Pakistan XML Sitemap</span>
            <h1>Indexable URL Directory</h1>
            <p class="lead">Official Google Search Central &amp; Bing XML sitemap for aitoolgems.tech. Lists verified Pakistani AI tool catalog listings, buying guides, and directories.</p>
            <div class="meta-info">
              <div class="stat-pill">Total Indexable URLs: <b><xsl:value-of select="count(sitemap:urlset/sitemap:url)"/></b></div>
              <div class="stat-pill">Marketplace: <b>Pakistan (PKR / EasyPaisa / JazzCash)</b></div>
            </div>
          </div>
          <table>
            <thead>
              <tr>
                <th style="width: 60px;">#</th>
                <th>URL Location</th>
                <th style="width: 140px;">Last Modified</th>
              </tr>
            </thead>
            <tbody>
              <xsl:for-each select="sitemap:urlset/sitemap:url">
                <tr>
                  <td style="color: #7c8d86; font-weight: 600;"><xsl:value-of select="position()"/></td>
                  <td>
                    <xsl:variable name="itemURL">
                      <xsl:value-of select="sitemap:loc"/>
                    </xsl:variable>
                    <a href="{$itemURL}">
                      <xsl:value-of select="sitemap:loc"/>
                    </a>
                  </td>
                  <td class="date">
                    <xsl:value-of select="sitemap:lastmod"/>
                  </td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
          <div class="footer">
            <span>© 2026 AI Tool Gems Pakistan · Independent AI Tools Marketplace</span>
            <span><a href="https://aitoolgems.tech/">Visit Storefront →</a></span>
          </div>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
