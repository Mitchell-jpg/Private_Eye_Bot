import time
from prawcore.exceptions import NotFound, TooManyRequests, ResponseException

class RedditUserData:
    """ A class to manage request made to reddits database"""

    def __init__(self, reddit) -> None:
        """
        Initialize reddit instance
        """
        
        self.reddit = reddit

    def check_user_exists(self, username: str) -> bool:
        """
        Checks is user exists. returns T or F
        
        """
        #Check if user exists.
        print(f"\nsearching for {username}..")
        username_check = self.get_user_info(username)
        

        if not username_check:
            return False
        return True
                
                    

    def get_user_info(self, username: str) -> str:
        """
        Take username and outputs Karma, redditID, Acount creation time, etc.

        returns string value formatted in markdown if user exists.

        raises False is no user if found.
        """
        max_retries = 3
        attempts = 0
        
        while attempts < max_retries:

            try:
                # Create instance of user
                self.user = self.reddit.redditor(username)

                # Convert UTC to Local
                time_obj = time.localtime(self.user.created_utc)
                local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)
                    
                # Information on user
                text = (f"##{self.user}\n\n> Karma: {self.user.comment_karma}\n\n> [Profile_pic]({self.user.icon_img})\n\n>" +                               
                f" Reddit ID: {self.user.id}\n\n> Account made @ {local_time}\n\n> Verifed Email?: {self.user.has_verified_email}\n\n" +             
                f"> Reddit employee? {str(self.user.is_employee)}\n\n> Moderator?: {str(self.user.is_mod)}\n\n> Reddit Premium?: {str(self.user.is_gold)}\n\n")

                # output   
                return text
        
            except NotFound as e:
                # User not found; Return False
                print(f"\n{e}: Username {username} could not be found.  Check for spelling mistakes.\n")
                return False
                
                    
            except TooManyRequests as e:
                attempts += 1
                print(f"{e}: waiting 20 seconds and trying again.. attempt {attempts} of {max_retries}\n")
                time.sleep(20)

    def check_user_comments(self, username:str , keywords: list =None) -> list:
        """
        Check user comments for keywords.  
        
        Returns up to 30 comments with keywords.
        Return last 5 comments with no keywords.
        """

        collected_comments = []

        
        print("\nSearching for recent comments...\n")

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
                                
                        # return comments, ready for markdown.
                        extracted_comment.append ( 
                            f"**Subreddit name:** r/{comment.subreddit.display_name} \n\n"        +
                            "---\n\n"                                                                 +
                            comment.body + "\n\n"                                                 +
                            "---\n\n"                                                                 +
                            f"Karma: {comment.score}  |  Posted at: {local_time}\n\n"             +                                        
                            f"[Link_to_comment](https://reddit.com{comment.permalink})\n\n"  
                        )
                        collected_comments.append(extracted_comment)

                    # break loop if all comments collected sucessfully.
                    success = True
                    
                        
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
                        # break loop if all comments collected sucessfully
                        success = True
            
            # If user has made no comments, break loop.
            except NotFound as e:
                print(f"{e} No comment's found for {username}")
                success = True
                break
                
            # If rate-limited wait 20 seconds and try again a maximum of three times.
            except TooManyRequests as e:
                attempts +=1
                print(f"Too many reqests.. waiting 20 seconds and trying again.. attempt {attempts} of {max_retries}\n")
                time.sleep(20)

        # if nothing was found append list.  This will be processed by format_comments() function to notify via PM.
        if collected_comments == []:
            return ["no comments matching keyword was found"]
        
        else:
            return self._format_comments(collected_comments)

    def _format_comments(self, collected_comments: list) -> str:
        """
         Format response from collected comments

         returns string formatted in markdown.
        """
        
        list_to_string = ""
        num_of_comments = 0

        #Process comments found
        for comment in collected_comments:
            # Check for errors
            if "no comments matching keyword was found" in comment:
                list_to_string = " no comments matching keyword(s) was found.\n"
                break
            else:
                # concat comment's
                for element in comment :
                    num_of_comments += 1
                    list_to_string += element + "\n\n"    
            
        text = f"Found {num_of_comments} Comment(s):\n\n{list_to_string}"
        return text