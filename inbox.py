from prawcore.exceptions import TooManyRequests, NotFound


class Inbox:

    def __init__(self, reddit):
        self.reddit = reddit


    def check_messages(self):
        """Monitor bot's inbox for keywords"""

        max_retries = 3
        attempts = 0
        success = False
        
        while not success and attempts < max_retries:
            try:
                inbox = self.reddit.inbox.unread()
                success = True
            except TooManyRequests as e:
                attempts += 1
                print(f"Too many reqests.. waiting 20 seconds and trying again.. attempt {attempts} of {max_retries}\n")
        
        # Begin monitoring inbox for keywords.
        for message in inbox:
                
            # Print recieved message into console.
            print("message recieved\n"             +
                  f"From: {message.author}\n"      +
                  f"Subject: {message.subject}\n"  +
                  message.body + "\n\n"
                  )
            
            self.search_for_commands(message)

    def search_for_commands(self, message):
        """Search for keywords in messages"""
           
        # Allow bot owner to shutdown remotley; Block others who try.
        if "!shutdown" in message.subject: 
            if message.author != self.owner_username:
                print(f"Blocked user {message.author} for trying to shutdown bot.")
                message.mark_read()
                message.block()
                
            print("shutting down bot")
            self.bot_active = False
            
        elif "!search" in message.subject:

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
                    formatted_reply = self.format_reply(collected_comments)
            else:
                    username = body.strip(" ").lower()
                    collected_comments = self.check_user_comments(username)
                    formatted_reply = self.format_reply(collected_comments)    
                
            message.reply(f"{self.get_user_info(username)} \n {formatted_reply}")
            message.mark_read()
            print(f"Infromation on {username} provided to {message.author}.\nResuming inbox monitoring\n\n")
                
        else:
            message.reply(self.convert_to_markdown(f"Invalid format or unsupported command.\n\nI currently only support the *'!search'*"))
            message.mark_read()
            print(f"sent try again message to {message.author}")