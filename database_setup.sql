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
