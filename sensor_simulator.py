"""
sensor_simulator.py
Author: Ben Posnick
===================
Reads in data from text files to simulate receiving data from sensors and then:
(1) Conducts preprocessing on samples to create examples
(2) Sends batches of examples to machine learning model endpoint on Azure
(3) Invokes the function server if a fall has occurred to trigger email alert and
    write to the database on Azure
"""
import os
import time
import numpy as np
import requests
from preprocessing import *
from azure.cosmos import CosmosClient
from datetime import datetime


def find_fall_sequence(arr):
    """
    Returns true if the fall sequence (defined to be [1, 1, 1, 3, 3], meaning 3
    "falling" events followed by 2 "lying" events) is present in the sequence
    of predictions "arr"; returns false otherwise. Also returns the length of the
    fall sequence "k".
    """
    fall_sequence = [1, 1, 1, 3, 3]
    k = len(fall_sequence)
    for i in range(len(arr)):
        if i >= k and arr[i-k:i] == fall_sequence:
            return True, k
    return False, k


def database_write(apt_num):
    """
    Writes to CosmosDB database on Azure, logging that a resident has fallen
    at the current time in apartment "apt_num" and unique index "idx".
    """
    db_endpoint = "https://fall-detection-logs.documents.azure.com:443/"
    key = "wNZuwOXUGBnFxbqcEfY1KLIHn7Pq6C1kRG3HhONZydyHaxyPLXBWwyBPK4yQ0HuW545njp84ho300wLsf2BBFA=="
    client = CosmosClient(db_endpoint, {'masterKey': key})
    database_id = "fall-detection-logs1"
    container_id = "logs1-container-1"
    database = client.get_database_client(database_id)
    container = database.get_container_client(container_id)
    now = datetime.now()
    current_time = str(now)
    document = {
        'id': current_time,
        'apartmentNumber': apt_num,
        'time': current_time,
        'description': 'Fallen resident'
    }
    container.create_item(document)


# Define constants
data_dir = "./data/"  # TODO: Change data_dir to wherever data is stored on EdgeVM
CPU2_endpoint = "http://f41b13f1-7767-470d-a493-76498cfe8aa2.eastus2.azurecontainer.io/score"
CPU1_endpoint = "http://03031af5-e1f0-49b6-a023-8f1266fa77ac.eastus2.azurecontainer.io/score"
APT_NUM = 5412
MAX_BATCH_SIZE = 10
N = 3  # Number of sensor data points to construct new "examples"

endpoint = CPU2_endpoint
while True:
    for file_name in os.listdir(data_dir):
        if "sensor_data_subject" not in file_name:
            continue
        print("\n\nReceiving data from:", file_name)
        f = open(data_dir + file_name)

        # Initialize loop variables
        curr_batch_size = 0
        X = []
        last_k_preds = []
        curr_ex_xyz = []
        curr_ex_labels = []
        # Counts how many of each sensor ID are in current example
        id_counts = [0]*4
        # Holds mean X, Y, Z positions for samples in current example
        mean_positions = [0]*3
        n = 0  # Counter for number of samples seen so far for current example

        for line in f:
            if n == N:
                # K samples collected so we have a full example now
                curr_example = create_example(
                    mean_positions, N, curr_ex_xyz, id_counts)
                X.append(list(curr_example))
                curr_batch_size += 1
                # Clear loop variables to prepare for next example
                curr_ex_xyz = []
                curr_ex_labels = []
                id_counts = [0]*4
                mean_positions = [0]*3
                n = 0
                last_subject = None
            # end-if
            if curr_batch_size == MAX_BATCH_SIZE:
                # MAX_BATCH_SIZE examples collected so we have a full batch now
                resp = requests.post(endpoint,
                                     "{\"data\": " + str(list(X)) + "}",
                                     headers={'Content-Type': 'application/json'})
                print("Response time:", resp.elapsed.total_seconds())
                preds = np.fromstring(resp.text[1:-1], dtype=int, sep=", ")
                print("Predictions:", preds)
                sequence = list(last_k_preds) + list(preds)
                has_fallen, k = find_fall_sequence(sequence)
                last_k_preds = preds[-k:]
                if has_fallen:
                    # Send trigger to function server to send email and write to database
                    database_write(APT_NUM)
                    print("FALL!")
                # Clear loop variables to prepare for next batch
                X = []
                curr_batch_size = 0
            # end-if
            curr_features = list(line.split(","))[:-1]
            mean_positions, curr_ex_xyz, curr_ex_labels, id_counts, n = process_sample(
                curr_features, mean_positions, curr_ex_xyz, None, id_counts, n)
            time.sleep(.025)  # To simulate collecting data
        # end-for
    # end-for
    break
# end-while
