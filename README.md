# Timebook
Simple Flask application for tracking how you spend your time,
slightly inspired by Traggo - a tag-based time tracking tool.

![](.images/screenshot.png)


## Features
- time tracking based on free text description, end-time and duration
- list timespans by date, or show all
- generic "Archived" status, to mark already reported/invoiced/whatever records


## Virtual environment

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt


## Run the application

    flask run --host=0.0.0.0 --debug


## Command-line interface

    flask cli --help
    flask cli time-delete --help
    flask cli time-prune --help


## Credits
CSS style based on [ajusa/lit](https://github.com/ajusa/lit), a ridiculously
small responsive css framework.
