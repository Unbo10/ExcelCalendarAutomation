#!/usr/bin/env python3
import datetime
import os.path
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# * If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_ids(service, calendar_name):
    calendar_list = service.calendarList().list().execute()
    for calendar_entry in calendar_list["items"]:
        if calendar_entry["summary"] == calendar_name:
            return calendar_entry["id"]
        
def remove_invalid_entries(df: pd.DataFrame) -> pd.DataFrame:
    df_length: int = len(df)
    rows_to_drop: list = []
    for i in range(df_length):
        if df.at[i, "Due date"] == "???" or isinstance(df.at[i, "Due date"], float):
            rows_to_drop.append(i)
        else:
            if df.at[i, "Due date"] < datetime.datetime.now():
                rows_to_drop.append(i)
    df = df.drop(rows_to_drop)
    df.reset_index(drop=True, inplace=True)
    return df

def join_date_and_time_series(df: pd.DataFrame) -> pd.DataFrame:
    for i in range(len(df)):
        date_time: datetime.datetime = df.at[i, "Due date"]
        time: datetime.datetime = df.at[i, "Time"] # * Both datetimes are apparently already datetime objects thanks to Excel
        combined_datetime = datetime.datetime.combine(date_time.date(), time)
        df.at[i, "Due date"] = combined_datetime
    return df

def get_assignments_from_xlsx(file_path: str)-> pd.DataFrame:
    df: pd.DataFrame = pd.read_excel(file_path, sheet_name="Work Sheet - Fall Term 2024", engine="openpyxl")
    selected_rows: pd.DataFrame = df.iloc[5:] # * Ignores the first 6 rows
    selected_data: pd.DataFrame = selected_rows.iloc[:, 1:6] # * Ignores the first and last 3 columns
    selected_data.rename(columns={selected_data.columns[0]: "Number", selected_data.columns[1]: "Assignment", selected_data.columns[2]: "Course code", selected_data.columns[3]: "Due date", selected_data.columns[4]: "Time"}, inplace=True)
    selected_data.reset_index(drop=True, inplace=True)
    valid_data: pd.DataFrame = remove_invalid_entries(selected_data).dropna()
    # print(valid_data)
    valid_data = join_date_and_time_series(valid_data)
    valid_data["Due date"] = pd.to_datetime(valid_data["Due date"])
    valid_data.drop(columns=["Time"], inplace=True)
    valid_data.reset_index(drop=True, inplace=True)
    return valid_data

def add_assignment_to_calendar(service, calendar_id, assignment: dict):
    course_name: dict = {
        "CHG 2312": "Fluid Flow",
        "CHG 2317": "Introduction to Chemical Process Analysis and Design",
        "CHM 2120": "Organic Chemistry II",
        "GNG 1103": "Engineering Design",
        "MAT 2384": "Ordinary Differential Equations and Numerical Methods"
    }
    course_color_id: dict = {
        "CHG 2312": 11,
        "CHG 2317": 6,
        "CHM 2120": 3,
        "GNG 1103": 5,
        "MAT 2384": 2
    }
    event = {
        "status": "confirmed",
        "summary": assignment['Assignment'],
        "description": f"{course_name[assignment['Course code']]} ({assignment['Course code']}) task #{assignment['Number']}",
        "location": "University of Ottawa",
        "colorId": course_color_id[assignment["Course code"]],
        "start": {
            "dateTime": assignment["Due date"].isoformat(),
            "timeZone": "America/Toronto",
        },
        "end": {
            "dateTime": (assignment["Due date"] + pd.Timedelta(hours=1.5)).isoformat(),
            "timeZone": "America/Toronto",
        },
        "reminders": {
        "useDefault": False,
        "overrides": [
                {"method": "email", "minutes": 24 * 60},
                {"method": "popup", "minutes": 180},
            ],
        },
    }
    new_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    # print(f"Event '{assignment['Assignment']}' created:", new_event.get("htmlLink"))

def update_csv(new_assignments: list):
    current_assignments_df: pd.DataFrame = pd.read_csv("assignments.csv")
    current_assignments_df["Due date"] = pd.to_datetime(current_assignments_df["Due date"])
    new_assignments_df: pd.DataFrame = pd.DataFrame(new_assignments)
    updated_assignments_df: pd.DataFrame = pd.concat([current_assignments_df, new_assignments_df], ignore_index=True)
    updated_assignments_df.sort_values(by="Due date", ascending=True, inplace=True)
    updated_assignments_df.to_csv("assignments.csv", index=False)

def main():
    # * AUTHENTICATION
    creds = None
    # * The file token.json stores the user's access and refresh tokens, and is
    # * created automatically when the authorization flow completes for the first
    # * time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # * If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        
    try:
        service = build("calendar", "v3", credentials=creds) # * Service to interact with the API

        calendar_name = "Uni tasks"
        calendar_id = get_calendar_ids(service, calendar_name)
        if calendar_id is None:
            raise ValueError(f"Calendar '{calendar_name}' not found")
        assignments_df: pd.DataFrame = get_assignments_from_xlsx("Fall_2024.xlsx").sort_values(by="Due date", ascending=True)
        assignments_df = assignments_df.dropna()
        assignment_history_df: pd.DataFrame = pd.read_csv("assignments.csv")
        assignment_history_df["Due date"] = pd.to_datetime(assignment_history_df["Due date"])
        # * Reset the index to avoid problems when comparing the dataframes
        assignments_df = assignments_df.reset_index(drop=True)
        assignment_history_df = assignment_history_df.reset_index(drop=True)
        # print(assignments_df)

        # * Check if the assignment is already in the calendar
        new_assignments: list = []
        for i in range(len(assignments_df)):
            assignment = assignments_df.at[i, "Assignment"]
            # * Add the assignment to the calendar in case it is not there
            if assignment not in assignment_history_df["Assignment"].values:
                add_assignment_to_calendar(service, calendar_id, assignments_df.iloc[i])
                new_assignments.append(assignments_df.iloc[i])
        if len(new_assignments) > 0:
            update_csv(new_assignments)
        else:
            print("No new assignments to add")

    except HttpError as error:
        print(f"An error occurred: {error}")
    
    except ValueError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()