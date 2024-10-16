# Excel-Google Calendar integration and automation

This project was made to learn about the use of Google's APIs while remembering the use of pandas in Excel files. The project consists of a Python script that reads a list of tasks from a particular sheet from an Excel file and creates events in a Google Calendar (to which the user logged in previously).

It is an excesively specific project, but it can serve as a base to other projects and to build an even broader automation system.

## Requirements

- Python 3.6 or higher
- Pandas library
- Google account
- Google Calendar API enabled

## How to use

1. Clone the repository.
2. Install Python if you don't have installed (you can check by running the command `python3 --version`).
3. Install the required libraries by running the command `pip install -r requirements.txt`.
4. Enable the Google Calendar API in the Google Cloud Platform.
5. Download the credentials file and save it in the same directory as the script.
6. Copy your Excel file to the same directory as the script.
7. Run the script by running the command `python3 main.py`, or if you want to make it an executable, follow this steps:
   1. Make the script executable by running the command `chmod +x main.py`.
   2. Run the script by running the command `./main.py`.

Hope you find it useful <3.