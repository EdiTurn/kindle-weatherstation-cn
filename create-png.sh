#!/bin/sh

PWD=$(pwd)
export LD_LIBRARY_PATH=$PWD/lib
export FONTCONFIG_FILE=$PWD/fonts.conf
SESSION_LOG="/tmp/weather_session.log"
STATUS=${1:-0} 

if [ "$STATUS" -eq 0 ]; then
    python3 -u $PWD/weather2svg.py >> $SESSION_LOG 2>&1
    STATUS=$?
fi

if [ "$STATUS" -ne 0 ]; then
    echo "`date '+%Y-%m-%d_%H:%M:%S'`: Failure detected with status $STATUS, generating error SVG" >> $SESSION_LOG
    python3 -u $PWD/error2svg.py $STATUS $SESSION_LOG >> $SESSION_LOG 2>&1
fi

$PWD/bin/rsvg-convert --background-color=white -o kindle-weather.png weather-script-output.svg >> $SESSION_LOG 2>&1
