Table users {
  id uuid [pk, default: `gen_random_uuid()`]
  email varchar [not null, unique]
  username varchar [not null, unique]
  role varchar [not null, note: 'admin, author, player']
  bio text
  website_url varchar
  created_at timestamp_with_time_zone [not null, default: `now()`]
}

Table labs {
  id uuid [pk, default: `gen_random_uuid()`]
  author_id uuid [not null, ref: > users.id]
  title varchar [not null]
  slug varchar [not null, unique]
  description text
  category varchar [default: 'Hardware']
  points integer [default: 100]
  wokwi_url text [not null]
  is_published boolean [default: false]
  created_at timestamp_with_time_zone [not null, default: `now()`]
  updated_at timestamp_with_time_zone [not null, default: `now()`]
}

Table flags {
  id uuid [pk, default: `gen_random_uuid()`]
  lab_id uuid [not null, ref: - labs.id] 
  flag_hash varchar [not null, note: 'Bcrypt/Argon2 hash of expected flag']
  is_case_sensitive boolean [default: true]
  created_at timestamp_with_time_zone [not null, default: `now()`]
}

Table submissions {
  id uuid [pk, default: `gen_random_uuid()`]
  player_id uuid [not null, ref: > users.id]
  lab_id uuid [not null, ref: > labs.id]
  submitted_flag text [not null]
  is_correct boolean [not null]
  created_at timestamp_with_time_zone [not null, default: `now()`]
}

Table solves {
  id uuid [pk, default: `gen_random_uuid()`]
  player_id uuid [not null, ref: > users.id]
  lab_id uuid [not null, ref: > labs.id]
  submission_id uuid [not null, unique]
  points_awarded integer [not null]
  created_at timestamp_with_time_zone [not null, default: `now()`]
}

Ref: submissions.id -? solves.submission_id
