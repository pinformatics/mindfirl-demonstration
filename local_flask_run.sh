cd /Users/jonathonlowe/Documents/Repositories/mindfirl-display_results
source resultsEnv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
deactivate
