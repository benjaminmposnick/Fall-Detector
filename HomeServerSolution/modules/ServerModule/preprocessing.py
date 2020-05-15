"""
preprocessing.py
Author: Ben Posnick
===================
Defines functions for preprocessing the raw accelerometer data used in classifying
whether or not a person falls in their smart home.
Dataset: Localization Data for Posture Reconstruction
  Authors: Mitja Lustrek (mitja.lustrek@ijs.si), Bostjan Kaluza
  (bostjan.kaluza@ijs.si), Rok Piltaver (rok.piltaver@ijs.si), Jana Krivec
  (jana.krivec@ijs.si), Vedrana Vidulin (vedrana.vidulin@ijs.si) 
"""
import numpy as np
import pandas as pd


def convert_id_to_int(id):
    """
    Returns the unique integer representation of "id" corresponding to the four
    sensor IDs given in the dataset:
    - ANKLE_LEFT   010-000-024-033
    - ANKLE_RIGHT  010-000-030-096
    - CHEST        020-000-033-111
    - BELT         020-000-032-221
    Preconditions: "id" is a string and its value is one of the four listed above
    """
    assert type(id) == str
    if id == "010-000-024-033":
        return 0
    elif id == "010-000-030-096":
        return 1
    elif id == "020-000-033-111":
        return 2
    elif id == "020-000-032-221":
        return 3
    else:
        raise ValueError("ID " + id + " is not supported")


def most_frequent(arr):
    """
    Returns the most frequent element in "arr"
    """
    return max(set(arr), key=arr.count)


def convert_label_to_int(label):
    """
    Returns the unique integer representation of "label" corresponding to the
    class labels given in the dataset
    Preconditions: "label" is a string and its value is one of the class labels
    in the dataset
    """
    assert type(label) == str
    if label == "walking":
        return 0
    elif label == "falling":
        return 1
    elif label == "lying down":
        return 2
    elif label == "lying":
        return 3
    elif label == "sitting":
        return 4
    elif label == "sitting down" or label == "sitting on the ground":
        return 5
    elif label == "on all fours":
        return 6
    elif label == "standing up from sitting" or label == "standing up from sitting on the ground" or label == "standing up from lying":
        return 7
    else:
        raise ValueError("Label " + label + " is not supported")


def get_trajectory(a, b, c):
    """
    Given three floats "a", "b", and "c", where "a" was recorded before "b"
    and "b" was recorded before "c", returns an integer to depict the trajectory
    of these three positional data points such that:
    -  1 means the values are increasing
    -  0 means the values have a local minimum or local maximum
    - -1 means the values are decreasing
    Preconditions: "a", "b", and "c" are floats and they correspond to the same
    position metric (i.e. X, Y, or Z position)
    """
    if a < b and b < c:
        return 1
    elif (a < b and b > c) or (a > b and b < c):
        return 0
    elif a > b and b > c:
        return -1
    else:
        raise ValueError("Data is corrupted")


def create_feature_vectors(data_file, is_test_data):
    """
    Reads in data from CSV file "data_file" and creates feature vectors.
    Preconditions: data_file is a string that gives the path to a CSV file
    """
    assert ".csv" in data_file
    raw_data = pd.read_csv(data_file).to_numpy()

    # Define constants
    N_ROWS = raw_data.shape[0]
    N_COLS = raw_data.shape[1]
    N_CLASSES = 8
    N = 3  # Number of sensor data points to construct new "examples"
    MAX_PER_LABEL = 1250

    # Initialize loop variables
    label_counts = np.zeros(N_CLASSES)
    X, Y = [], []
    curr_ex_xyz, curr_ex_labels = [], []
    # Counts how many of each sensor ID are in current example
    id_counts = [0]*4
    # Holds mean X, Y, Z positions for samples in current example
    mean_positions = [0]*3
    n = 0  # Counter for number of samples seen so far for current example
    last_subject = None  # ID of the current subject whose data is being collected

    for i in range(N_ROWS):
        if n == N:
            # K samples collected so we have a full example now
            argmax_label = most_frequent(curr_ex_labels)
            if label_counts[argmax_label] < MAX_PER_LABEL or is_test_data:
                curr_example = create_example(
                    mean_positions, N, curr_ex_xyz, id_counts)
                X.append(curr_example)
                Y.append(argmax_label)
                label_counts[argmax_label] += 1
            # Clear loop variables to prepare for next example
            curr_ex_xyz = []
            curr_ex_labels = []
            id_counts = [0]*4
            mean_positions = [0]*3
            n = 0
            last_subject = None
        # end-if
        curr_features = raw_data[i]
        subject = curr_features[0]
        if last_subject is not None and last_subject != subject:
            # Discard data for this example since subjects changed
            curr_ex_xyz = []
            curr_ex_labels = []
            id_counts = [0]*4
            mean_positions = [0]*3
            n = 0
            last_subject = None
            continue
        # end-if
        mean_positions, curr_ex_xyz, curr_ex_labels, id_counts, n = process_sample(
            curr_features, mean_positions, curr_ex_xyz, curr_ex_labels, id_counts, n)
    # end-for
    return np.asarray(X), np.asarray(Y)


def process_sample(curr_features, mean_positions, curr_ex_xyz, curr_ex_labels, id_counts, n):
    """
    Collects important features from raw data sample to be used in constructing
    example, which is comprised of 3 samples, and returns this information
    Preconditions: "curr_features" is a row of the CSV file containing the 
    accelerometer data
    """
    id_str = curr_features[1]
    id_int = convert_id_to_int(id_str)
    x = float(curr_features[4])
    y = float(curr_features[5])
    z = float(curr_features[6])
    if curr_ex_labels is not None:
        label_str = curr_features[7]
        label_int = convert_label_to_int(label_str)
        if label_str == "standing up from lying":
            # Throw away this label because of issues in dataset
            return mean_positions, curr_ex_xyz, curr_ex_labels, id_counts, n
        curr_ex_labels.append(label_int)
    mean_positions[0] += x
    mean_positions[1] += y
    mean_positions[2] += z
    curr_ex_xyz.append(id_int)
    curr_ex_xyz.append(x)
    curr_ex_xyz.append(y)
    curr_ex_xyz.append(z)
    id_counts[id_int] += 1
    n += 1
    return mean_positions, curr_ex_xyz, curr_ex_labels, id_counts, n


def create_example(mean_positions, K, curr_ex_xyz, id_counts):
    """
    Returns an example created from the data collected from three accelerometer
    samples.
    """
    mean_positions[0] /= K  # Compute mean X
    mean_positions[1] /= K  # Compute mean Y
    mean_positions[2] /= K  # Compute mean Z
    trajectory = [0]*3
    for j in range(3):
        # j=0 => X; j=1 => Y; j=2 => Z
        # Get jth position data from each sample for this example
        trajectory[j] = get_trajectory(curr_ex_xyz[j+1],
                                       curr_ex_xyz[j+5], curr_ex_xyz[j+9])
    curr_example = curr_ex_xyz + id_counts + mean_positions + trajectory
    return np.asarray(curr_example)
