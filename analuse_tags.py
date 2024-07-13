import pandas as pd
import os
import json
from collections import Counter

def make_aggregated_tags():
    tags_directory = 'subreddits_tags'  # Replace with your actual directory path
    tag_counter = Counter()

    # Check if the directory exists
    if not os.path.exists(tags_directory):
        print(f"Directory {tags_directory} does not exist.")
        return

    # List all JSON files in the specified directory
    filenames = os.listdir(tags_directory)

    for filename in filenames:
        if filename.endswith(".json"):
            filepath = os.path.join(tags_directory, filename)
            with open(filepath, "r") as file:
                data = json.load(file)
                if 'tags' in data:
                    tags = data['tags']
                    tag_counter.update(tags)

    # Convert the tag counter to a DataFrame
    df = pd.DataFrame(tag_counter.items(), columns=['Tag', 'Count'])
    print(df)

    return df

def do_analysis():
    # Assume make_aggregated_tags returns a DataFrame
    raw_tags_df = make_aggregated_tags()

    if raw_tags_df is not None:
        print("Columns in raw_tags_df:", raw_tags_df.columns)

        # Check if 'none' column exists before accessing it
        if 'none' in raw_tags_df.columns:
            print(raw_tags_df.loc[raw_tags_df['none'] == 0].shape)
        else:
            print("Column 'none' does not exist in the DataFrame.")

def main():
    do_analysis()

if __name__ == "__main__":
    main()
