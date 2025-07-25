import asyncpraw
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio
import aiofiles
import logging

# --- Configuration ---
SUBREDDIT_NAME = "Chainsawfolk"
POST_LIMIT = 500
POSTS_FILE = "nu_eta/posts_async.jsonl"
COMMENTS_FILE = "nu_eta/comments_async.jsonl"

# --- Logging Setup ---
log = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
log.addHandler(handler)


def convert_utc_to_vietnam_time(utc_timestamp):
    """Converts a UTC timestamp to a human-readable string in Vietnam time."""
    utc_datetime = datetime.fromtimestamp(utc_timestamp, tz=ZoneInfo("UTC"))
    vietnam_tz = ZoneInfo("Asia/Ho_Chi_Minh")
    vietnam_datetime = utc_datetime.astimezone(vietnam_tz)
    return vietnam_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")


async def scrape_subreddit(reddit):
    """
    Scrapes the latest posts and their comments from a specified subreddit
    and saves them to separate jsonl files.
    """
    log.info(f"Connecting to subreddit: r/{SUBREDDIT_NAME}")
    subreddit = await reddit.subreddit(SUBREDDIT_NAME)

    all_posts_data = []
    all_comments_data = []
    post_count = 0

    log.info(f"Fetching the latest {POST_LIMIT} posts...")
    async for post in subreddit.new(limit=POST_LIMIT):
        post_count += 1
        log.info(
            f'Processing post {post_count}/{POST_LIMIT}: "{post.title}" (ID: {post.id})'
        )

        post_data = {
            "id": post.id,
            "title": post.title,
            "score": post.score,
            "url": post.url,
            "author": str(post.author),
            "created_utc": post.created_utc,
            "created_vietnam": convert_utc_to_vietnam_time(post.created_utc),
            "selftext": post.selftext,
            "comments": [],
        }

        try:
            submission = await reddit.submission(id=post.id)
            log.info(f"  Fetching comments for post {submission.id}...")
            await submission.comments.replace_more(limit=None)
            comments = submission.comments.list()
            log.info(f"  Found {len(comments)} comments.")
            for comment in comments:
                if isinstance(comment, asyncpraw.models.reddit.comment.Comment):
                    comment_data = {
                        "id": comment.id,
                        "post_id": post.id,
                        "parent_id": comment.parent_id,
                        "body": comment.body,
                        "score": comment.score,
                        "author": str(comment.author),
                        "created_utc": comment.created_utc,
                        "created_vietnam": convert_utc_to_vietnam_time(
                            comment.created_utc
                        ),
                    }
                    post_data["comments"].append(comment_data)
                    all_comments_data.append(comment_data)
        except asyncpraw.exceptions.RedditAPIException as e:
            log.error(f"Could not process comments for post {post.id}: {e}")

        all_posts_data.append(post_data)

    if all_posts_data:
        async with aiofiles.open(POSTS_FILE, "w") as posts_file:
            for post_item in all_posts_data:
                await posts_file.write(json.dumps(post_item) + "\n")
        log.info(f"\nSuccessfully saved {len(all_posts_data)} posts to: {POSTS_FILE}")
    else:
        log.info("\nNo posts found to save.")

    if all_comments_data:
        async with aiofiles.open(COMMENTS_FILE, "w") as comments_file:
            for comment_item in all_comments_data:
                await comments_file.write(json.dumps(comment_item) + "\n")
        log.info(
            f"Successfully saved {len(all_comments_data)} comments to: {COMMENTS_FILE}"
        )
    else:
        log.info("No comments found to save.")


async def main():
    """Initializes the reddit client and runs the scraper."""
    reddit = asyncpraw.Reddit("bot1")
    try:
        await scrape_subreddit(reddit)
    finally:
        await reddit.close()
        log.info("\n--- Script Finished ---")


if __name__ == "__main__":
    asyncio.run(main())
