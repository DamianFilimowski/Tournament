# Tournament Application

Welcome to the Tournament Application! This Django app allows you to manage tournaments, teams, matches, and scorers for
different events.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)


## Features

- Create, update, and delete tournaments, teams, users
- Manage teams and players
- After reaching at least 8 teams in tournament you can start tournament, choice is between tournament with grop stage
with playoff phase or only playoff. In case choice group stages teams are randomly set into most possibly equally sized 
groups of size between 4 and 8 teams, depending on amount teams in tournament. Matches are automatically drawn, each team 
plays once against every team in group. After last game of group stage top 2 teams are promoted to playoff stage.
In playoff stage winner is automatically promoted into next phase, in case of semi-final, loser is set to third place 
match.
- Keep track of match results and scorers
- Group stage and playoff management

## Installation

1. Clone this repository:

   git clone https://github.com/your-username/tournament-app.git
   cd tournament-app

2. Create a virtual environment:
    
    python3 -m venv venv

3. Activate the virtual environment:
    
    On macOS and Linux:

        source venv/bin/activate

4. Install the required packages:

    pip install -r requirements.txt

5. Apply database migrations:

    python manage.py migrate

6. Run the development server:
    
    python manage.py runserver

## Usage

Access the Django admin panel by visiting http://localhost:8000/tournaments/. Log in using your superuser credentials or
create account.

Create tournaments, teams, and matches through application.