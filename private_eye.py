import sys
import praw
import time
import requests
from inbox import Inbox
from reddit import RedditUserData
from functools import wraps
from prawcore.exceptions import NotFound, TooManyRequests, InvalidToken, ResponseException


class PrivateEye:
    """Overall Class to manage bot"""

    def __init__(self) -> None:
        """Initialize bot"""

        # Create reddit instance
        self.reddit = praw.Reddit("PrivateEye", user_agent="Private_Eye_Bot 0.1")
        self.reddit_inbox = Inbox(self.reddit)
        self.reddit_user_data = RedditUserData(self.reddit)

        # Start with bot turned off
        self.bot_active = False

    def connectivity_check(func: any) -> any:
        """ 
        Checks for internet connectivity.

        Prevent's actions that require internet connectivity from being performed.

        This will still allow the bot to initialize.
        
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> func:
            """ 
            Attempt to make a GET request 3 times.
            Continues if no connection can be made
            """

            attempts = 0
            max_attempts = 3
                
            while attempts < max_attempts:
            
                try:
                    requests.get("Http://google.com", timeout=3)
                    return func(*args, **kwargs)
                except requests.ConnectionError:
                    attempts += 1
                    print(f"attempting to establish connection..  Attempt {attempts} of {max_attempts}.")
                    time.sleep(5)

            
            if func.__name__ != "run_bot":
                return print("Network error: Unable to process request.")
        
            print("\nUnable to establish internet connection. Private Eye cannot process requests until internet connectivity is re-established.\n")
            func(pi)
            
        return wrapper
    
    def record_results(func: any) -> None:
        """ 
        Takes results and appends them to results.txt 
        """
        def wrapper(*args, **kwargs) -> func:

            results = func(*args, **kwargs)
        
            today = time.localtime()
            print("This information has been recorded in the results.txt file.")
            with open("results.txt", "a") as file:
                file.write(results + f"Date retrieved: {today.tm_mon}/{today.tm_mday}/{today.tm_year} @ {today.tm_hour}:{today.tm_min}\n")
                file.close()
                
        return wrapper
        

    @connectivity_check
    def run_bot(self) -> None:
        """Start main loop"""

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

            # Displays help message
            if user_input == "help" or user_input == "h":
                print("The available commands are: 'start bot', 'search', and 'help'.  Type 'quit' to end the program.")
            # Ends Program
            elif user_input == "quit" or user_input == "q":
                print("goodbye.")
                sys.exit()
            else:
                try:
                    # Attempts to locate commands that require API calls.
                    self._check_user_input(user_input)
                except ResponseException as e:
                    return print(f"{e}, check Praw.ini file for errors.")
            
            # if user inputs, 'Start bot': Initialize ability to recieve commands via reddit PM  
            if self.bot_active == True:
                self._activate_bot()
    
    @connectivity_check
    def _activate_bot(self) -> None:
        print("\nBot activated sucessfully, monitoring for messages.  Press CTRL + C to stop bot locally.")
        
        while self.bot_active == True:
            try:
                self.reddit_inbox.check_messages()    
                time.sleep(10)

            # Exception is used to break free from loop when !shutdown command is issued via PM
            except Exception:
                self.bot_active = False
                break

    @connectivity_check
    def _check_user_input(self, user_input: str) -> None:
        """
        Parse user input for CLI commands.

        searches for strings "start bot", and "search".

        Requires Internet conectivity.

        """
        

        # initialize ability to recieve commands by reddit PM
        if user_input == "start bot":
               
                # Prompts user to setup username that is allowed to send !shutdown message.  Begins while loop in run_bot()
                self.reddit_inbox.setup_bot_owner()
                self.bot_active = True

        # Search for user, optionally search user comments.
        elif user_input == "search" or user_input == "s":
            try:    
                self._perform_search_command()

            except ResponseException as e:
                return print(f"{e}, check Praw.ini file for errors.")
                
    def _perform_search_command(self) -> str:
        """ 
        Performs search based on user input of username and keywords

        returns results. 
        """
                
        # Gathers valid target username from user.
        username = self._gather_username_to_search()
        
        # Gathers if the user wants to search comments. If so, prompts for keywords.
        if not self._ask_to_check_comments(username):
            results = self._find_reddit_results(username, None, False)
            return results

        else:        
            #If user wants to search for comments, gather keywords.
            keyword_input = input("\nEnter Keyword(s) seperated by ','.  Press enter for none: ")
            keywords = self._format_keywords(keyword_input)
            results = self._find_reddit_results(username, keywords, True)
            return results


    def _gather_username_to_search(self) -> str:
        """ 
        Gathers input from user, checks for validity, returns formatted string 
        """

        while True:
                username = input("\nPlease enter a username to search: ")
                username = username.lower()
                
                #Check if user exists.
                if self.reddit_user_data.check_user_exists(username):
                    return username
                
                print(f"\nUsername {username} could not be found.  Check for spelling mistakes.\n")
                continue
        
    def _ask_to_check_comments(self, username: str) -> bool:

        while True:
            # Gather user choice
            search_comments = input(f"\nuser {username} found. Search their comments? yes or no: ")

            if search_comments.lower() == "no":
                return False
            elif search_comments.lower() != "no" and search_comments.lower() != "yes":
                print("that is not a valid command. Please enter 'yes', or 'no'")
                continue
            return True

  
    def _format_keywords(self, keyword: str = None) -> list:
        """
        Formats supplied keywords into a list

        """ 
        if not keyword:
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

    @record_results
    def _find_reddit_results(self, username: str, keylist: list = None, check_comments: bool = False) -> str:
        """
        Takes username and keyword list and queries reddit user data for results.

        """
        if not check_comments:
            results = f"{self.reddit_user_data.get_user_info(username)}\n"
            print(results)
            return results

        if keylist is None:
            # If no keywords return last 5 comments.
            formatted_comments = self.reddit_user_data.check_user_comments(username)
            results = f"{self.reddit_user_data.get_user_info(username)}\n {formatted_comments}"
        else:
            # Keywords are present, search comments for mentions of keywords.
            formatted_comments = self.reddit_user_data.check_user_comments(username, keylist)

            results = f"{self.reddit_user_data.get_user_info(username)}\n {formatted_comments}"
        
        print(results)
        return results 
    
if __name__ == "__main__":
    pi = PrivateEye()
    pi.run_bot()

        