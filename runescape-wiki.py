import praw
import re
import json
import requests
import os

def main():
    config = get_config()
    reddit = praw.Reddit(user_agent=config['reddit']['user_agent'],
                         client_id=config['reddit']['client_id'], client_secret=config['reddit']['secret'],
                         username=config['reddit']['username'], password=config['reddit']['password'])

    subreddit = reddit.subreddit('2007scape+runescape')
    print("Now waiting for matches in comments...to quit: Ctrl+C or interrupt process.")
    for comment in subreddit.stream.comments():
        process_comment(comment)

def get_config():
    """Load the config from config.json"""
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    try:
        with open(os.path.join(location, 'config.json')) as json_data_file:
            config = json.load(json_data_file)
            return config
    except IOError:
        raise IOError("Missing or unreadable config.json file")

def get_matches(comment):
    return re.findall(r'\[\[(.*?)\]\]', comment)

def build_reply(wiki_data, subreddit):
    results = ""
    for item in wiki_data:
        results += "**[%s](%s)** | %s \n\n >%s \n\n" % (item['result_name'], re.escape(item['result_url']), item['result_url'], item['description'])
    return "I found %s %s %s for your search. \n\n %s --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. %s " %        (len(wiki_data), "OSRS Wiki" if subreddit == "2007scape" else "RuneScape Wiki" , "articles" if len(wiki_data) > 1 else "article", results, "^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)." if subreddit == "runescape" else "")

def get_wiki_info(value, subreddit):
    api_rs_OPENSEARCH = "https://runescape.wiki/api.php?action=opensearch&search="
    api_osrs_OPENSEARCH = "https://oldschool.runescape.wiki/api.php?action=opensearch&search="
    api_rs_PARSE = "https://runescape.wiki/api.php?action=parse&prop=properties&redirects=1&format=json&page="
    api_osrs_PARSE = "https://oldschool.runescape.wiki/api.php?action=parse&prop=properties&redirects=1&format=json&page="

    try:
        if subreddit == "2007scape":
            response = requests.get(api_osrs_OPENSEARCH + value)
        else:
            response = requests.get(api_rs_OPENSEARCH + value)
        search_results = response.json()
        if search_results[1]:
            if subreddit == "2007scape":
                response = requests.get(api_osrs_PARSE + search_results[1][0])
            else:
                response = requests.get(api_rs_PARSE + search_results[1][0])
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
            except KeyError:
                print("No page found for %s" % search_results[1][0])
                return None
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def process_comment(comment):
    wiki_data = []
    match = get_matches(comment.body)
    if len(match) > 0:
        for page in match:
            if len(page) < 75:
                result = get_wiki_info(page, comment.subreddit)
                if result and len(wiki_data) < 6:
                    wiki_data.append(result)
        if wiki_data:
            comment.reply(build_reply(wiki_data, comment.subreddit))

if __name__ == '__main__':
    main()