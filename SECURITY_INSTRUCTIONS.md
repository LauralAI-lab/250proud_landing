# Security Action Items & Instructions for 250PROUD

Please complete these manual security tasks to secure your cloud accounts. You can copy these items into Google Tasks or your project management workflow.

---

## 🔑 1. Supabase Security Settings

### Enable Row-Level Security (RLS)
Ensure that malicious actors cannot read or write to your database tables directly via the public API keys.
1. Log in to the [Supabase Dashboard](https://supabase.com).
2. Go to **Database** (left sidebar) -> **Tables**.
3. Select your key tables (e.g., `b2b_orders`, `users`).
4. Ensure **Row-Level Security (RLS)** is toggled **ON**.
5. Add access policies so users can only read/write their own data (e.g., matching `auth.uid() = user_id`).

### Enable Dashboard Multi-Factor Authentication (MFA)
Protect your administrative access to the database.
1. In the Supabase Dashboard, click your profile icon in the bottom-left corner -> **Account Settings**.
2. Go to **Security** and enable **Multi-Factor Authentication (MFA)**.

---

## 📧 2. Resend Domain Verification (DNS)

To prevent spoofing and ensure your emails do not land in spam folders, verify Resend's records in your domain registrar (GoDaddy, Namecheap, Route53, etc.).
1. Log in to the [Resend Dashboard](https://resend.com).
2. Go to **Domains** and select `250proud.net`.
3. Copy the generated **SPF**, **DKIM**, and **DMARC** records.
4. Log in to your domain registrar and add these records to your DNS settings.
5. Go back to Resend and click **Verify**.

---

## 💻 3. GitHub Organization Hardening

Protect the codebase from unauthorized code pushes.
1. Log in to [GitHub](https://github.com).
2. Navigate to your repository settings -> **Branches**.
3. Add a branch protection rule for the `main` branch.
4. Toggle **Require a pull request before merging** and **Require approvals** to ON.
