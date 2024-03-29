from prawcore.exceptions import TooManyRequests, NotFound
from reddit import RedditUserData



class Inbox:
    """ A class to manage the bot's inbox """

    def __init__(self, reddit):
        self.reddit = reddit
        self.reddit_user_data = RedditUserData(self.reddit)
    
    def setup_bot_owner(self):
        self.bot_owner = input("Enter the bot owner's username (allows !shutdown message from entered username):")

    def check_messages(self):
        """Monitor bot's inbox for keywords"""
        # Initialize unread messages
        self.inbox = self.reddit.inbox.unread()

        # Begin monitoring inbox for keywords.
        for message in self.inbox:
                
            # Print recieved message into console.
            print("\nmessage recieved\n"             +
                  f"From: {message.author}\n"      +
                  f"Subject: {message.subject}\n"  +
                  message.body + "\n\n"
                  )
            
            self.search_for_commands(message)
    
    def search_for_commands(self, message):
        """Search for keywords in messages"""
           
        # Allow bot owner to shutdown remotley; Block others who try.
        if message.subject.lower() == "!shutdown": 
            if message.author != self.bot_owner:
                print(f"Blocked user {message.author} for trying to shutdown bot.")
                message.mark_read()
                message.block()
                
            print("shutting down bot")
            self.bot_active = False
            message.mark_read()
            
        elif message.subject.lower() == "!search" or "re: !search":

            body = message.body
      
            # Check if there are multiple keywords; format and check for comments.
            username = self.parse_username_from_body(message, body)

            # Check if username exists.
            if self.check_user_exists(username) == False:
                print(f" user:{username} doesn't exist.  notifying {message.author}")
                message.reply("This user does not exist.  Please try again.")
                message.mark_read()
                
            else:

                keywords = self.parse_keywords_from_body(body)
                collected_comments = self.reddit_user_data._check_user_comments(username, keywords)
                formatted_comments = self.reddit_user_data.format_comments(collected_comments)
   
                # Reply to sender
                message.reply(f"{self.reddit_user_data.get_user_info(username)} \n {formatted_comments}")
                message.mark_read()
                print(f"Infromation on {username} provided to {message.author}.\nResuming inbox monitoring\n\n")
                
        else:
            message.reply(f"Invalid format or unsupported command.\n\nI currently only support the *'!search'*")
            message.mark_read()
            print(f"sent try again message to {message.author}")

    def check_user_exists(self, username):
        """ Checks is user exists. returns T or F """
        #Check if user exists.
        print(f"\nsearching for {username}..")
        username_check = self.reddit_user_data.get_user_info(username)
                    
        if not username_check:
            return False
        else: 
            return True
        
    def parse_username_from_body(self, message, body):
        """ Parses a message body for a username"""

        if "|" in body:
            sepmsg = body.split("|")

            # If the delimiter splits in anything other than two the format must be wrong.
            if len(sepmsg) != 2:
                message.reply("Wrong format used.  Seperate username and keywords using '|' and seperate keywords by ','")
            else:
                username = sepmsg[0].strip(" ").lower()
                return username
        else:
            username = body.strip(" ").lower()
            return username

    def parse_keywords_from_body(self, body):
        """ Parses a message body for keywords. """
        if "|" in body:
            sepmsg = body.split("|")

            if "," in sepmsg[1]:
                keywords = sepmsg[1].split(",")
                for i in range(len(keywords)):
                    keywords[i] = keywords[i].strip().lower()
                return keywords
                                    
            else:
                keywords = sepmsg[1]
                for keyword in keywords:
                    keyword.strip(" ").lower()
                return keywords
        else:
            keywords = None
            return keywords


    