from datetime import datetime
import json
from flask import Flask, render_template, request, redirect, flash, url_for

def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs

def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')
 
def filter_upcoming_competitions(competitions):
    """Return a list of competitions that are upcoming."""
    current_datetime = datetime.now()
    return [comp for comp in competitions if datetime.strptime(comp["date"], "%Y-%m-%d %H:%M:%S") > current_datetime]

@app.route('/showSummary', methods=['POST'])
def showSummary():
    upcoming_competitions = filter_upcoming_competitions(competitions)
    email = request.form.get('email')
    if not email:
        flash("Email is required")
        return redirect(url_for('index'))

    club = next((club for club in clubs if club['email'] == email), None)
    if club is None:
        flash("Club not found")
        return redirect(url_for('index'))

    return render_template('welcome.html', club=club, competitions=upcoming_competitions)

# Correction du bug login

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)

    if not foundClub or not foundCompetition:
        flash("Something went wrong - please try again")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    return render_template('booking.html', club=foundClub, competition=foundCompetition)

# Correction du bug de réservation

@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)
    placesRequired = int(request.form['places'])

    if not competition or not club:
        flash('Competition or club not found.')
        return redirect(url_for('index'))

    if placesRequired < 1:
        flash('You need to book at least 1 place.')
        return render_template('booking.html', club=club, competition=competition)
    
    if placesRequired > 12:
        flash('Impossible de commander plus de 12 places.')
        return render_template('welcome.html', club=club, competitions=competitions)


    if placesRequired > int(competition['numberOfPlaces']):
        flash('Not enough places available.')
        return render_template('booking.html', club=club, competition=competition)

    if placesRequired > int(club['points']):
        flash('Not enough points available in your club account.')
        return render_template('booking.html', club=club, competition=competition)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    club['points'] = int(club['points']) - placesRequired

    flash('Great - booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)

# Correction du bug d'achat de places

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()
app.run(debug=True)
