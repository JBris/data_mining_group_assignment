#!/usr/bin/env bash

usage() {
    echo '
    ###############################################################
    Help:

    * Description:
        - Imports the contents of a CSV file into InfluxDB.
    * Usage:
        - ./import_data.sh [csv file] [influxdb host]

    ###############################################################
    '
}

if [ "$#" -ne 2 ]; then
    usage
    exit 100
fi

csv_to_influxdb="$(pwd)/csv-to-influxdb/csv-to-influxdb.py"
file="$1"
host="$2"

if [ $(command -v python3 >/dev/null 2>&1 && echo 1) -eq 1 ]; then
    command=python3
elif [ $(command -v python3 >/dev/null 2>&1 && echo 1) -eq 1 ]; then
    command=python
else
    echo "Error: Python is not available."
    exit 100
fi

"$command" "$csv_to_influxdb" -i "$file" -s "$host" -tc date_time -tf '%d/%m/%Y %H:%M' --metricname usage --fieldcolumns usage --dbname project --create -b 5000 --tagcolumns channel_id,channel_key,site,channel_pair
