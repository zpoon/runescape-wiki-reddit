# runescape-wiki-reddit: Simple bot that replies to searches in reddit comments with relevant rs-wiki links
# author: Nicholas Torkos (/u/zpoon)
import praw
import re
import time
import json
import requests
import os
# Initialize praw object with config info and watch comment stream
def main():
    config = get_config()
    reddit = praw.Reddit(user_agent=config['reddit']['user_agent'],
                         client_id=config['reddit']['client_id'], client_secret=config['reddit']['secret'],
                         username=config['reddit']['username'], password=config['reddit']['password'])

    subreddit = reddit.subreddit('2007scape+runescape')
    print("Now waiting for matches in comments...to quit: Ctrl+C or interrupt process.")
    while True:
        try:
            for comment in subreddit.stream.comments():
                process_comment(comment)
        # Handle when reddit doesn't want to co-operate
        except Exception as e:
            if '503' in str(e):
                print("Reddit server is having issues, waiting...")
                time.sleep(30)
                continue
# Get config data from config.json
def get_config():
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    try:
        with open(os.path.join(location, 'config.json')) as json_data_file:
            config = json.load(json_data_file)
            return config
    except IOError:
        raise IOError("Missing or unreadable config.json file")
# Search comment for [[ ]] terms
def get_matches(comment):
    return re.findall(r'\[\[(.*?)\]\]', comment)
# Build the reply with wiki data
def build_reply(wiki_data, subreddit, truncate):
    results = ""
    for item in wiki_data:
        results += "**[%s](%s)** | %s \n\n >%s \n\n" % (item['result_name'], re.escape(item['result_url']), item['result_url'], item['description'])
    if truncate == 0:
        return "I found %s %s %s for your search. \n\n %s --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. %s " %        (len(wiki_data), "OSRS Wiki" if subreddit == "2007scape" else "RuneScape Wiki" , "articles" if len(wiki_data) > 1 else "article", results, "^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)." if subreddit == "runescape" else "")
    else:
        return "I found %s %s %s for your search. *(%s %s ignored. Limit 6 results per comment.)* \n\n %s --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. %s " %        (len(wiki_data), "OSRS Wiki" if subreddit == "2007scape" else "RuneScape Wiki" , "articles" if len(wiki_data) > 1 else "article", truncate, "search was" if truncate == 1 else "searches were", results, "^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)." if subreddit == "runescape" else "")
# Access the rs-wiki api to get relevant data per search term
def get_wiki_info(value, subreddit):
    # RS3 and OSRS searches use different api endpoints. 
    # OPENSEARCH takes a search term and finds a matching rs-wiki page, then returns it.
    api_rs_OPENSEARCH = "https://runescape.wiki/api.php"
    api_osrs_OPENSEARCH = "https://oldschool.runescape.wiki/api.php"
    # PARSE takes the returned rs-wiki page and gets the full page title, URL, and a short description
    api_rs_PARSE = "https://runescape.wiki/api.php"
    api_osrs_PARSE = "https://oldschool.runescape.wiki/api.php"
    params_OPENSEARCH = {'action': 'opensearch', 'search': value}
    params_PARSE = {'action': 'parse', 'prop': 'properties', 'redirects': 1, 'format': 'json'}
    try:
        if subreddit == "2007scape":
            response = requests.get(api_osrs_OPENSEARCH, params=params_OPENSEARCH)
        else:
            response = requests.get(api_rs_OPENSEARCH, params=params_OPENSEARCH)
        search_results = response.json()
        if search_results[1]:
            params_PARSE['page'] = search_results[1][0]
            if subreddit == "2007scape":
                response = requests.get(api_osrs_PARSE, params=params_PARSE)
            else:
                response = requests.get(api_rs_PARSE, params=params_PARSE)
            description_page = response.json()
            try:
                if description_page['parse']['title'] not in "Nonexistence":
                    for prop in description_page['parse']['properties']:
                        if prop['name'] == "description":
                            description = prop['*']
                    return {
                        'result_name': search_results[1][0],
                        'result_url': search_results[3][0],
                        'description': description
                    }
                else:
                    return None
            # Handle searches with no results
            except KeyError:
                print("No page found for %s" % search_results[1][0])
                return None
        else:
            return None
    # Handle HTTP errors accessing rs-wiki
    except requests.exceptions.RequestException as e:
        print(e)
        return None
# Recieve new comment from stream, send it to regex search, and reply to user if term exists
def process_comment(comment):
    wiki_data = []
    match = get_matches(comment.body)
    # Check for [[ ]] trigger presence
    if len(match) > 0:
        for page in match:
            # Simple check to make sure search term isn't spam although it shouldn't affect anything
            if len(page) < 75:
                result = get_wiki_info(page, comment.subreddit)
                if result and len(wiki_data) < 6:
                    wiki_data.append(result)
        if wiki_data:
            try:
                # Only handle first 6 search terms to prevent spam
                if len(match) > 6:
                    results_ignored = len(match) - 6
                    comment.reply(build_reply(wiki_data, comment.subreddit, results_ignored))
                else:
                    comment.reply(build_reply(wiki_data, comment.subreddit, 0))
            # Another handler for when reddit isn't cooperating
            except Exception as e:
                if '503' in str(e):
                    print("Reddit server is having issues, waiting...")
                    time.sleep(30)

if __name__ == '__main__':
    main()