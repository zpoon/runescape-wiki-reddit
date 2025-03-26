# runescape-wiki-reddit
A simple reddit bot that links relevant RuneScape wiki page to comments. Supports contextual replies in /r/runescape and /r/2007scape.

Enclose search terms in two square brackets `[[ ]]` in a comment for the bot to find a relevant Wiki article, grab a quick summary, and link it in a reply.

Example: `[[rune platebody]]`

#### Optional:
Specify a modifier before the search term to overrride the default site the search will complete in (default is based on the subreddit the comment was made in). This can allow you to search the OSRS wiki in the /r/runescape subreddit and vice-versa.

Example: `[[os:rune platebody]]`

- RuneScape: `r, rs3, rsw, rs, runescape`
- Old School RuneScape: `o, 2007, osrs, osw, osrsw, os, oldschool, 2007scape, oldschoolrunescape`

# Setup

### config.json

The bot loads configuration data from file `config.json` that holds reddit OAuth secrets and what subreddit is the bot running on. You can get these values by creating your own app on Reddit [here](https://www.reddit.com/prefs/apps).

An example config.json would look like this:
```
{
    "reddit": {
        "client_id": "client_id_here",
        "secret": "secret_here",
        "password": "password_here",
        "username": "username_here",
        "user_agent": "Reddit bot for <subreddit> by /u/zpoon",
        "subreddit": "subreddit_here"
    }
}
```

### Dependencies

The bot uses a number of dependencies that can be installed with `pip`.  Namely `praw` to inteact with the Reddit API and `requests` to create HTTP requests to the RuneScape Wiki API. 

# Donate
I currently run /u/RSWikiLink on my own hardware. I'm more than happy to continue this, but if you found it helpful and want to help with the small costs involved, then feel free to chip in :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=A5KFGHFLNP6HS&currency_code=USD&source=url)
