"""
split_data.py
Author: Ben Posnick
===================
Script that splits the original dataset into multiple CSV files, where one is for
training the fall detection classifier and the others each contain data
corresponding to a specific subject in the dataset, so as to simulate different
people in different homes.
Dataset: Localization Data for Posture Reconstruction
  Authors: Mitja Lustrek (mitja.lustrek@ijs.si), Bostjan Kaluza
  (bostjan.kaluza@ijs.si), Rok Piltaver (rok.piltaver@ijs.si), Jana Krivec
  (jana.krivec@ijs.si), Vedrana Vidulin (vedrana.vidulin@ijs.si) 
"""
import pandas as pd

raw_data = pd.read_csv("accelerometer_data.csv").to_numpy()
N_ROWS = raw_data.shape[0]
# Indices are extracted by inspection of "accelerometer_data.csv""
subject_indices = [(0, 5830), (5830, 11521), (11521, 16847),
                   (16847, 22249), (22249, N_ROWS)]
for i, tup in enumerate(subject_indices):
    s = tup[0]
    e = tup[1]
    subset = raw_data[s:e]
    df = pd.DataFrame(subset)
    if e != N_ROWS:
        file_name = "sensor_data_subject_A0" + str(i+1) + ".csv"
    else:
        file_name = "sensor_data_training.csv"
    df.to_csv(file_name, index=False, sep=",", header=False)
