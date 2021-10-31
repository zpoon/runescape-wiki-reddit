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

    subreddit = reddit.subreddit(config['reddit']['subreddit'])
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
    sites = []
    for item in wiki_data:
        sites.append(item['site'])
        results += "**[%s](%s)** | %s \n\n >%s \n\n" % (item['result_name'], re.escape(item['result_url']), item['result_url'], item['description'])
    if sites.count('osrs') >= 1 and sites.count('rs3') >= 1:
        headline = "%s RuneScape Wiki + %s OSRS Wiki %s" % (sites.count('rs3'), sites.count('osrs'), "articles" if sites.count('osrs') > 1 else "article")
    elif sites.count('osrs') >= 1:
        headline = "%s OSRS Wiki %s" % (sites.count('osrs'), "articles" if sites.count('osrs') > 1 else "article")
    else:
        headline = "%s RuneScape Wiki %s" % (sites.count('rs3'), "articles" if sites.count('rs3') > 1 else "article")
    if truncate == 0:
        return "I found %s for your search. \n\n %s --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. ^^^| **^^^NEW:** ^^^use ^^^optional ^^^modifiers ^^^(rs3:osrs) ^^^to ^^^specify ^^^wiki ^^^sites ^^^in ^^^searches. %s " %        (headline, results, "^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)." if subreddit == "runescape" else "")
    else:
        return "I found %s for your search. *(%s %s ignored. Limit 6 results per comment.)* \n\n %s --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. ^^^| **^^^NEW:** ^^^use ^^^optional ^^^modifiers ^^^(rs3:osrs) ^^^to ^^^specify ^^^wiki ^^^sites ^^^in ^^^searches. %s " %        (headline, truncate, "search was" if truncate == 1 else "searches were", results, "^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)." if subreddit == "runescape" else "")
# Access the rs-wiki api to get relevant data per search term
def get_wiki_info(value, site):
    # RS3 and OSRS searches use different api endpoints. 
    # OPENSEARCH takes a search term and finds a matching rs-wiki page, then returns it.
    api_rs = "https://runescape.wiki/api.php"
    api_osrs = "https://oldschool.runescape.wiki/api.php"
    params_OPENSEARCH = {'action': 'opensearch', 'search': value}
    params_PARSE = {'action': 'parse', 'prop': 'properties', 'redirects': 1, 'format': 'json'}
    try:
        if site == "osrs":
            response = requests.get(api_osrs, params=params_OPENSEARCH)
        else:
            response = requests.get(api_rs, params=params_OPENSEARCH)
        search_results = response.json()
        if search_results[1]:
            params_PARSE['page'] = search_results[1][0]
            if site == "osrs":
                response = requests.get(api_osrs, params=params_PARSE)
            else:
                response = requests.get(api_rs, params=params_PARSE)
            description_page = response.json()
            try:
                if description_page['parse']['title'] not in "Nonexistence":
                    for prop in description_page['parse']['properties']:
                        if prop['name'] == "description":
                            description = prop['*']
                    return {
                        'result_name': search_results[1][0],
                        'result_url': search_results[3][0],
                        'description': description,
                        'site': site
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
    rs_modifiers = ["r", "rs3", "rsw", "rs", "runescape"]
    os_modifiers = ["o", "2007", "osrs", "osw", "osrsw", "os", "oldschool", "2007scape", "oldschoolrunescape"]
    wiki_data = []
    match = get_matches(comment.body)
    # Check for [[ ]] trigger presence
    if len(match) > 0:
        for page in match:
            # Simple check to make sure search term isn't spam although it shouldn't affect anything
            if len(page) < 75:
                # Check for site modifiers
                mod_split = page.split(":", 1)
                if len(mod_split) == 2:
                    if mod_split[0] in rs_modifiers:
                        page = mod_split[1]
                        site = 'rs3'
                    elif mod_split[0] in os_modifiers:
                        page = mod_split[1]
                        site = 'osrs'
                    # Case when modifier found but it's not a site one
                    else:
                        page = mod_split[1]
                        site = 'rs3' if comment.subreddit == 'runescape' else 'osrs'
                # Default case when no modifier
                else:
                    site = 'rs3' if comment.subreddit == 'runescape' else 'osrs'
                result = get_wiki_info(page, site)
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