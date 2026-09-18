# Privacy Policy — RSWikiLink

**Last updated:** September 18, 2026

rs-wiki-linker ("the app") is a Reddit Developer Platform (Devvit) app that replies to comments containing `[[search terms]]` with links and short summaries from the RuneScape Wiki and the Old School RuneScape Wiki. This policy explains what data the app handles. The app is operated by Reddit user u/zpoon ("the developer").

## Summary

- The app does not collect, sell, or share personal data.
- It reads comment text only to look for `[[ ]]` search terms.
- The only information sent outside Reddit is the search term you typed, sent to the RuneScape Wiki or Old School RuneScape Wiki.
- The app stores nothing about you. It keeps one short-lived technical record per comment, described below.

## What the app reads

In subreddits where a moderator has installed the app, Reddit notifies the app when a new comment is submitted. For each comment the app receives:

- The comment text, which it scans for text inside double square brackets (`[[like this]]`)
- The comment ID and the subreddit name
- The comment author's username, used only to avoid replying to the app's own comments

Comments with no `[[ ]]` search terms are ignored, and nothing about them is kept.

## What the app stores

The app uses Devvit's built-in per-installation storage (Redis), which is provided and hosted by Reddit. It stores one entry per comment it processes:

| Data | Purpose | Retention |
|---|---|---|
| The comment ID (as a key, with the value "1") | Prevents replying twice to the same comment if Reddit delivers the same event more than once | Automatically deleted after 1 hour |

The app does not store usernames, comment text, search terms, or any user profile information.

## What the app sends outside Reddit

To build its reply, the app makes requests to two public wiki APIs:

| Domain | Purpose |
|---|---|
| `runescape.wiki` | Look up a page and its summary on the RuneScape Wiki |
| `oldschool.runescape.wiki` | Look up a page and its summary on the Old School RuneScape Wiki |

Each request contains **only the search term** written between the brackets, plus standard request information such as a User-Agent header identifying the app. The app does **not** send usernames, comment IDs, subreddit names, or full comment text to either wiki. Because the requests are made from Reddit's servers, the wikis do not receive the IP address of the person who wrote the comment.

The wikis are operated by third parties and have their own privacy practices. Please see each wiki's own policies.

## What the app posts

When a search term matches a wiki page, the app posts a public comment reply on Reddit from the app's account. That reply contains links and short summaries taken from the wiki. It is public content, like any Reddit comment, and is subject to Reddit's policies.

## What the app does not do

- It does not sell or share data with third parties (other than sending search terms to the two wikis above).
- It does not use analytics, advertising, tracking, or cookies.
- It does not use Reddit data to train machine learning or AI models.
- It does not collect data from users who are not commenting in a subreddit where the app is installed.

## Your choices

- **Opt out:** Do not include `[[ ]]` in your comment and the app will not act on it.
- **Removing a reply:** Replies are ordinary Reddit comments. Moderators of the subreddit can remove them, and you can ask the developer to have one removed.
- **Uninstalling:** Moderators can uninstall the app from their subreddit at any time, which stops all processing there.

Because the app stores no personal data beyond the 1-hour comment ID record described above, there is generally nothing to access, correct, or delete. If you have a question or request, contact the developer.

## Changes to this policy

If this policy changes materially, the updated version will be published at the same URL and the "Last updated" date will change.

## Contact

Reddit: u/zpoon (message or modmail)

Use of Reddit and the Reddit Developer Platform is also governed by Reddit's [Privacy Policy](https://www.reddit.com/policies/privacy-policy), User Agreement, and Developer Terms.
