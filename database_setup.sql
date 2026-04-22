-- Run this in Supabase SQL editor to create subscribers table
CREATE TABLE IF NOT EXISTS subscribers (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  first_name text,
  email text NOT NULL,
  address text,
  city text,
  state text,
  zip text,
  phone text,
  comm_pref text,
  source text,
  created_at timestamptz DEFAULT now()
);

-- Index on email for deduplication checks
CREATE UNIQUE INDEX IF NOT EXISTS subscribers_email_idx ON subscribers(email);

-- Enforce Row-Level Security (RLS) to secure the table
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (so landing page can submit data if using Anon Key)
-- Service Role keys in Vercel bypass RLS automatically.
CREATE POLICY "Enable insert for anonymous users" 
ON subscribers FOR INSERT 
TO public 
WITH CHECK (true);
