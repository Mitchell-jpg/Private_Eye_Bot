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

    def format_reply(self, message, collected_comments):
        """ Format response from collected comments"""
        
        list_to_string = ""
        num_of_comments = 0

        #Process comments found
        
        for comment in collected_comments:

            # Check for errors
            if comment == "no comments matching keyword was found.":
                message.reply("no comments matching keyword was found.")
            elif comment == "something went wrong":
                message.reply("something went wrong")
            else:

                # Seperate comments into their own list
                for element in comment :
                    print(comment)
                    num_of_comments += 1
                    list_to_string += element + "\n\n"
        
        text = f"#Found {num_of_comments}Comment(s):\n\n {list_to_string}"
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
    
    def check_user_comments(self, username, keywords=""):
        """Check user comments for keywords.  If no keywords, return last 5 comments"""

        collected_comments = []

        # Create instance of comments
        comments = self.reddit.redditor(username).comments.new

        # Search for most recent comments; display last 5 if found.
        print("Searching for recent comments...\n")

        # If no searchable keywords, return last 5 comments.
        if keywords == "":
            try:
                for comment in comments(limit=5):
                    
                    extracted_comment = []

                    # Convert UTC to Local
                    time_obj = time.localtime(comment.created_utc)
                    local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)
                        
                    # return comments.
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
            except:
                return ""
                
            return collected_comments
                
        # Search for keywords, return matching comments (maximum 30)
        else:
            try:
                for comment in comments(limit=30):
                    for keyword in keywords:
                        if keyword in comment.body:
                            extracted_comment = []

                            # Convert UTC to Local
                            time_obj = time.localtime(comment.created_utc)
                            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)
                            
                            # Store in temporary list.
                            extracted_comment.append ( 
                                f"**Subreddit name:** r/{comment.subreddit.display_name} \n\n"        +
                                "---\n\n"                                                                 +
                                comment.body + "\n\n"                                                 +
                                "---\n\n"                                                                 +
                                f"Karma: {comment.score}  |  Posted at: {local_time}\n\n"             +                                        
                                f"[Link_to_comment](https://reddit.com{comment.permalink})\n\n"
                            )  
                            collected_comments.append(extracted_comment)
            except:
                return ""
            
            if collected_comments == []:
                return "no comments matching keyword was found."
            else:
                return collected_comments
 
    def get_user_info(self, username):

        # Create instance of user
        self.user = self.reddit.redditor(username)

        # Convert UTC to Local
        try:
            time_obj = time.localtime(self.user.created_utc)
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time_obj)
              
            # Information on user
            text = (f"##{self.user}\n\n> Karma: {self.user.comment_karma}\n\n> [Profile_pic]({self.user.icon_img})\n\n>" +                               
            f" Reddit ID: {self.user.id}\n\n> Account made @ {local_time}\n\n> Verifed Email?: {self.user.has_verified_email}\n\n" +             
            f"> Reddit employee? {str(self.user.is_employee)}\n\n> Moderator?: {str(self.user.is_mod)}\n\n> Reddit Premium?: {str(self.user.is_gold)}\n\n")
        except:
            return f"{username} not found."
        
        return self.convert_to_markdown(text)

    def search_for_commands(self, message):
        """Search for keywords in messages"""
           
        # Allow bot owner to shutdown remotley; Block others who try.
        if message.subject == "!shutdown": 
            if message.author == self.settings.owner:
                bot_active = False
            else:
                print(f"Blocked user {message.author} for trying to shutdown bot.")
                self.message.mark_read()
                self.message.block()
            
        elif message.subject == "!search" or "Re: !search":

            body = message.body
                
            # Check if delimiter used, if not format username and search last 5 comments.
            if "|" in body:

                sepmsg = body.split("|")

                # If the delimiter splits in anything other than two the format must be wrong.
                if len(sepmsg) != 2:
                    message.reply("Wrong format used.  Seperate username and keywords using '|' and seperate keywords by ','")
                else:

                    username = sepmsg[0].strip(" ").lower()
                        
                    # Check if there are multiple keywords; format and check for comments.
                    if "," in sepmsg[1]:
                        keywords = sepmsg[1].split(",")
                        for i in range(len(keywords)):
                            keywords[i] = keywords[i].strip().lower()
                            
                    else:
                        keywords = sepmsg[1]
                        for keyword in keywords:
                            keyword.strip(" ").lower()

                    collected_comments = self.check_user_comments(username, keywords)
                    formatted_reply = self.format_reply(message, collected_comments)
            else:
                    username = body.strip(" ").lower()
                    collected_comments = self.check_user_comments(username)
                    formatted_reply = self.format_reply(message, collected_comments)    
                
            message.reply(f"{self.get_user_info(username)} \n {formatted_reply}")
            message.mark_read()
            print(f"Infromation on {username} provided to {message.author}.\nResuming inbox monitoring\n")
                
        else:
            message.reply("Try again.")
            print(f"sent try again message to {message.author}")
            message.mark_read()

        
    def check_messages(self):
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
            
            self.search_for_commands(message)


    def run_bot(self):
        """Start main loop"""

        # Set active flag
        bot_active=True

        self.owner_username = input("Enter the bot owner's username: ")
        print("monitoring for messages")

        while bot_active:
           
            self.check_messages()
            time.sleep(5)


if __name__ == "__main__":
    pi = PrivateEye()
    pi.run_bot()