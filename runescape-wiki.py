import praw
import re
import json
import requests

def main():
    config = get_config()
    reddit = praw.Reddit(user_agent=config['reddit']['user_agent'],
                         client_id=config['reddit']['client_id'], client_secret=config['reddit']['secret'],
                         username=config['reddit']['username'], password=config['reddit']['password'])

    subreddit = reddit.subreddit('2007scape+runescape')
    print "Now waiting for matches in comments...to quit: Ctrl+C or interrupt process."
    for comment in subreddit.stream.comments():
        process_comment(comment)

def get_config():
    """Load the config from config.json"""
    try:
        with open('config.json') as json_data_file:
            config = json.load(json_data_file)
            return config
    except IOError:
        raise IOError("Missing or unreadable config.json file")


def process_comment(comment):
    match = re.search(r'\[\[(.*?)\]\]', comment.body)
    if match:
        if comment.subreddit == "2007scape":
            response = requests.get("https://oldschool.runescape.wiki/api.php?action=opensearch&search=" + match.group(1))
            data = response.json()
            if data[1]:
                reply_text = "I have found a OSRS Wiki article for your search. \n\n **[" + data[1][0] + "](" + data[3][0] + ")** | " + data[3][0] + " \n\n --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. ^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)."
                comment.reply(reply_text)
        if comment.subreddit == "runescape":
            response = requests.get("https://runescape.wiki/api.php?action=opensearch&search=" + match.group(1))
            data = response.json()
            if data[1]:
                reply_text = "I have found a RuneScape Wiki article for your search. \n\n **[" + data[1][0] + "](" + data[3][0] + ")** | " + data[3][0] + " \n\n --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. ^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)."
                comment.reply(reply_text)


if __name__ == '__main__':
    main()