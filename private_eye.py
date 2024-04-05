import sys
from functools import wraps
import praw
import time
import requests
from prawcore.exceptions import NotFound, TooManyRequests, InvalidToken, ResponseException
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

        # Start with bot turned off
        self.bot_active = False

    def connectivity_check(func: any) -> any:
        """ 
        Checks for internet connectivity.
        
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            
            """ 
            Attempt to make a GET request 3 times.
            Continues if no connection can be made
            """

            attempts = 0
            max_attempts = 3
                
            while attempts < max_attempts:
            
                try:
                    requests.get("Http://google.com", timeout=3)
                    func(*args, **kwargs)
                except requests.ConnectionError:
                    attempts += 1
                    print(f"attempting to establish connection..  Attempt {attempts} of {max_attempts}.")
                    time.sleep(5)

            
            if func.__name__ != "run_bot":
                return print("Network error: Unable to process request.")
        
            print("\nUnable to establish internet connection. Private Eye cannot process requests until internet connectivity is re-established.\n")
            func(pi)
            
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
            elif user_input == "quit" or user_input == "q":
                print("goodbye.")
                sys.exit()
            else:
                try:
                    self._check_user_input(user_input)
                except ResponseException as e:
                    return print(f"{e}, check Praw.ini file for errors.")
            
            # if user inputs, 'Start bot': Initialize ability to recieve commands via reddit PM  
            bot_active = self.bot_active
            if bot_active == True:
                print("\nBot activated sucessfully, monitoring for messages.  Press CTRL + C to stop bot locally.")
            while bot_active == True:
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

        """
        

        # initialize ability to recieve commands by reddit PM
        if user_input == "start bot":
               
                # Prompts user to setup username that is allowed to send !shutdown message.  Begins while loop in run_bot()
                self.reddit_inbox.setup_bot_owner()
                self.bot_active = True
                
            

        # Search for user, optionally search user comments.
        elif user_input == "search" or user_input == "s":
            try:    
                # Gathers target username from user.
                while True:
                    username = input("\nPlease enter a username to search, enter 'go back' to cancel: ")
                    username = username.lower().strip(" ")

                    if username == "go back":
                        print("\ncancelling search..\n")
                        break

                    # Confirm the target exists, else reprompt user.
                    elif not self.check_user_exists(username):
                        continue
                    break
         
                # Gathers if the user wants to search comments. If so, prompts for keywords.
                while True:
                    # Gather user choice
                    search_comments = input(f"\nuser {username} found. Search their comments? yes or no: ")

                    if search_comments.lower() == "go back":
                        print("\nCancelling search..\n")
                        break

                    # If no comments are searched, return only basic user info.
                    if search_comments.lower() == "no":
                        results = self.reddit_user_data.get_user_info(username)
                        print(results)
                        self.record_results(results)
                        break
                    # If the input is not 'yes', or 'no'. reprompt user for choice.
                    elif search_comments.lower() != "no" and search_comments.lower() != "yes":
                        print("that is not a valid command. Please enter 'yes', or 'no'")
                        continue
                    # Obtain keyword or keywords to search by, turn into a list, search the users comments for the keywords.
                    keyword_input = input("\nEnter Keyword(s) seperated by ','.  Press enter for none: ")
                    keywords = self._format_keywords(keyword_input)
                    results = self._find_results(username, keywords)
                    self.record_results(results)
                    break

            except ResponseException as e:
                return print(f"{e}, check Praw.ini file for errors.")

    def check_user_exists(self, username: str) -> bool:
        """
        Checks if username is tied to a user.
        Returns T or F

        """
        
        #Check if user exists.
        print(f"\nsearching for {username}..")
        username_check = self.reddit_user_data.get_user_info(username)
                        
        # Reprompt is user does not exist.
        if not username_check:
            return False  
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

    
    def _find_results(self, username: str, keylist: list = None) -> str:
        """
        Takes username and keywor list and queries reddit user data for results.

    
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
    
    def record_results(self, results):
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

        