
## Private Eye Reddit bot

Private eye bot takes commands from a private message and replies to the user with the results.

It utilizes Reddit's API with the praw module and is able to find users by name and can output basic info and search through every comment made by the specified user.

# Example Usage

Currently, the bot only supports the "!search" command. You can use this command by sending a private message to your bot. The command is in the subject line, and the body of the message should contain the target's username separated by a "|" character and the keywords separated by an "," :

>subject line: !search
>
>Body: Username | keyword, keyword, keyword,

Another acceptable form of input is a username without any delimiters, although this will limit the bot to only searching basic facts about the account and the last 5 comments made by the user:

>subject: !search
>
>body: Userneame



# Deployment

To deploy this bot clone the repository

```bash
  git clone https://github.com/mitchell-j/reddit_bot
```

fill out the praw.ini file in the directory with your API information:

```
[PrivateEye]
client_id=*Reddit_API_ID
client_secret=*Reddit_API_SECRET
password=*your_bots_reddit_password
username=*your_bots_name
```

run the bot!
