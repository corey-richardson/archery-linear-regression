from matplotlib import pyplot as plt
import seaborn as sns

import pandas as pd
from datetime import date


YEAR = date.today().strftime("%y")
score_data = pd.read_csv(f"static/arrow_scores_outdoors_{YEAR}.csv", header=0)

#########################
## DATA PRE-PROCESSING ##
#########################

score_data.date = pd.to_datetime(score_data.date)
score_data["golds_pct"] = (score_data.golds / score_data.arrows)*100
score_data["days_since_first_entry"] = (
    score_data.date - min(score_data.date) ).dt.days
most_recent_date = max(score_data.date).strftime("%Y-%m-%d")
score_data["day_of_week"] = score_data.date.dt.day_of_week

##############
## PLOTTING ##
##############

# Figure labels
plt.xlabel("Distance")
plt.ylabel("Average Arrow Score")

# Fixes the symptom, not the illness.
import warnings, matplotlib
warnings.filterwarnings(
    "ignore", 
    category=matplotlib.MatplotlibDeprecationWarning)

# Colour Map used to differentiate days of week or by month
# DEPRECATION WARNING REGARDING GET_CMAP, TO FIX?
# Use ``matplotlib.colormaps[name]`` or ``matplotlib.colormaps.get_cmap(obj)`` 
# instead.
cmap_seven = plt.cm.get_cmap('cool', 7)
cmap_twelve = plt.cm.get_cmap('cool', 12)

# cmap_seven = plt.colormaps.get_cmap('cool', 7)
# cmap_twelve = plt.colormaps.get_cmap('cool', 12)
# ColormapRegistry.get_cmap() takes 2 positional arguments but 3 were given
# What's the current equivelant to what I'm trying to do here?

# Scatterplot of distance against arrow average
# Style: O markers if not competition, X markers if is competition
# Hue: Change colour of marker depending on day of week of shoot, 
# uses 'cmap' to discern colours

##############################
# graphs/day_of_week_fig.png # 
# graphs/month_fig.png       #
##############################

def plot_by_hue(hue_type, label, cmap):
    sns.scatterplot(
        data = score_data,
        x = "distance", y = "arrow_average",
        style = "is_comp",
        hue = hue_type,
        palette = cmap,
    )

    # Plot lines for min / avg / max arrow scores at each distance
    plt.plot(
        score_data.distance.unique(), 
        score_data.groupby(['distance']).arrow_average.max(), 
        "k:")
    plt.plot(
        score_data.distance.unique(), 
        score_data.groupby(['distance']).arrow_average.mean(), 
        "g--")
    plt.plot(
        score_data.distance.unique(), 
        score_data.groupby(['distance']).arrow_average.min(), 
        "k:")
    
    plt.show(block=False) # Running in GH codespace, plot does not appear
    plt.savefig(f"graphs/{label}_fig.png")
    plt.clf()

plot_by_hue(score_data.day_of_week, "day_of_week", cmap_seven)    
plot_by_hue(score_data.date.dt.month, "month", cmap_twelve)

###########################
# graphs/distance_fig.png #
###########################

cmap = plt.cm.get_cmap('tab10', score_data.distance.nunique())
sns.scatterplot(
    data = score_data,
    x = "date", y = "arrow_average",
    style = "is_comp",
    hue = "distance",
    palette = cmap,
)

averages = score_data.groupby(['distance']).mean().arrow_average
for i, avg in enumerate(averages):
    plt.axhline(avg, color=cmap.colors[i], alpha=0.7, linestyle=':')
    
# 252 Scheme Boundaries
plt.axhline(280 / 36, color='k', linestyle="dashed", linewidth=0.9) # Compound
plt.axhline(252 / 36, color='k', linestyle="dashed", linewidth=0.9) # Recurve

plt.savefig("graphs/distance_fig.png")
plt.clf()

#############################
# graphs/arrows_per_day.png #
#############################

arrows_per_day = score_data.groupby(score_data.date).arrows.sum()
plt.plot(arrows_per_day)
plt.savefig("graphs/arrows_per_day.png")

print(f"Analysis derived from {sum(arrows_per_day)} datapoints.")

#####################
## DATA DISPLAYING ##
#####################

# Display the trends depending on day of week
day_of_week = score_data.groupby(score_data.day_of_week)
day_of_week_cols = day_of_week[['arrow_average','arrows','golds_pct']]
day_of_week_summary = day_of_week_cols.mean()
day_of_week_count = score_data.groupby(score_data.day_of_week)['date'].count()
day_of_week_merged = day_of_week_summary.merge(day_of_week_count, on=["day_of_week"])
print(f"\n\nScore Data grouped by Day of Week: \n{day_of_week_merged}\n")

# Display the trends depending on month and year
month_and_year = score_data.groupby(
    [score_data.date.dt.year, score_data.date.dt.month])
month_and_year_cols = month_and_year[['arrow_average','distance','arrows','golds_pct']]
month_and_year_summary = month_and_year_cols.mean()
print(f"Score Data grouped by Month: \n{month_and_year_summary}\n")

# Display the trends depending on month and year ALSO seperated by Distance to target
month_year_dist = score_data.groupby(
    [score_data.distance, score_data.date.dt.year, score_data.date.dt.month] )
month_year_dist_cols = month_year_dist[['arrow_average','arrows','golds_pct']]
month_year_dist_summary = month_year_dist_cols.mean()
print(f"Score Data grouped by Distance by Month: \n{month_year_dist_summary}\n")

# Display the trends depending on distance
dist = score_data.groupby(['distance'])
dist_cols = dist[['arrow_average','arrows','golds_pct']]
dist_summary = dist_cols.mean()
print(f"Score Data grouped by Distance: \n{dist_summary}\n")

# Display the trends depending on whether or not the shoot was at a competition
dist_comp = score_data.groupby([score_data.distance, score_data.is_comp])
dist_comp_cols = dist_comp[['arrow_average','arrows','golds_pct']]
dist_comp_summary = dist_comp_cols.mean()
print(f"Score Data grouped by Competition Status: \n{dist_comp_summary}\n")