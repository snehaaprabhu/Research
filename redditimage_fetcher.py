import praw
import requests
import re
from pathlib import Path
import os
import json
from local_secrets import REDDIT_SECRET, REDDIT_CLIENT_ID, REDDIT_USER_AGENT

# Function to sanitize filenames
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# Function to get unique filename
def get_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base}_{counter}{ext}"
        counter += 1
    return unique_filename

# Set up reddit client app
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

# Subreddits to read from
sports_subreddits = [
    "Cricket",
    "IPL"
]

teams_subreddits = [
    "Royal Challengers Bangalore",
    "RCB", 
    "MI",
    "CSK"      
]

all_subreddits = [*sports_subreddits, *teams_subreddits]

# Track metadata for each image read
image_metadata = {}

# Load existing metadata
metadata_path = Path("image_metadata.json")
if metadata_path.exists():
    with open(metadata_path, "r") as f:
        existing_json = json.load(f)
else:
    existing_json = {}

# Read all the "Hot" posts from each subreddit and extract the images from the posts
for subreddit_name in all_subreddits:
    print(f"Processing subreddit: {subreddit_name}")
    subreddit_dir = Path("subreddits_2") / subreddit_name
    subreddit_dir.mkdir(parents=True, exist_ok=True)

    subreddit_instance = reddit.subreddit(subreddit_name)
    try:
        posts = subreddit_instance.hot(limit=10)  # Fetch only top 10 posts for example
        for post in posts:
            if post.is_reddit_media_domain and not post.is_video:
                url = post.url
                file_name = sanitize_filename(url.split("/")[-1])
                if "." not in file_name:
                    file_name += ".jpg"
                
                unique_file_name = get_unique_filename(subreddit_dir, file_name)
                
                if unique_file_name not in existing_json:
                    try:
                        r = requests.get(url)
                        r.raise_for_status()
                        image_path = subreddit_dir / unique_file_name
                        with open(image_path, "wb") as f:
                            f.write(r.content)
                        image_metadata[unique_file_name] = {
                            "url": post.url,
                            "post_id": str(post),
                            "subreddit": subreddit_name,
                            "title": post.title,
                            "created_utc": post.created_utc
                        }
                    except requests.RequestException as e:
                        print(f"Failed to download image {url}: {e}")
                else:
                    print(f"Image {unique_file_name} already downloaded.")
    except Exception as e:
        print(f"Failed to process subreddit {subreddit_name}: {e}")

# Update the image_metadata.json file
existing_json.update(image_metadata)
with open(metadata_path, "w") as f:
    json.dump(existing_json, f, indent=4)

print("Image metadata updated.")
