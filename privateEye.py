import praw
import time

class PrivateEye:
    """Overall Class to manage bot"""

    def __init__(self):
        """Initialize bot"""

        # Create reddit instance
        self.reddit = praw.Reddit("PrivateEye", user_agent="Private_Eye_Bot 0.1")

        # Owner Username
        self.owner_username = ""

    def _check_user_comments(self, username, keyword=""):
        """
        Check Defined users comments
        
        work in progress, keywords will come in th futrue.
        """

        # Create instance of comments
        comments = self.reddit.redditor(username).comments.new

        # Search for most recent comments; display last 5 if found.
        print("Searching for recent comments...\n")

        collected_comments = []

        # If no searchable keywords, return last 5 comments.
        
        if keyword == "":
            

            print("No keywords..  Printing last 5 comments\n")

            try:
                for comment in comments(limit=5):
                    
                    extracted_comment = []

                    # Convert UTC to Local
                    time_obj = time.localtime(comment.created_utc)
                    local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)
                    
                    # return comments.
                    extracted_comment.append( 
                        f"Subreddit name : r/{comment.subreddit.display_name} |"              +
                        comment.body                                                        +
                        " | "                                                                +
                        f"Karma: {comment.score}  |  Posted at: {local_time} "             +                                        
                        f"Link: https://reddit.com{comment.permalink} "  
                    )
                    collected_comments.append(extracted_comment)
            except:
                return ""
            
            return collected_comments
                
        # Search for keywords, return matching comments.
        else:
            try:
                for comment in comments:
                    if keyword in comment:
                        extracted_comment = []

                        # Convert UTC to Local
                        time_obj = time.localtime(comment.created_utc)
                        local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)
                        
                        # Store in temporary list.
                        extracted_comment.append(f"Subreddit name : {comment.subreddit.display_name} " )
                        extracted_comment.append(comment.body + " ")                                                        
                        extracted_comment.append("")                                                               
                        extracted_comment.append(f"Karma: {comment.score}  |  Posted at: {local_time} ")                         
                        extracted_comment.append(f"Link: https://reddit.com{comment.permalink} ")

                        collected_comments.append(extracted_comment)
            except:
                return ""
            

            if collected_comments == []:
                return "no comments matching keyword was found."
            else:
                return collected_comments

    
    def _get_user_info(self, username):

        # Create instance of user
        self.user = self.reddit.redditor(username)

        # Convert UTC to Local
        try:
            time_obj = time.localtime(self.user.created_utc)
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)
        
        
            # Information on user
            basic_info = (
            fr"Basic info for user: {self.user}\  " +
            fr"Karma: {self.user.comment_karma}\  " +                                     
            fr"Link to Profile pic: {self.user.icon_img}\  " +                             
            fr"Reddit ID: {self.user.id}\  " +                                              
            fr"Account Age: {local_time}\  " +           
            fr"Verifed Email? : {self.user.has_verified_email}\  " +                        
            fr"Reddit employee? {str(self.user.is_employee)}\  " +                          
            fr"Moderator? : {str(self.user.is_mod)}\  " +                                 
            fr"Reddit Premium?: {str(self.user.is_gold)}&nbsp;")
        except:
            return f"{username} not found."
        
        return basic_info

    def _search_for_keywords(self, message):
            """Search for keywords in messages"""

            
            # Allow bot owner to shutdown remotley; Block others who try.
            if message.subject == "!shutdown": 
                if message.author == self.settings.owner:
                    bot_active = False
                else:
                    print(f"Blocked user {message.author} for trying to shutdown bot.")
                    self.message.mark_read()
                    self.message.block()
            
            elif message.subject == "!search":

                target_username = message.body
                collected_comments = self._check_user_comments(target_username)
                
                formatted_reply = ""
                
                # Process comments
                for comment in collected_comments:
                    formatted_reply += fr"{comment}\  "
            
                
                message.reply(fr"{self._get_user_info(target_username)}\  {formatted_reply}")
                message.mark_read()
                print(f"Infromation on {target_username} provided to {message.author}.\nResuming inbox monitoring")
                

            else:
                message.reply("Try again.")
                print(f"sent try again message to {message.author}")
                message.mark_read()

        
    def _check_messages(self):
        """Monitor bot's inbox for keywords"""
        
        inbox = self.reddit.inbox.unread()
        # Begin monitoring inbox for keywords.
        
        for message in inbox:
                
            # Print recieved message into console.
            print(
                  f"From: {message.author}\n"      +
                  f"Subject: {message.subject}\n"  +
                  message.body
                  )
            
            self._search_for_keywords(message)
                
           


    def run_bot(self):
        """Start main loop"""

        # Set active flag
        bot_active=True

        self.owner_username = input("Enter the bot owner's username: ")
        

        print("monitoring for messages")

        while bot_active:
           
            self._check_messages()
            time.sleep(5)


        
            
                    
                    



if __name__ == "__main__":
    pi = PrivateEye()
    pi.run_bot()