import sys
import praw
import time
import requests
from prawcore.exceptions import NotFound, TooManyRequests, InvalidToken
from inbox import Inbox
from reddit import RedditUserData


class PrivateEye:
    """Overall Class to manage bot"""

    def __init__(self):
        """Initialize bot"""

        # Create reddit instance
        self.reddit = praw.Reddit("PrivateEye", user_agent="Private_Eye_Bot 0.1")
        self.reddit_inbox = Inbox(self.reddit)
        self.reddit_user_data = RedditUserData(self.reddit)

        # Establish internet connection
        self._connectivity_check()
        self.internet_connection = False

        # Start with bot turned off
        self.bot_active = False

    def run_bot(self):
        """Start main loop"""

        
        print("\nChecking for internet connection...\n")
        
        # If there is no internet connection, inform user.
        if not self._connectivity_check():
            print("Network error: Unable to process requests..  are you connected to the internet?")

            # Try to recconect three times, warn user the program will not work without internet connection.
            self._attempt_internet_reconnect()

        

        print("""\
              
            ______     _            _        
            | ___ \   (_)          | |       
            | |_/ / __ ___   ____ _| |_ ___  
            |  __/ '__| \ \ / / _` | __/ _ \ 
            | |  | |  | |\ V / (_| | ||  __/ 
            \_|  |_|  |_| \_/_\__,_|\__\___| 
                            |  ___|           
                            | |__ _   _  ___  
                            |  __| | | |/ _ \ 
                            | |__| |_| |  __/ 
                            \____/\__, |\___| 
                                    _/ |    `  
                                   |___/       
              
              \n""")

        print("The available commands are: 'start bot', 'search', and 'help'.  Type 'quit' to end the program.\n\n")

       
        while True:
            # Gather User input
            user_input = input("private eye > ")
            user_input = user_input.lower().strip(" ")

            # Ensure internet is active, then process user request.
            if not self._connectivity_check():
                print("\nNetwork error: Unable to process requests..  are you connected to the internet?\n")
            else:
                self._check_user_input(user_input)
            
            # if user inputs, 'Start bot': Initialize ability to recieve commands via reddit PM  
            bot_active = self.bot_active
            while bot_active == True:
                self.reddit_inbox.check_messages()
                time.sleep(10)
                
        
    def _connectivity_check(self):
        """ 
        Checks for intternet connectivity.

        Returns Boolean as result

        True -> able to make GET request

        False -> unable to make GET request
        
        """
        try:
            requests.get("Http://google.com", timeout=3)
            self.internet_connection = True
            return True
        except requests.ConnectionError:
            self.internet_connection = False
            return False
        
    def _assert_internet_connection(self):
        """ Notify user if there is no netork connection"""
        if not self._connectivity_check():
            time.sleep(10)
        
        if self._connectivity_check == True:
            print("Connection to internet established. Please try your request again.")

    def _attempt_internet_reconnect(self):
        """ 
        Attempt to make a GET request 3 times.
        Continues if no connection can be made
        """
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            if not self.internet_connection:
                self._assert_internet_connection()
                attempts += 1
                print(f"attempting to establish connection..  Attempt {attempts} of {max_attempts}.")
                if attempts == max_attempts:
                    print("\nUnable to establish connection. Private Eye cannot process requests until internet connectivity is re-established.\n")
                    print("initializing Private Eye.. Please ensure internet acess before making a request.\n\n")

    
    def _check_user_input(self, user_input):
        """
        Parse user input for CLI commands.

        searches for help, start bot, search, and quit.

        kwargs = user_input --> str
        
        """
        # Displays help message
        if user_input == "help" or user_input == "h":
            print("The available commands are: 'start bot', 'search', and 'help'.  Type 'quit' to end the program.")

        # initialize ability to recieve commands by reddit PM
        elif user_input == "start bot":
                
                # Prompts user to setup username that is allowed to send !shutdown message.  Begins while loop in run_bot()
                self.reddit_inbox.setup_bot_owner()
                self.bot_active = True
                print("\nBot activated sucessfully, monitoring for messages.  Press CTRL + C to stop bot.")

        # Search for user, optionally search user comments.
        elif user_input == "search" or user_input == "s":
                
                # Gathers target username from user.
                while True:
                    username = input("\nPlease enter a username to search: ")
                    username = username.lower().strip(" ")

                    # Confirm the target exists, else reprompt user.
                    if not self.check_user_exists(username):
                        continue
                    break
         
                # Gathers if the user wants to search comments. If so, prompts for keywords.
                while True:
                    # Gather user choice
                    search_comments = input(f"\nuser {username} found. Search their comments? yes or no: ")

                    # If no comments are searched, return only basic user info.
                    if search_comments.lower() == "no":
                        results = self.reddit_user_data.get_user_info(username)
                        print(results)
                        self._record_results(results)
                        break
                    # If the input is not 'yes', or 'no'. reprompt user for choice.
                    elif search_comments.lower() != "no" and search_comments.lower() != "yes":
                        print("that is not a valid command. Please enter 'yes', or 'no'")
                        continue
                    # Obtain keyword or keywords to search by, turn into a list, search the users comments for the keywords.
                    keyword_input = input("\nEnter Keyword(s) seperated by ','.  Press enter for none: ")
                    keywords = self._format_keywords(keyword_input)
                    results = self._find_results(username, keywords)
                    self._record_results(results)
                    break
                
        # ends the program.  
        elif user_input == "quit" or user_input == "q":
            print("goodbye.")
            sys.exit(0)

    def check_user_exists(self, username):
        """
        Checks if username is tied to a user.
        Returns T or F

        kwags:
            username --> str
        """
        
        #Check if user exists.
        print(f"\nsearching for {username}..")
        username_check = self.reddit_user_data.get_user_info(username)
                    
        # Reprompt is user does not exist.
        if not username_check:
            return False  
        else:
            return True
  
    def _format_keywords(self, keyword=""):
        """
        Formats supplied keywords into a list

        kwargs = keyword --> str
        """

        
        if keyword == "":
                # if user passed no keywords, return null list.
                keywords = None
                return keywords
                
        else:
            # Check if there are multiple keywords; format and check for comments.
            keywords = keyword.split(",")

            if len(keywords) > 1:
                for i in range(len(keywords)):
                    keywords[i] = keywords[i].strip(" ").lower()
                return keywords
                            
            else:
                # format singular keyword and place it in list.
                for keyword in keywords:
                    keyword.strip(" ").lower()
                return keywords

    
    def _find_results(self, username, keylist=None):
        """
        Takes username and keywor list and queries reddit user data for results.

        kwags: 
            username --> str 
          
            keylist --> list
        """

        if keylist is None:
            # If no keywords return last 5 comments.
            collected_comments = self.reddit_user_data._check_user_comments(username)

            if collected_comments == []:
                # If no comment's return user info
                results = f"{self.reddit_user_data.get_user_info(username)}\n"
            else:
                # if comments present, format them and return user info and comments
                formatted_comments = self.reddit_user_data.format_comments(collected_comments)
                results = f"{self.reddit_user_data.get_user_info(username)}\n {formatted_comments}"
        else:
            # Keywords are present, search comments for mentions of keywords.
            collected_comments = self.reddit_user_data._check_user_comments(username, keylist)

            if collected_comments == []:
                # No comments matching keywords.  Return user info.
                results = f"{self.reddit_user_data.get_user_info(username)}\n"
            else:
                # Keywords present.  Return user info and comments with keywords highlighted.
                formatted_comments = self.reddit_user_data.format_comments(collected_comments)
                results = f"{self.reddit_user_data.get_user_info(username)}\n {formatted_comments}"
        
        print(results)
        return results
    
    def _record_results(self, results):
        """ 
        Takes results and appends them to results.txt 
        
        kwags:
        
        results --> str
        """
        
        today = time.localtime()
        print("This information has been recorded in the results.txt file.")
        with open("results.txt", "a") as file:
            file.write(results + f"Date retrieved: {today.tm_mon}/{today.tm_mday}/{today.tm_year} @ {today.tm_hour}:{today.tm_min}\n")
            file.close()
    
if __name__ == "__main__":
    pi = PrivateEye()
    pi.run_bot()

        