open comments.jsonl |select id parent_id author score created_vietnam created_utc | sort-by score
open posts.jsonl |select id author score created_vietnam created_utc | sort-by created_utc
open comments.jsonl | columns


open comments_async.jsonl |select id parent_id author score created_vietnam created_utc | sort-by score
open posts_async.jsonl |select id author score created_vietnam created_utc | sort-by created_utc
