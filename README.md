# vaccine-scraper
Scrapes walgreens and notifies via IFTTT when vaccine appointments are available. Deploys to AWS Lambda. 
Contact: stopaustin7@gmail.com

IFTTT Setup:
1) Create a free IFTTT account
2) Create an applet which receives a webhook request with event name "notifier"
3) Set up push notifications (or any other notifying platform), using value1/value2/value3 as defined in lambda_function.py
4) Save your webhook API key
5) Download the IFTTT app onto your phone, with push notifications enabled

AWS Setup:
1) Create a free AWS account
2) Create a new lambda function
3) Once created, upload the zipped lfv12 file in the "Code" tab
4) Set up enviornment variable "ZIP_CODES" with a comma separated list of all zip codes you wish to scan
5) Set up environment variable IFTTT_KEY with your API key, as saved in IFTTT Setup
6) Test your code by sending a test event 
7) If everything checks out, set up an EventBridge trigger with a cron job
 -> You can run this every 5 minutes without exceeding your monthly Lambda allowance
