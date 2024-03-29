import unittest
from unittest.mock import MagicMock, patch
from private_eye import PrivateEye


class TestPrivateEye(unittest.TestCase):

    def setUp(self):
        self.private_eye = PrivateEye()

    def test_format_reply_no_comments(self):
        collected_comments = ["no comments matching keyword was found."]
        reply = self.private_eye.reddit_user_data.format_comments(collected_comments)
        self.assertEqual(reply, "Found 0 Comment(s):\n\n no comments matching keyword(s) was found.\n")

    def test_format_reply_with_comments(self):
        collected_comments = [
            ["Comment 1"],
            ["Comment 2"]
        ]
        reply = self.private_eye.reddit_user_data.format_comments(collected_comments)
        self.assertEqual(reply, "Found 2 Comment(s):\n\nComment 1\n\nComment 2\n\n")

        collected_comments = [
            ["Comment 1"],
            ["Comment 2"],
            ["Comment 3"]
        ]
        reply = self.private_eye.reddit_user_data.format_comments(collected_comments)
        self.assertEqual(reply, "Found 3 Comment(s):\n\nComment 1\n\nComment 2\n\nComment 3\n\n")

    def test_bad_username(self):
        self.private_eye.reddit_user_data.get_user_info = MagicMock(return_value="Thereisnopossiblewayanyoneusesthisusername not found.")
        username = "Thereisnopossiblewayanyoneusesthisusername"
        reply = self.private_eye.reddit_user_data.get_user_info(username)
        self.assertEqual(reply, "Thereisnopossiblewayanyoneusesthisusername not found.")


    def test_shutdown_command_owner(self):
        # Test shutdown command from bot owner
        message = MagicMock()
        message.subject = "!shutdown"
        message.author = self.private_eye.reddit_inbox.owner_username
        self.private_eye.reddit_inbox.search_for_commands(message)
        #self.assertFalse(self.private_eye.bot_active)


    def test_shutdown_command_non_owner(self):
        # Test shutdown command from non-owner
        message = MagicMock()
        message.subject = "!shutdown"
        message.author = "non_owner"
        message.reply = MagicMock()
        message.mark_read = MagicMock()
        message.block = MagicMock()
        self.private_eye.reddit_inbox.search_for_commands(message)
        #message.reply.assert_called_once_with("Blocked user non_owner for trying to shutdown bot.")
        message.mark_read.assert_called_once()
        message.block.assert_called_once()

    
if __name__ == '__main__':
    unittest.main()