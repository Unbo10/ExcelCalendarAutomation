#!/bin/bash

FILE_TO_TRACK="/home/inbo10/Documents/ExcelCalendarAutomation/Fall_2024.xlsx"
FILE_TO_RUN="/home/inbo10/Documents/ExcelCalendarAutomation/main.py"

# * What this will do is to output the changes of FILE_TO_TRACK as a single input to the commands after the pipe (|).
# * The while loop will make sure that the actions are only 
# * The `read` command will read the standard output that's now the input from the pipe.
# * The `-r` flag will make sure the backslashes are not escape characters, so even if there is one in the input, it won't break the line or finish execution.
# * The `event` variable will store the input given to `read`. This is just so that there is somewhere `read` can flush the data to.
# * Finally, the indented lines after `do` will be a new shell prompt to be executed.
fswatch -o "$FILE_TO_TRACK" | while read -r event; do
    python3 "$FILE_TO_RUN" "$FILE_TO_TRACK"
done