# %%
import ast
import glob
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Read the data from mapmyrun
mapmyrun = pd.read_csv("workout_history.csv", parse_dates=["Date Submitted", "Workout Date"], sep=";")
mapmyrun["Avg Pace (min/km)"] = mapmyrun["Avg Pace (min/km)"].str.replace(",", ".").astype("float")
mapmyrun["pace"] = mapmyrun["Avg Pace (min/km)"]
mapmyrun.set_index("Workout Date", inplace=True)
mapmyrun

# %%
# Read the data from runtastic
sessions = []
for file in glob.glob(os.path.join("sessions", "*")):
    with open(file, 'r', encoding="utf8") as f:
        sessions.append(json.load(f))

sessions
# To Dataframe
df = pd.DataFrame.from_records(sessions)
df["start_time"] = pd.to_datetime(df["start_time"], unit='ms')
df = df.set_index('start_time')
df

df.features = df.features.astype("str")
df_sessions = pd.json_normalize(
    df.features.apply(ast.literal_eval)
)

for column in df_sessions.columns:
    df_sessions[column] = df_sessions[column].astype("str")
    feature = pd.json_normalize(
        df_sessions[column].apply(ast.literal_eval)
    )
    feature = feature.add_prefix(feature[~feature.type.isna()].type.iloc[0] + ".")
    df_sessions = df_sessions.drop(columns=[column])
    df_sessions = pd.concat([feature, df_sessions], axis=1)

df_sessions.index = df.index

df = pd.concat([df_sessions.add_prefix("features."), df], axis=1)
df["features.track_metrics.attributes.average_pace"] = df["features.track_metrics.attributes.average_pace"].astype("float")
df["features.track_metrics.attributes.average_speed"] = df["features.track_metrics.attributes.average_speed"].astype("float")

df



df["features.heart_rate.attributes.average"]
heart_rates = df[df["features.heart_rate.attributes.average"] != 0]
heart_rates

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(111)
ax.scatter(heart_rates.index, heart_rates["features.heart_rate.attributes.average"])
ax.scatter(mapmyrun.index, mapmyrun["Avg Heart Rate"])

average_speed = df[~df["features.track_metrics.attributes.average_speed"].isna()]["features.track_metrics.attributes.average_speed"]
average_speed = 1 / (average_speed * 60 / 1000)
fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(111)
ax.scatter(average_speed.index, average_speed)
ax.scatter(mapmyrun.index,  mapmyrun["pace"])
# .plot()






# %%

paces = pd.DataFrame(pd.concat([average_speed, mapmyrun["pace"]]).sort_index(), columns=["pace"])

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(111)
# ax.scatter(paces.index, paces["pace"])
paces.rolling(7).median().plot(ax=ax)


# df_sessions
# flat_results = pd.concat([results, df_sessions], axis=1)
