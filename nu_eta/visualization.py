import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter
import re


# Function to load jsonl file into a pandas DataFrame
def load_jsonl(file_path):
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Skipping invalid line in {file_path}: {line.strip()}")
    return pd.DataFrame(data)


# Load the datasets
try:
    posts_df = load_jsonl("posts_async.jsonl")
    comments_df = load_jsonl("comments_async.jsonl")
except FileNotFoundError as e:
    print(
        f"Error: {e}. Make sure the jsonl files are in the same directory as the script."
    )
    exit()

print(f"Loaded {len(posts_df)} posts and {len(comments_df)} comments.")

# --- Visualization 1: Posts and Comments over time ---
print("Generating plot for posts and comments over time...")

if "created_utc" in posts_df.columns and "created_utc" in comments_df.columns:
    # Convert 'created_utc' to datetime
    posts_df["created_datetime"] = pd.to_datetime(posts_df["created_utc"], unit="s")
    comments_df["created_datetime"] = pd.to_datetime(
        comments_df["created_utc"], unit="s"
    )

    # Resample to get daily counts
    posts_per_day = posts_df.resample("D", on="created_datetime").size()
    comments_per_day = comments_df.resample("D", on="created_datetime").size()

    plt.figure(figsize=(12, 6))
    plt.plot(
        posts_per_day.index,
        posts_per_day.values,
        label="Posts per day",
        marker="o",
        linestyle="-",
    )
    plt.plot(
        comments_per_day.index,
        comments_per_day.values,
        label="Comments per day",
        marker="o",
        linestyle="-",
    )
    plt.title("Number of Posts and Comments Over Time")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("posts_comments_over_time.png")
    plt.close()
    print("Saved posts_comments_over_time.png")
else:
    print("Skipping time series plot because 'created_utc' column is missing.")


# --- Visualization 2: Score distribution for posts ---
print("Generating plot for post score distribution...")
if "score" in posts_df.columns:
    plt.figure(figsize=(10, 5))
    # Using a log scale for y-axis can be helpful if scores are very skewed
    plt.hist(
        posts_df["score"],
        bins=50,
        range=(0, max(100, int(posts_df["score"].quantile(0.95)))),
        log=True,
    )
    plt.title("Distribution of Post Scores (up to 95th percentile)")
    plt.xlabel("Score")
    plt.ylabel("Number of Posts (log scale)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("post_scores_distribution.png")
    plt.close()
    print("Saved post_scores_distribution.png")
else:
    print("Skipping post score distribution plot because 'score' column is missing.")


# --- Visualization 3: Score distribution for comments ---
print("Generating plot for comment score distribution...")
if "score" in comments_df.columns:
    plt.figure(figsize=(10, 5))
    plt.hist(
        comments_df["score"],
        bins=50,
        range=(-10, max(50, int(comments_df["score"].quantile(0.95)))),
        log=True,
    )
    plt.title("Distribution of Comment Scores (up to 95th percentile)")
    plt.xlabel("Score")
    plt.ylabel("Number of Comments (log scale)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("comment_scores_distribution.png")
    plt.close()
    print("Saved comment_scores_distribution.png")
else:
    print("Skipping comment score distribution plot because 'score' column is missing.")


# --- Visualization 4: Top words in post titles ---
print("Generating plot for top words in post titles...")
if "title" in posts_df.columns:
    # Basic stopwords
    stopwords = set(
        [
            "t",
            "s",
            "the",
            "a",
            "to",
            "and",
            "is",
            "in",
            "it",
            "of",
            "for",
            "i",
            "you",
            "he",
            "she",
            "that",
            "this",
            "what",
            "why",
            "how",
            "who",
            "when",
            "where",
            "my",
            "me",
            "we",
            "our",
            "your",
            "about",
            "an",
            "are",
            "as",
            "at",
            "be",
            "by",
            "from",
            "has",
            "have",
            "if",
            "on",
            "or",
            "with",
        ]
    )

    word_counts = Counter()
    for title in posts_df["title"].dropna():
        words = re.findall(r"\b\w+\b", title.lower())
        word_counts.update(w for w in words if w not in stopwords and not w.isdigit())

    most_common_words = word_counts.most_common(20)
    words, counts = zip(*most_common_words)

    plt.figure(figsize=(12, 8))
    plt.barh(range(len(words)), counts, align="center")
    plt.yticks(range(len(words)), words)
    plt.gca().invert_yaxis()  # display in descending order
    plt.title("Top 20 Most Common Words in Post Titles")
    plt.xlabel("Frequency")
    plt.tight_layout()
    plt.savefig("top_words_in_titles.png")
    plt.close()
    print("Saved top_words_in_titles.png")
else:
    print("Skipping top words plot because 'title' column is missing.")

print("\nAll visualizations have been generated and saved as PNG files.")
