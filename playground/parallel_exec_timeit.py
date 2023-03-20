from pyspark.sql import SparkSession
from bs4 import BeautifulSoup
import re
import os
import timeit
from joblib import Parallel, delayed

 # extract the links and headings from the HTML files
def extract_links_headings(text):
    soup = BeautifulSoup(text, "html.parser")
    links = soup.find_all("a", href=True)
    if links:
        links = [a.get("href") for a in links]
    headings =  soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    if headings:
        headings = [re.sub(r"\s+", " ", h.get_text(strip=True)) for h in headings]

    return links, headings

def extract_links_headings_from_file(file):
    # open the file
    with open(file, "r") as f:
        # read the file
        text = f.read()
        # extract the links and headings
        links, headings = extract_links_headings(text)
        # print the results
        return links, headings

def run_spark(root_dir):
    # create a SparkSession
    spark = SparkSession.builder.appName("WebPageCategorization").getOrCreate()

    # load the HTML files from the directory
    html_files_rdd = spark.sparkContext.wholeTextFiles(root_dir)
    links_headings_rdd = html_files_rdd.map(lambda x: extract_links_headings(x[1]))


    # convert the RDD to a DataFrame using sampling
    df = links_headings_rdd.toDF(["Links", "Headings"], sampleRatio=0.1)

    # show the first 20 rows of the DataFrame
    # df.show(20, False)

    # Save the results to a CSV file
    # df.write.format("parquet").save("/workspaces/webpage_categorization/my.parquet", mode="overwrite")

    # stop the SparkSession
    spark.stop()

def run_normal(root_dir):
    # get all files in the directory
    files = os.listdir(root_dir)
    # iterate over the files
    items = []
    for file in files:
        if not os.path.isfile(root_dir + file):
            continue

        # open the file
        with open(root_dir + file, "r") as f:
            # read the file
            text = f.read()
            # extract the links and headings
            links, headings = extract_links_headings(text)
            # print the results
            items.append((links, headings))
    print(len(items))

def run_joblib(root_dir, n_jobs=4):
    # get all files in the directory
    files = [file for file in os.listdir(root_dir) if os.path.isfile(root_dir + file)]
    # iterate over the files
    items = Parallel(n_jobs=n_jobs)(delayed(extract_links_headings_from_file)(root_dir + file) for file in files)
    print(len(items))

if __name__ == "__main__":
    root_dir = "/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/"
    # root_dir = "/workspaces/webpage_categorization/data/spark_test/"
    # time the execution of the normal code
    print("Joblib code execution time: ", timeit.timeit(lambda: run_joblib(root_dir, 12), number=1))
    # print("Spark code execution time: ", timeit.timeit(lambda: run_spark(root_dir), number=1))
    # print("Normal code execution time: ", timeit.timeit(lambda: run_normal(root_dir), number=1))
    # time the execution of the Spark code
    
