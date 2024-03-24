import unittest
from privateEye import PrivateEye


class TestPrivateEye(unittest.TestCase):

    def setUp(self):
        self.private_eye = PrivateEye()

    def test_format_reply_no_comments(self):
        collected_comments = ["no comments matching keyword was found."]
        reply = self.private_eye.format_reply(collected_comments)
        self.assertEqual(reply, "Found 0 Comment(s):\n\n no comments matching keyword was found.\n")

    def test_format_reply_with_comments(self):
        collected_comments = [
            ["Comment 1"],
            ["Comment 2"]
        ]
        reply = self.private_eye.format_reply(collected_comments)
        expected_reply = f"Found 2 Comment(s):\n\nComment 1\n\nComment 2\n\n\n"
        self.assertEqual(reply, expected_reply)

        collected_comments = [
            ["Comment 1"],
            ["Comment 2"],
            ["Comment 3"]
        ]
        reply = self.private_eye.format_reply(collected_comments)
        expected_reply = f"Found 3 Comment(s):\n\nComment 1\n\nComment 2\n\nComment 3\n\n\n"
        self.assertEqual(reply, expected_reply)
    
if __name__ == '__main__':
    unittest.main()