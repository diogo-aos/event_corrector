install dependencies

make sure a "app_credentials.json" file exists with the credentials created for your project, follow Google guide

run once, from script directory, to authenticate

after first run, a calendar_tags.json file will be created, and a token.pickle file will store auth credentials

add tags for each calendar in json format

use cron to run script (make sure to run script for is directory for relative paths to work)

crontab -e 

e.g. to run script every minute
* * * * * cd /absolute/path/script/directory && python3 event_corrector.py

service cron reload 
