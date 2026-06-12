-- Run this in the Supabase SQL Editor before using user-scoped buckets.

create table if not exists public.user_buckets (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    bucket_name text not null unique,
    display_name text not null,
    created_at timestamptz not null default now()
);

create index if not exists user_buckets_user_id_idx on public.user_buckets (user_id);

alter table public.user_buckets enable row level security;

create policy "Users can view own buckets"
    on public.user_buckets
    for select
    using (auth.uid() = user_id);

create policy "Users can insert own buckets"
    on public.user_buckets
    for insert
    with check (auth.uid() = user_id);

create policy "Users can delete own buckets"
    on public.user_buckets
    for delete
    using (auth.uid() = user_id);
