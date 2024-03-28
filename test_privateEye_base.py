import unittest
from unittest.mock import MagicMock
from privateEye import PrivateEye


class TestPrivateEye(unittest.TestCase):

    def setUp(self):
        self.private_eye = PrivateEye()

    def test_format_reply_no_comments(self):
        collected_comments = ["no comments matching keyword was found."]
        reply = self.private_eye.format_reply(collected_comments)
        self.assertEqual(reply, "Found 0 Comment(s):\n\n no comments matching keyword(s) was found.\n")

    def test_format_reply_with_comments(self):
        collected_comments = [
            ["Comment 1"],
            ["Comment 2"]
        ]
        reply = self.private_eye.format_reply(collected_comments)
        self.assertEqual(reply, "Found 2 Comment(s):\n\nComment 1\n\nComment 2\n\n\n")

        collected_comments = [
            ["Comment 1"],
            ["Comment 2"],
            ["Comment 3"]
        ]
        reply = self.private_eye.format_reply(collected_comments)
        self.assertEqual(reply, "Found 3 Comment(s):\n\nComment 1\n\nComment 2\n\nComment 3\n\n\n")

    def test_bad_username(self):
        self.private_eye.get_user_info = MagicMock(return_value="Thereisnopossiblewayanyoneusesthisusername not found.")
        username = "Thereisnopossiblewayanyoneusesthisusername"
        reply = self.private_eye.get_user_info(username)
        self.assertEqual(reply, "Thereisnopossiblewayanyoneusesthisusername not found.")

    def test_search_command_with_delimiter(self):
        # Test search command with delimiter
        message = MagicMock()
        message.subject = "!search"
        message.body = "username | keyword1, keyword2"
        message.reply = MagicMock()
        message.mark_read = MagicMock()
        self.private_eye.get_user_info = MagicMock(return_value="User info")
        self.private_eye.check_user_comments = MagicMock(return_value=["Comment 1", "Comment 2"])
        self.private_eye.format_reply = MagicMock(return_value="Formatted reply")
        self.private_eye.search_for_commands(message)
        self.private_eye.get_user_info.assert_called_once_with("username")
        self.private_eye.check_user_comments.assert_called_once_with("username", ["keyword1", "keyword2"])
        self.private_eye.format_reply.assert_called_once_with(["Comment 1", "Comment 2"])
        message.reply.assert_called_once_with("User info \n Formatted reply")
        message.mark_read.assert_called_once()

    def test_shutdown_command_owner(self):
        # Test shutdown command from bot owner
        message = MagicMock()
        message.subject = "!shutdown"
        message.author = self.private_eye.owner_username
        self.private_eye.search_for_commands(message)
        self.assertFalse(self.private_eye.bot_active)

    def test_shutdown_command_non_owner(self):
        # Test shutdown command from non-owner
        message = MagicMock()
        message.subject = "!shutdown"
        message.author = "non_owner"
        message.reply = MagicMock()
        message.mark_read = MagicMock()
        message.block = MagicMock()
        self.private_eye.search_for_commands(message)
        #message.reply.assert_called_once_with("Blocked user non_owner for trying to shutdown bot.")
        message.mark_read.assert_called_once()
        message.block.assert_called_once()

    def test_search_command_with_keywords(self):
        # Test search command with keywords
        message = MagicMock()
        message.subject = "!search"
        message.body = "username | keyword1, keyword2"
        message.reply = MagicMock()
        message.mark_read = MagicMock()
        self.private_eye.get_user_info = MagicMock(return_value="User info")
        self.private_eye.check_user_comments = MagicMock(return_value=["Comment 1", "Comment 2"])
        self.private_eye.format_reply = MagicMock(return_value="Formatted reply")
        self.private_eye.search_for_commands(message)
        self.private_eye.get_user_info.assert_called_once_with("username")
        self.private_eye.check_user_comments.assert_called_once_with("username", ["keyword1", "keyword2"])
        self.private_eye.format_reply.assert_called_once_with(["Comment 1", "Comment 2"])
        message.reply.assert_called_once_with("User info \n Formatted reply")
        message.mark_read.assert_called_once()

    def test_search_command_without_keywords(self):
        # Test search command without keywords
        message = MagicMock()
        message.subject = "!search"
        message.body = "username"
        message.reply = MagicMock()
        message.mark_read = MagicMock()
        self.private_eye.get_user_info = MagicMock(return_value="User info")
        self.private_eye.check_user_comments = MagicMock(return_value=["Comment 1", "Comment 2"])
        self.private_eye.format_reply = MagicMock(return_value="Formatted reply")
        self.private_eye.search_for_commands(message)
        self.private_eye.get_user_info.assert_called_once_with("username")
        self.private_eye.check_user_comments.assert_called_once_with("username")
        self.private_eye.format_reply.assert_called_once_with(["Comment 1", "Comment 2"])
        message.reply.assert_called_once_with("User info \n Formatted reply")
        message.mark_read.assert_called_once()

    
if __name__ == '__main__':
    unittest.main()