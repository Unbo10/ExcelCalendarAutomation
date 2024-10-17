#!/bin/bash

FILE_TO_TRACK="/home/inbo10/Documents/ExcelCalendarAutomation/Fall_2024.xlsx"
FILE_TO_RUN="/home/inbo10/Documents/ExcelCalendarAutomation/main.py"
LOG_FILE="/home/inbo10/Documents/ExcelCalendarAutomation/script_log.txt"
DEBOUNCE_TIME=5 # * How much time should there be between the last execution and the last change detected by inotifywait.
LAST_RUN=0 # * Further in the code, it keeps track of when was the last execution of the Python script
LOCKFILE="/home/inbo10/Documents/ExcelCalendarAutomation/auto_run_linux.lock"

# Trap to remove the lock file on exit
trap 'rm -f "$LOCKFILE"; exit' INT TERM EXIT

# * Lock files prevent multiple tasks running the same script simultaneously
# * Check if the lock file exists
if [ -e "$LOCKFILE" ]; then
    echo "Script is already running. Exiting..."
    exit 1
fi

# Create the lock file
touch "$LOCKFILE"

# * Creates the log file in case it wasn't created before.
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    echo "Log file created at $(date)" >> "$LOG_FILE"
fi

# * This does pretty much the same as the Mac script:
# * It inputs the changes made to a file to a while loop that reads them and executes something.
# * The only difference is that in Linux the "command-line utility" inotifywait is used to track the changes.
# * The `--monitor` or `-m` flag keeps inotifywait running even after the first event (set of changes).
# * The `--event modify` or `-e modify` tells inotifywait what to look for: changes in FILE_TO_TRACK.
fswatch -o "$FILE_TO_TRACK" | while read -r event; do
    echo "Changes detected"
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - LAST_RUN))
    echo "$TIME_DIFF"
    if [ "$TIME_DIFF" -ge "$DEBOUNCE_TIME" ]; then
        echo "Executing..."
        echo "Starting script at $(date) with PID $$" >> "$LOG_FILE"
        python3 "$FILE_TO_RUN" "$FILE_TO_TRACK" >> "$LOG_FILE" 2>&1
        echo "Script finished at $(date)" >> "$LOG_FILE"
        LAST_RUN=$CURRENT_TIME
    fi
done