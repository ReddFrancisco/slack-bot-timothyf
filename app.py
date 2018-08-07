import os
import time
import re
import tweepy
import json
import schedule
import time
from slackclient import SlackClient
import config

slack_client = SlackClient('xoxb-410672786499-410808760530-inZwdfIzLRdAPrtNAX0lzBPH')

starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "trending"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def post_trends():
    authenticate = tweepy.OAuthHandler(config.consumer_key, config.consumer_pass)
    authenticate.set_access_token(config.access_token, config.access_token_pass)
    api = tweepy.API(authenticate)

    PASIG_WOE_ID = 1

    trend = api.trends_place(PASIG_WOE_ID)

    trend = json.loads(json.dumps(trend, indent=1))

    trend_temp = []
    for trend_loop in trend[0]["trends"]:
        trend_temp.append((trend_loop["name"]))

    trending_all = ', \n'.join(trend_temp[:10])

    return trending_all

def post_message():
    slack_client.api_call(
        "chat.postMessage",
        channel="#assignment1",
        text= post_trends()
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("timothyf Slack Bot connected and running!")
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        schedule.every().day.at("8:00").do(post_message)
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            schedule.run_pending()
            time.sleep(1)
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")