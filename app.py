import pandas as pd

from sklearn import linear_model
from sklearn.model_selection import train_test_split

from flask import Flask, render_template, redirect, url_for, session

from forms import GetScoreData, GetNewScore

from datetime import date

###############
## APP SETUP ##
###############

# Define constants
YEAR = date.today().strftime("%y")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

###########################################
## DATA PRE-PROCESSING AND LIN REG MODEL ##
###########################################

# Load dataframe
# Then, convert the 'date' column to be datetypes 
score_data = pd.read_csv(f"static/arrow_scores_outdoors_{YEAR}.csv", header=0)
score_data.date = pd.to_datetime(score_data.date)

# Create a column of the calculated percent of gold arrows (arrows scoring >9)
score_data["golds_pct"] = (score_data.golds / score_data.arrows)*100

# Create a column indicating the time elapsed since the first entry
# This is used as a feature to show progress over time
score_data["days_since_first_entry"] = (
    score_data.date - min(score_data.date) ).dt.days

# Get the most recent entry to the .csv file.
# This is displayed in "index.html" for the user to calculate the desired 
# days till feature since this date.
# Create dataframe column converting the datetime object to a day of 
# week string
most_recent_date = max(score_data.date).strftime("%Y-%m-%d")
score_data["day_of_week"] = score_data.date.dt.day_of_week

# Select features to predict FROM and features to predict TO
features = score_data[["distance","days_since_first_entry","is_comp"]]
scored = score_data[["arrow_average","golds_pct"]]

# Split the data into training and testing subsets
# This ensures there is 'real' data left unseen by the model which can be 
# used to score the models accuracy.
# THERE IS A DANGER HERE: if the 20% testing subset includes the very few datapoints with
# "is_comp" equal to 1 then the model will have no values to train this feature on.
# To resolve this issue I need more data, however this is obviously easier said than done...
X_train, X_test, y_train, y_test = train_test_split(
    features, scored, test_size = 0.2, random_state = 864)

# Creates the LinReg model and trains it with the training subset
model = linear_model.LinearRegression()
model.fit(X_train, y_train)

# Score the model
# This is done on training AND testing data to highlight overfitting
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Train Model Score: {train_score}")
print(f"Test Model Score: {test_score}\n")

##################
## FLASK ROUTES ##
##################

# Index / Homepage
# http://127.0.0.1:5000/
@app.route('/', methods=["GET","POST"])
def index():
    get_score_data = GetScoreData()
    # On submission...
    if get_score_data.validate_on_submit():
        # Getters for form data
        season = get_score_data.season.data
        distance = get_score_data.distance.data
        units = get_score_data.units.data
        on_date = get_score_data.days_till.data
        is_comp = get_score_data.is_comp.data
        
        days_till = (date.today() - on_date).days
        
        # Sanitise input
        distance, days_till, units = float(distance), float(days_till), float(units)
        distance *= units
        
        # Use the trained model to predict output variables from input variables
        # max(score_data.days_since_first_entry) + days_till 
        # --> Most recent entry to .csv file + user specified number of days
        guesses = model.predict(
            [[distance, 
              max(score_data.days_since_first_entry) + days_till, 
              is_comp]]
        )
        
        # Sanitise output
        # Max possible score is 10
        # Max gold_pct is 100%
        if guesses[0][0] > 10:
            guesses[0][0] == f"10.00 {guesses[0][0]}"
        if guesses[0][1] > 100:
            guesses[0][1] = 100

        # Save vars to server-side-stored session data
        # f"{on_date.year:>04}-{on_date.month:>02}-{on_date.day:>02}"
        session["distance"] = distance
        session["on_date"] = on_date.strftime("%A %d %B %Y")
        session["avg_score"] = guesses[0][0]
        session["gold_pct"] = guesses[0][1]
        session["is_comp"] = is_comp
        
        # Redirect to the 'submitted' path
        return redirect(url_for(
            'submitted',
            _external=True, 
            scheme='https'
        ))
     
    return render_template(
        "index.html", 
        get_score_data=get_score_data
    )

# Model Prediction Results Displayer
# http://127.0.0.1:5000/submitted
@app.route('/submitted', methods=["GET","POST"])
def submitted():
    # Retrieve vars from server-side-stored session data
    distance = session["distance"]
    on_date = session["on_date"]
    avg_score = session["avg_score"]
    gold_pct = session["gold_pct"]
    is_comp = session["is_comp"]
    
    # Pass all template vars in here
    return render_template(
        "submit.html",
        distance = distance,
        on_date = on_date,
        avg_score = f"{avg_score:.3f}",
        gold_pct = f"{gold_pct:.2f}",
        is_comp = is_comp,
        _external=True, _scheme='https')

# Add New Score to .csv File
# http://127.0.0.1:5000/add_score
@app.route('/add_score', methods=["GET","POST"])
def add_score():
    get_new_score = GetNewScore()
    # On submission...
    # Get values from submitted form
    if get_new_score.validate_on_submit():
        season = get_new_score.season.data
        arrow_average = get_new_score.arrow_average.data
        distance = get_new_score.distance.data
        units = get_new_score.units.data
        date = get_new_score.date.data
        golds = get_new_score.golds.data
        total_arrows = get_new_score.total_arrows.data
        is_comp = get_new_score.is_comp.data
        
        # Initialise file path
        file_path = f"static/arrow_scores_{season}_{YEAR}.csv"

        # Convert to yards
        # If metres selected in dropdown, units is 1.09... to convert into yards
        # If yards selected in dropdown, unit is 1 --> no change
        distance = int(distance) * float(units)
        
        # Write to the relevant .csv file
        to_write = f'\n{arrow_average:.2f},{distance:.2f},"{date}",{golds},{total_arrows},{is_comp}'
        with open(file_path, "a+") as file:
            file.write(to_write)
        
        # Redirect to the 'display' route for the relevant season
        return redirect(url_for(
            'results',
            _external=True, 
            scheme='https',
            season=season
        ))
        
    return render_template(
        "add_score.html",
        get_new_score = get_new_score
    )

# Display Results For Outdoor/Indoor Season
# http://127.0.0.1:5000/display/outdoors
# http://127.0.0.1:5000/display/indoors
@app.route('/results/<season>', methods=["GET","POST"])
def results(season):
    season = season.strip("/")
    # Open dataframe for selected season of current year
    # Sort by distance and by average arrow score
    score_data = pd.read_csv(f"static/arrow_scores_{season}_{YEAR}.csv")
    score_data = score_data.sort_values(
        by=["distance","arrow_average"], 
        ascending=[True, False])
    return render_template(
        "results.html",
        season = season.title(),
        score_data = score_data.values.tolist()
    ) 