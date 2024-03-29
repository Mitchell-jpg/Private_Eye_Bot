![image](https://github.com/Mitchell-jpg/Private_Eye_Bot/assets/91237766/efb5f80b-eacc-4562-a8d5-e60ed18eadf6)


Private eye bot takes commands from a private message and replies to the user with the results.

It utilizes Reddit's API with the praw module and is able to find users by username and can output basic info and search through every comment made by the specified user and can even filter by keyword!

## CLI mode usage

When starting the program, you will begin in CLI mode. Here you have the commands: 'search', 'help', 'quit', and 'start bot'.

The search command allows you to search for a users basic info and can access any comments made by the user when supplied with (a) keyword(s). If no keywords are supplied you can receive the last 5 comments made by the user.

Performing a search will output the result(s) in the 'results.txt' file.

Optionally, you may start the bot using the 'start bot' command.  This allows the bot to receive requests via private messaging.

## Bot Mode Usage

Currently, the bot supports the "!search" command. You can use this command by sending a private message to your bot. The command is in the subject line, and the body of the message should contain the target's username separated by a "|" character and the keywords separated by an "," :

>subject line: !search
>
>Body: Username | keyword, keyword, keyword,

Another acceptable form of input is a username without any delimiters, although this will limit the bot to only searching basic facts about the account and the last 5 comments made by the user:

>subject: !search
>
>body: Userneame



## Deployment

To deploy this bot clone the repository

```bash
  git clone https://github.com/mitchell-j/reddit_bot
```

Fill out the praw.ini file in the directory with your API information:

```
[PrivateEye]
client_id=*Reddit_API_ID
client_secret=*Reddit_API_SECRET
password=*your_bots_reddit_password
username=*your_bots_name
```

Ensure that required dependencies are downloaded:

```
python3 -m pip install -r requirements.txt
```

run the bot!
