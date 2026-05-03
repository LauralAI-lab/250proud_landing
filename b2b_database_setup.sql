-- 1. Create the b2b_orders table to replace orders.json
CREATE TABLE IF NOT EXISTS b2b_orders (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  order_id text UNIQUE NOT NULL, -- The checkout session ID from Stripe/Shopify
  email text NOT NULL,
  company_name text,
  phone text,
  website text,
  headline text,
  copy text,
  logo_path text,
  headshot_path text,
  hero_path text,
  interior_path text,
  status text DEFAULT 'pending_payment',
  created_at timestamptz DEFAULT now()
);

-- Secure the table (Vercel Service Role bypasses this, but public access is blocked)
ALTER TABLE b2b_orders ENABLE ROW LEVEL SECURITY;

-- 2. Create the b2b_pdfs storage bucket
INSERT INTO storage.buckets (id, name, public) 
VALUES ('b2b_pdfs', 'b2b_pdfs', true)
ON CONFLICT (id) DO NOTHING;

-- Allow public access to read PDFs
CREATE POLICY "Public Access" 
ON storage.objects FOR SELECT 
TO public 
USING (bucket_id = 'b2b_pdfs');

-- Note: Vercel will use the Service Role key to upload, so we don't need to write an upload policy for public users.
