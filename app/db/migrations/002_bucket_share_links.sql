-- Shareable bucket links with viewer/editor permissions.
-- Run in Supabase SQL editor before using share endpoints.

create table if not exists public.bucket_share_links (
  id uuid primary key default gen_random_uuid(),
  bucket_name text not null,
  created_by uuid not null references auth.users (id) on delete cascade,
  token text not null unique,
  role text not null default 'viewer' check (role in ('viewer', 'editor')),
  anyone_with_link boolean not null default true,
  revoked_at timestamptz,
  expires_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_bucket_share_links_bucket on public.bucket_share_links (bucket_name);
create index if not exists idx_bucket_share_links_creator on public.bucket_share_links (created_by);
create index if not exists idx_bucket_share_links_token on public.bucket_share_links (token);
