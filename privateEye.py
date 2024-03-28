import sys
import praw
import time
from prawcore.exceptions import NotFound, TooManyRequests, InvalidToken
from inbox import Inbox


class PrivateEye:
    """Overall Class to manage bot"""

    def __init__(self):
        """Initialize bot"""

        # Create reddit instance
        try:
            self.reddit = praw.Reddit("PrivateEye", user_agent="Private_Eye_Bot 0.1")
            self.inbox = Inbox(self.reddit)
        except InvalidToken as e:
            print(f"{e}: Check tokens in praw.ini file.")

        # Owner Username
        self.owner_username = ""

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
              
              \r""")

        print("The available commands are: 'start bot', 'search', and 'help'.  Type 'quit' to end the program.\n\n")

        # Set active flag
        bot_active=False
        while True:
            user_input = input("private eye > ")

            self._check_user_input(user_input)
                    
            while bot_active:
        
                self.inbox.check_messages()
                time.sleep(10)
                
        
    
    def _check_user_input(self, user_input):
        """Parse user input for commands."""
        
        if "help" in user_input.lower():
            print("The available commands are: 'start bot', 'search', and 'help'.  Type 'quit' to end the program.")

        elif "start bot" in user_input.lower():
                self.owner_username = input("Enter the bot owner's username (allows remote shutdown):  ")
                self.bot_active = True
                print("Bot activated sucessfully, monitoring for messages.  Press CTRL + C to stop bot.")

        elif "search" in user_input.lower():
                username = input("Please enter a username to search: ")
                search_comments = input(f"Search {username}'s comments? yes or no ")
                
                if search_comments.lower() != "yes":

                    results = f"""\
                                {self._get_user_info(username)}\n
                                """
                    print(results)
                    print("This information has been recorded in the results.txt file.")
                    with open("results.txt", "w") as file:
                        file.write(results)
                        file.close()
                    return results
                
                keyword = input("enter keywords to search for seperated by ',' or press enter: ")

                if keyword == "":
                    collected_comments = self._check_user_comments(username)
                    formatted_comments = self.format_comments(collected_comments)
                    print(f"""\
                          {self._get_user_info(username)}\n {formatted_comments}
                          """)
                    results = f"""\
                        {self._get_user_info(username)}\n {formatted_comments}
                        """
                    print(results)
                    print("This information has been recorded in the results.txt file.")
                    with open("results.txt", "w") as file:
                        file.write(results)
                        file.close()
                        return results
                    
                keylist = keyword.split(",")
                    
                # Check if there are multiple keywords; format and check for comments.
                if "," in keylist:
                    keywords = keylist.split(",")
                    for i in range(len(keywords)):
                        keywords[i] = keywords[i].strip().lower()
                            
                else:
                    keywords = keylist
                    for keyword in keywords:
                        keyword.strip(" ").lower()

                collected_comments = self._check_user_comments(username, keywords)
                formatted_comments = self.format_comments(collected_comments)
                results = f"""\
                        {self._get_user_info(username)}\n {formatted_comments}
                        """
                print(results)
                print("This information has been recorded in the results.txt file.")
                with open("results.txt", "w") as file:
                    file.write(results)
                    file.close()
            
        elif "quit" in user_input.lower():
            print("goodbye.")
            sys.exit(0)

    def _get_user_info(self, username):

        max_retries = 3
        attempts = 0
        success = False
        
        while not success and attempts < max_retries:

            try:
                print(f"searching for {username}..\n")

                # Create instance of user
                self.user = self.reddit.redditor(username)
                success = True

            

                # Convert UTC to Local
                time_obj = time.localtime(self.user.created_utc)
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)
                    
                # Information on user
                text = (f"##{self.user}\n\n> Karma: {self.user.comment_karma}\n\n> [Profile_pic]({self.user.icon_img})\n\n>" +                               
                f" Reddit ID: {self.user.id}\n\n> Account made @ {local_time}\n\n> Verifed Email?: {self.user.has_verified_email}\n\n" +             
                f"> Reddit employee? {str(self.user.is_employee)}\n\n> Moderator?: {str(self.user.is_mod)}\n\n> Reddit Premium?: {str(self.user.is_gold)}\n\n")

                # output   
                print(f"info on user {username} found.. ")
                return self.convert_to_markdown(text)
        
            except NotFound as e:

                print(f"{e}: Username {username} not found\n\n")
                break
                    
            except TooManyRequests as e:

                time.sleep(20)
                print(f"Too many reqests.. waiting 20 seconds and trying again.. attempt {attempts} of {max_retries}\n")

    def _check_user_comments(self, username, keywords=None):
        """Check user comments for keywords.  If no keywords, return last 5 comments"""

        collected_comments = []

        
        print("Searching for recent comments...\n")

        # Create instance of comments
        comments = self.reddit.redditor(username).comments.new
            
        max_retries = 3
        attempts = 0
        success = False
        
        while not success and attempts < max_retries:
            try:
                # If no searchable keywords, return last 5 comments.
                if keywords is None:
                    for comment in comments(limit=5):
                            
                        extracted_comment = []

                        # Convert UTC to Local
                        time_obj = time.localtime(comment.created_utc)
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)

                        # Highlight found keywords
                        highlighted_comment = comment.body.replace(keyword, f"**{keyword}**")
                                
                        # return comments, ready for markdown.
                        extracted_comment.append ( 
                            f"**Subreddit name:** r/{comment.subreddit.display_name} \n\n"        +
                            "---\n\n"                                                                 +
                            highlighted_comment.body + "\n\n"                                                 +
                            "---\n\n"                                                                 +
                            f"Karma: {comment.score}  |  Posted at: {local_time}\n\n"             +                                        
                            f"[Link_to_comment](https://reddit.com{comment.permalink})\n\n"  
                        )
                        collected_comments.append(extracted_comment)
                    
                    return collected_comments
                        
                # Search for keywords, return matching comments (maximum 30)
                else:
                    for comment in comments(limit=30):
                        for keyword in keywords:
                            if keyword in comment.body:
                                extracted_comment = []

                                # Convert UTC to Local
                                time_obj = time.localtime(comment.created_utc)
                                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)

                                # Highlight found keyword
                                highlighted_comment = comment.body.replace(keyword, f"**{keyword}**")
                                    
                                # Store in temporary list.
                                extracted_comment.append ( 
                                    f"**Subreddit name:** r/{comment.subreddit.display_name} \n\n"        +
                                    "---\n\n"                                                                 +
                                    highlighted_comment + "\n\n"                                             +
                                    "---\n\n"                                                                 +
                                    f"Karma: {comment.score}  |  Posted at: {local_time}\n\n"             +                                        
                                    f"[Link_to_comment](https://reddit.com{comment.permalink})\n\n"
                                )  
                                collected_comments.append(extracted_comment)
            
            except NotFound as e:
                print(f"{e} No comment's found for {username}")
                success = True
                break
                
            except TooManyRequests as e:
                attempts +=1
                print(f"Too many reqests.. waiting 20 seconds and trying again.. attempt {attempts} of {max_retries}\n")
                time.sleep(20)

            if collected_comments == []:
                return collected_comments["no comments matching keyword was found."]
            else:
                return collected_comments

    def format_comments(self, collected_comments):            # <-- clarify function is for comments
        """ Format response from collected comments"""
        
        list_to_string = ""
        num_of_comments = 0

        #Process comments found
        for comment in collected_comments:
            # Check for errors
            if comment == "no comments matching keyword was found.":
                list_to_string = " no comments matching keyword(s) was found."
                break

            else:
                # Seperate comments into their own list
                for element in comment :
                    print(comment)
                    num_of_comments += 1
                    list_to_string += element + "\n\n"
            
        text = f"Found {num_of_comments} Comment(s):\n\n{list_to_string}"
        return self.convert_to_markdown(text)
    
    
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
    
if __name__ == "__main__":
    pi = PrivateEye()
    pi.run_bot()