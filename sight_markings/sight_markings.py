import pandas as pd
import numpy as np
from sklearn import linear_model

# Read data from csv
scope = pd.read_csv(f"sight_markings/sight_marks.csv", header = 0)
distances = scope["distance"]
sight_markings = scope["sight_marking"]

# Reshape into a 'inferred' (-1) by 1 array
distances = np.reshape(distances, (-1, 1))
sight_markings = np.reshape(sight_markings, (-1, 1))

# Create and fit the model
# Predict values to plot, and user specified distance
model = linear_model.LinearRegression()
model.fit(distances, sight_markings)

distances_yds = [10,     20, 30, 40, 50, 60, 70, 80, 90, 100, ]
distances_m =   [10, 18, 20, 30, 40, 50, 60, 70, 80, 90, 100, ]

def predicter(distances_arr, unit):
    for distance in distances_arr:
        
        # Lin-reg model uses yard values as input
        # If metres are being predicted, convert to yards BUT keep the front-facing
        # value (distance) as metres to display later.
        if unit == "m":
            distance_modified = distance * 1.09361
        else:
            distance_modified = distance
            
        distance_modified = np.reshape(distance_modified, (-1, 1))
        sight_mark = model.predict(distance_modified)
        print(f"{distance}{unit} : {sight_mark[0][0]:.2f}")
    print()
        
predicter(distances_yds, "yds")
predicter(distances_m, "m")