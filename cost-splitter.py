#!/usr/bin/python3
"""
Cost-Splitter
"""
from __future__ import print_function
import boto3
import csv
import operator
import datetime
import time
import os.path
import zipfile
import yaml

LINKED_ACCOUNT_HEADING = "LinkedAccountId"
BLENDED_COST_HEADING = "BlendedCost"


def get_last_month():
    """
    Get the year and month of the last month
    return: Last month string in format YYYY-MM
    """
    # Get the first of this month
    today = datetime.date.today()
    first = today.replace(day=1)
    # Minus one day to get the last day of last month
    last_month = first - datetime.timedelta(days=1)
    # Return YYYY-MM as a string
    return last_month.strftime("%Y-%m")

def unzip_file(folder, file_name, archive_path):
    """
    Unzips the downloaded file
    :param folder: the folder the archive is in
    :param file_name: the file name (without .zip)
    :param archive_path: the full archive path in form folder/file.csv.zip
    return: succeeded: bool
    """
    # Check the file is there
    if os.path.isfile(archive_path):
        # Unzip the file
        print('Unzipping {}'.format(archive_path))
        zip_ref = zipfile.ZipFile(archive_path, 'r')
        zip_ref.extract(file_name, folder)
        zip_ref.close()
        return True
    else:
        # Throw an error
        print("Error: File {} not downloaded from bucket".format(archive_path))
        print("\tare you sure it is there?")
        return False


def split_cost(debug, row, search_indices, cost_index, reports, cost_split):
    """
    Analyse the row, split it to different reports
    :param debug: bool to describe if debug is enabled
    :param row: the row to analyse
    :param search_indices: a list of ints that represent columns to search
    :param cost_index: int representing the blended cost column
    :param reports: A list of reports and their tags
    :param cost_split: the variable used to store the current cost result
    return: cost_split: the variable used to store the current cost result
    """

    # We only want the ones that aren't zero
    cost = float(row[cost_index])
    if cost is not 0.0:
        for report in reports:
            title = list(report.keys())[0]
            tags = next(iter(report.values()))
            for tag in tags:
                for index in search_indices:
                    item = row[index].lower()
                    if tag in item:
                        cost_split[title] += cost
                        return cost_split
        # If debug mode is on, print the shared items
        if debug:
            for index in search_indices:
                if row[index]:
                    print("Shared : {} - {} $ {}".format(index, row[index], cost))
        cost_split["Shared"] += cost
    else:
        if debug:
            for index in search_indices:
                if row[index]:
                    print("Free: {} - {} $ {}".format(index, row[index], cost))
            cost_split["Free"] += cost
    return cost_split

def generate_metrics(config):
    """
    Generate the metrics
    :param config: the loaded config file
    """
    start_time = time.time()
    # Get the file from s3
    file_name = "{}-{}.{}".format(config['file_pattern'], get_last_month(),
                                  "csv")
    file_path = "{}/{}".format(config['save_folder'], file_name)
    archive_name = "{}.{}".format(file_name, "zip")
    archive_path = "{}/{}".format(config['save_folder'], archive_name)
    s3_client = boto3.client('s3')
    print('Downloading: {}'.format(archive_name))
    s3_client.download_file(config['bucket_name'], archive_name, archive_path)

    if unzip_file(config['save_folder'], file_name, archive_path):
        # load the file, sort it
        reader = csv.reader(open(file_path), delimiter=',')
        csv_headings = next(reader)
        # Get the indices we will need to extract the data
        linked_accound_index = csv_headings.index(LINKED_ACCOUNT_HEADING)
        index_blended_cost = csv_headings.index(BLENDED_COST_HEADING)
        search_indices = []
        for heading in config['searchable_column']:
            search_indices.append(csv_headings.index(heading))
        # sort the csv
        sortedlist = sorted(reader,
                            key=operator.itemgetter(linked_accound_index))

        # Loop through the list, because it is ordered by subscription id
        # we can give up after the group of subscription id has been loaded.
        subscription_list = []
        count = 0
        count_total = 0
        cost_blended = 0.0
        cost_split = {}
        print('Splitting costs')
        for report in config['reports']:
            title = list(report.keys())[0]
            cost_split[title] = 0.0
        cost_split["Shared"] = 0.0
        if config["debug"]:
            cost_split["Free"] = 0.0
        # Loop through and process the list
        for item in sortedlist:
            count_total += 1
            if item[linked_accound_index] == config['linked_account_id']:
                subscription_list.append(item)
                cost_blended += float(item[index_blended_cost])
                cost_split = split_cost(config["debug"], item, search_indices,
                                        index_blended_cost, config["reports"],
                                        cost_split)
                count += 1

        # Print the results
        total = cost_blended / 2
        print('\n=============================\n')
        print("For the month of {}".format(get_last_month()))
        print("Total Cost: {}".format(round(total, 2)))
        for report in cost_split:
            cost = cost_split[report] / 2
            percent = (cost / total) * 100
            print("{} cost is {}, {}% of the total".format(report,
                                                           round(cost, 2),
                                                           round(percent, 2)))
        print("{} of {} records were relevant".format(count, count_total))
        print("completed in %s seconds" % round(time.time() - start_time))
        print('\n=============================\n')
def main():
    """
    Generate cost metrics
    """
    with open("config.yml", 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
    if config['bucket_name'] and \
       config['file_pattern'] and \
       config['linked_account_id']:
        generate_metrics(config)
    else:
        print("Error: config.yml is poorly formed")

if __name__ == "__main__":
    main()
