import os
import time
import requests
import shutil
from slackclient import SlackClient
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

read_web_socket_delay = 1  # 1 second delay between reading from firehose
bot_id = os.environ.get("BOT_ID")
at_bot = "<@" + bot_id + ">"
token = os.environ.get('SLACK_BOT_TOKEN')
fname = os.environ.get("FNAME")
pic_url = os.environ.get("PIC_URL")

sc = SlackClient(token)


def handle_command(command, channel):
    r = requests.get(pic_url, stream=True)
    with open(fname, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    files = {'file': open(fname, 'rb')}
    params = {'token': token, 'channels': channel, 'filename': fname}
    requests.post('https://slack.com/api/files.upload',
                  files=files, params=params)


def check_slack_output(slack_rtm_output):
    """
    Return None unless message is directed at bot
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and at_bot in output['text']:
                # return text after the @ mention, whitespace removed
                return (output['text'], output['channel'])
    return None, None


if __name__ == "__main__":
    if sc.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = check_slack_output(sc.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(read_web_socket_delay)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
