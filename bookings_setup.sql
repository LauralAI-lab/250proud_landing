-- Run this in the Supabase SQL editor to create the bookings table for your scheduling app
CREATE TABLE IF NOT EXISTS bookings (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  host text NOT NULL, -- 'mike' or 'laurie'
  meeting_date date NOT NULL, -- YYYY-MM-DD
  meeting_time text NOT NULL, -- HH:MM (24-hour format)
  guest_name text NOT NULL,
  guest_email text NOT NULL,
  guest_phone text,
  guest_company text,
  topic text,
  duration integer DEFAULT 30, -- in minutes
  created_at timestamptz DEFAULT now()
);

-- Index for quick lookups on host and date
CREATE INDEX IF NOT EXISTS bookings_host_date_idx ON bookings(host, meeting_date);

-- Enforce Row-Level Security (RLS)
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (so visitors can book meetings)
CREATE POLICY "Enable insert for anonymous users" 
ON bookings FOR INSERT 
TO public 
WITH CHECK (true);

-- Allow anonymous select (so the frontend can fetch booked slots)
CREATE POLICY "Enable select for anonymous users" 
ON bookings FOR SELECT 
TO public 
USING (true);
