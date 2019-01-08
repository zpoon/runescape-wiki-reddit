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
    testcase = "This is a test case with multiple matches. While guthix Sleeps and Slayer"
    print "Now waiting for matches in comments...to quit: Ctrl+C or interrupt process."
    # for comment in subreddit.stream.comments():
    #     process_comment(comment)
    match = re.findall(r'\[\[(.*?)\]\]', testcase)
    print len(match)

def get_config():
    """Load the config from config.json"""
    try:
        with open('config.json') as json_data_file:
            config = json.load(json_data_file)
            return config
    except IOError:
        raise IOError("Missing or unreadable config.json file")

def get_matches(comment):
    return re.findall(r'\[\[(.*?)\]\]', comment)

def build_reply(wiki_data, subreddit):
    if subreddit == "2007scape":
        wiki_type = "OSRS Wiki"
    else:
        wiki_type = "RuneScape Wiki"
    return "I found 1 %s article for your search. \n\n **[%s](%s)** | %s \n\n >%s \n\n --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. ^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)." %        (wiki_type, wiki_data['result_name'], wiki_data['result_url'], wiki_data['result_url'], wiki_data['description'])

def get_wiki_info(value, subreddit):
    api_rs_OPENSEARCH = "https://runescape.wiki/api.php?action=opensearch&search="
    api_osrs_OPENSEARCH = "https://oldschool.runescape.wiki/api.php?action=opensearch&search="
    api_rs_PARSE = "https://runescape.wiki/api.php?action=parse&redirects=1&format=json&page="
    api_osrs_PARSE = "https://oldschool.runescape.wiki/api.php?action=parse&redirects=1&format=json&page="

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
                    description = description_page['parse']['properties'][1]['*']
                    return {
                        'result_name': search_results[1][0],
                        'result_url': search_results[3][0],
                        'description': description
                    }
                else:
                    return None
            except KeyError:
                print "No page found for %s" % search_results[1][0]
                return None
        else:
            return None
    except requests.exceptions.RequestException as e:
        print e
        return None



def process_comment(comment):
    match = get_matches(comment.body)
    if len(match) > 0:
        for page in match:
            if comment.subreddit == "2007scape":
                response = requests.get("https://oldschool.runescape.wiki/api.php?action=opensearch&search=" + match.group(1))
                data = response.json()
                if data[1]:
                    parse_page = requests.get("https://oldschool.runescape.wiki/api.php?action=parse&redirects=1&format=json&page=" + data[1][0])
                    page_json = parse_page.json()
                    try:
                        if page_json['parse']['title'] not in "Nonexistence":
                            description = page_json['parse']['properties'][1]['*']
                            reply_text = "I found 1 OSRS Wiki article for your search. \n\n **[" + data[1][0] + "](" + data[3][0] + ")** | " + data[3][0] + " \n\n >" + description + " \n\n --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. ^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)."
                            comment.reply(reply_text)
                    except KeyError:
                        print "No page found: " + match.group(1)
            if comment.subreddit == "runescape":
                response = requests.get("https://runescape.wiki/api.php?action=opensearch&search=" + match.group(1))
                data = response.json()
                if data[1]:
                    parse_page = requests.get("https://runescape.wiki/api.php?action=parse&redirects=1&format=json&page=" + data[1][0])
                    page_json = parse_page.json()
                    try:
                        if page_json['parse']['title'] not in "Nonexistence":
                            description = page_json['parse']['properties'][1]['*']
                            reply_text = "I found 1 RuneScape Wiki article for your search. \n\n **[" + data[1][0] + "](" + data[3][0] + ")** | " + data[3][0] + " \n\n >" + description + " \n\n --- \n\n **^^^RuneScape ^^^Wiki ^^^linker** ^^^| ^^^This ^^^was ^^^generated ^^^automatically. ^^^| ^^^View ^^^me ^^^on ^^^[GitHub](https://github.com/zpoon/runescape-wiki-reddit)."
                            comment.reply(reply_text)
                    except KeyError:
                        print "No page found: " + match.group(1)


if __name__ == '__main__':
    main()