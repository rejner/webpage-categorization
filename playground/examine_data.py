import pandas
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(file_path):
    df = pandas.read_csv(file_path)
    print(df.head())
    print(df.columns)
    # get set of unique labels from AttributeTag column
    tags = df["AttributeTag"].unique()
    print(tags)
    # get all "content" values from AttributeTag column
    content = df[df["AttributeTag"] == "content"]
    print(content.count())
    for i in range(0, 10):
        print("-" * 100)
        print(content.iloc[i]["Content"])
        print("-" * 100)

if __name__ == "__main__":
    FILE_PATH = "data/webpage__entity__contents.csv"
    main(FILE_PATH)