# Agent Blueprint: Admin Dashboard & Ecosystem Specification

This document captures the board's vision for the comprehensive **Agent Blueprint (AB) Admin Dashboard**. It serves as a spec reference to guide our implementation prompts once final BOD alignment is reached.

---

## 1. Core Visual Layout & Theme

Following the Sovereign Forge brand system, the dashboard will utilize a premium dark-workspace aesthetic:
* **Background:** Deep space charcoal (`#0A0A0A`) with clean workspace grids (`#121212`).
* **Accents:** Sovereign Gold (`#D4AF37`) for active configurations, success metrics, and highlighted alerts.
* **Alert States:** Accent Plum (`#3C1F3D`) and subtle muted red outlines for warning flags.
* **Layout:** A flexible sidebar layout separating **Active Agents (Ecosystem)**, **Tech Stack Integrations**, **Intelligence Feeds**, and **System Controls**.

---

## 2. Key Modules & Features

### A. Critical Alert Console
A high-priority notification pane displaying operational action items.
* **Tech Stack Disruptions:** Alerts when API authentications expire (e.g., FUB OAuth token refreshing, kvCORE connection drops).
* **Lead Latency Warnings:** Real-time flags when incoming portal leads wait longer than 5 minutes for a response.
* **Neglected Client Warnings:** Flags database contacts who haven't received an authentic personal check-in within the configured window (default 90 days).
* **To-Do Action Items:** Integration with daily briefings and calendar schedules, formatted with checked/unchecked checklist status.

### B. Live Real Estate AI & PropTech News Feed
A curated, dynamic feed keeping agents ahead of industry changes.
* **RSS/API Sync:** Pulling real-time updates from trusted industry sources (Inman News, RealTrends, PropTechInsider, and general AI developer releases).
* **Local Market Intelligence:** Feeds tracking local Mississippi / Gulf Coast real estate updates alongside national statistics.

### C. Deployed Agent Status Logs
A live terminal-style logger showing the activity of autonomous agents currently active on the platform.
* **Friction Responders:** Logs showing lead triage activity (e.g., *"Claude Responder synced FUB lead John Doe in 4.2 seconds"*).
* **Contract Auditors:** Logs showing file checks (e.g., *"Dotloop contract draft compiled and audited for compliance"*).
* **Follow-up Cron Jobs:** Logs documenting repeat/referral outreach.

### D. Tech Stack Integrations Console
An intuitive panel allowing agents to construct and modify their custom software stack.
* **Add/Remove Integrations:** Self-serve connection blocks for popular CRM, transaction, and marketing tools (kvCORE, Follow Up Boss, Dotloop, Mailchimp, Shopify).
* **Modular Mappings:** Simple toggle controls mapping data flows between systems (e.g., *"Sync FUB tags directly to Mailchimp Lists"*).

---

## 3. Implementation Checklist & Tech Stack (Draft)

* **Frontend:** Vanilla CSS glassmorphism, responsive grid systems, dynamic custom element controls.
* **Backend:** Express API handlers mapped via `server.js` to route third-party news RSS feeds and log database states.
* **Database:** Supabase PostgreSQL tables mapping customer stack states (`user_integrations`, `system_alerts`, `agent_logs`).
* **Integrations:** OAuth 2.0 flow wrappers for FUB/kvCORE to enable seamless addition and deletion of tech stack items.
