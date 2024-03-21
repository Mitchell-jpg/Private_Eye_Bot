
# Private Eye Reddit bot

Private eye bot takes commands from a private message and replies to the user with the results.

It utilizes Reddit's API with the praw module and is able to find users by name and can output basic info and search through every comment made by the specified user.


Currently the bot only supports the !search command.  You can utilize this command by sending a private message to your bot with 

subject line: !search 

Body: Username

This will search the username and reurn basic info along witth the 5 most recent comments.






## Deployment

To deploy this bot clone the repository

```bash
  git clone https://github.com/mitchell-j/reddit_bot
```

Create a praw.ini file and place it in directory

```
[DEFAULT]
# A boolean to indicate whether or not to check for package updates.
check_for_updates=True

# Object to kind mappings
comment_kind=t1
message_kind=t4
redditor_kind=t2
submission_kind=t3
subreddit_kind=t5
trophy_kind=t6

# The URL prefix for OAuth-related requests.
oauth_url=https://oauth.reddit.com

# The amount of seconds of ratelimit to sleep for upon encountering a specific type of 429 error.
ratelimit_seconds=5

# The URL prefix for regular requests.
reddit_url=https://www.reddit.com

# The URL prefix for short URLs.
short_url=https://redd.it

# The timeout for requests to Reddit in number of seconds
timeout=16

[PrivateEye]
client_id=*Reddit_API_ID
client_secret=*Reddit_API_SECRET
password=*your_bots_reddit_password
username=*your_bots_name
```

run the bot!