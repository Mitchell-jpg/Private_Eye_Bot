from prawcore.exceptions import TooManyRequests, NotFound
from reddit import RedditUserData
import time



class Inbox:
    """
     A class to manage the bot's inbox 
     
     Requires praw.reddit instance to be passed.
     
     """

    def __init__(self, reddit) -> None:
        """ Initializes reddit instance and userdata acess"""
        self.reddit = reddit
        self.reddit_user_data = RedditUserData(self.reddit)

    def setup_bot_owner(self) -> None:
        """ 
        prompts user to setup bot owner

        Bot owner will be the only one allowed to issue the !shutdown command.
        """
        self.bot_owner = input("Enter the bot owner's username (allows !shutdown message from entered username):")

    def check_messages(self) -> None:
        """Monitor bot's inbox for keywords"""

        # Initialize unread messages
        self.inbox = self.reddit.inbox.unread()

        # Begin monitoring inbox for keywords.
        max_retries = 3
        attempts = 0
        success = False
        
        while not success and attempts < max_retries:
            try:
                for message in self.inbox:
                        
                    # Print recieved message into console.
                    print("\nmessage recieved\n"             +
                        f"From: {message.author}\n"      +
                        f"Subject: {message.subject}\n"  +
                        message.body + "\n\n"
                        )
                    
                    self._search_for_commands(message)

                success = True
            
                

            except TooManyRequests as e:
                    attempts += 1
                    print(f"{e}: waiting 20 seconds and trying again.. attempt {attempts} of {max_retries}\n")
                    time.sleep(20)
                    
            
        
    def _search_for_commands(self, message) -> None:
        """
        Search for keywords in messages.

        Requires an instance of the message.

        This function will reply to users and mark messages as read.

        messages doc: https://praw.readthedocs.io/en/stable/code_overview/models/message.html
        """
           
        # Allow bot owner to shutdown remotley; Block others who try.
        if message.subject.lower() == "!shutdown": 
            if message.author != self.bot_owner:
                print(f"Blocked user {message.author} for trying to shutdown bot.")
                message.mark_read()
                message.block()
                
            print("shutting down bot")
            message.mark_read()

            #This exception is used to break free from the loop in private_eye.py
            raise Exception
            
        
        elif message.subject.lower() == "!search" or "re: !search":

            body = message.body
      
            # Check if there are multiple keywords; format and check for comments.
            username = self._parse_username_from_body(message, body)

            # Check if username exists.
            if self.reddit_user_data.check_user_exists(username) == False:

                # Notify message author if the user does not exist
                print(f" user:{username} doesn't exist.  notifying {message.author}")
                message.reply("This user does not exist.  Please try again.")
                message.mark_read()
                
            else:
                # process keywords from the body of the message
                keywords = self._parse_keywords_from_body(body)
                # Collect comments, filtered by keywords if supplied
                formatted_comments = self.reddit_user_data.check_user_comments(username, keywords)
                # Reply to sender
                message.reply(f"{self.reddit_user_data.get_user_info(username)} \n {formatted_comments}")
                message.mark_read()
                print(f"Infromation on {username} provided to {message.author}.\nResuming inbox monitoring\n\n")
                
        else:
            # If user types something wrong in the subject line, send user instructions.
            message.reply(f"Invalid format or unsupported command.\n\nI currently only support the *'!search'*")
            message.mark_read()
            print(f"sent try again message to {message.author}")

   
        
    def _parse_username_from_body(self, message, body: str) -> str:
        """ 
        Parses a message body for a username.

        requires message instance.
        """

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

    def _parse_keywords_from_body(self, body: str) -> list:
        """ 
        Parses a message body for a keywords, returns list.
        """
        if "|" not in body:
            keywords = None
            return keywords
        
        sepmsg = body.split("|")
        keywords = sepmsg[1].split(".")

        if len(keywords) > 1:
            for i in range(len(keywords)):
                keywords[i] = keywords[i].strip(" ").lower()
            return keywords
                            
        else:
            # format singular keyword and place it in list.
            for keyword in keywords:
                keyword.strip(" ").lower()
            return keywords
        


    