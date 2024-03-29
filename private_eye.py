import sys
import praw
import time
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
        


        # Bot owner's Reddit Username
        self.reddit_owner_username = self.reddit_inbox.owner_username

    def run_bot(self):
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

        # Set active flag
        bot_active = False
        while True:
            user_input = input("private eye > ")

            self._check_user_input(user_input)
                    
            while bot_active:
        
                self.reddit_inbox.check_messages()
                time.sleep(10)
                
        
    
    def _check_user_input(self, user_input):
        """Parse user input for commands."""
        
        if user_input.lower() == "help":
            print("The available commands are: 'start bot', 'search', and 'help'.  Type 'quit' to end the program.")

        elif user_input.lower() == "start bot":
                self.owner_username = input("Enter the bot owner's username (allows remote shutdown):  ")
                self.bot_active = True
                print("Bot activated sucessfully, monitoring for messages.  Press CTRL + C to stop bot.")

        elif user_input.lower() == "search":
                username = input("Please enter a username to search: ")
                
                while True:
                    search_comments = input(f"Search {username}'s comments? yes or no ")
                    if search_comments.lower() != "yes" or "y":
                        if search_comments.lower() != "no" or "n":
                            print("that is not a valid command.")

                        results = self._find_results()
                        self._record_results(results)
                        return results
                     
                    else: break   

                if keyword == "":
                    today = time.localtime
                    results = self._find_results(username)
                    self._record_results(results)
                    
                keylist = keyword.split(",")
                    
                # Check if there are multiple keywords; format and check for comments.
                if len(keylist) > 1:
                    keywords = keylist.split(",")
                    for i in range(len(keywords)):
                        keywords[i] = keywords[i].strip().lower()
                            
                else:
                    keywords = keylist
                    for keyword in keywords:
                        keyword.strip(" ").lower()

                results = self._find_results(username)
                self._record_results(results)
            
        elif "quit" in user_input.lower():
            print("goodbye.")
            sys.exit(0)

    
  
    def convert_to_markdown(self, text):
        """ Converts string into markdown"""
        markdown = ''
        lines = text.split('\n')
        
        
        for line in lines:
            if line.startswith('#'):
                level = line.count('#')
                markdown += f"{'#' * level} {line[level:].strip()}\n"
            elif line.startswith('* '):
                markdown += f"- {line[2:]}\n"
            elif line.startswith('1. '):
                markdown += f"1. {line[3:]}\n"
            elif line.startswith('> '):
                markdown += f"> {line[2:]}\n"
            else:
                markdown += line + '\n'   
        return markdown
    
    def _find_results(self, username):

        if not collected_comments:
            results = f"{self.reddit_user_data._get_user_info(username)}\n"
        else:

            collected_comments = self.reddit_user_data._check_user_comments(username)

            formatted_comments = self.reddit_user_data.format_comments(collected_comments)
            results = f"{self.reddit_user_data._get_user_info(username)}\n {formatted_comments}"
        
        print(results)
        return results
    
    def _record_results(self, results):
        """ Takes results and appends them to results.txt """
        
        today = time.localtime
        print(results)
        print("This information has been recorded in the results.txt file.")
        with open("results.txt", "a") as file:
            file.write(results + f"Date retrieved: {today.tm_mon}/{today.tm_mday}/{today.tm_year} @ {today.tm_hour}:{today.tm_min}")
            file.close()
    
if __name__ == "__main__":
    pi = PrivateEye()
    pi.run_bot()