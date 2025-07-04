import unittest
from unittest.mock import patch, mock_open
from api_s.crc import ChatRequestConfiguraion, IncorrectRole, IncorrectContent, ReachTokenLimit, IncorrectMessageID, BrokenFileError


FAKE_SCHEMA = '{"model": "model", "messages": "messages", "max_tokens": "max_tokens"}'

class TestChatRequestConfig(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data=FAKE_SCHEMA)
    @patch("tiktoken.get_encoding")
    def setUp(self, mocked_encoding, mocked_open):
        encoding_obj = lambda: None
        encoding_obj.encode = lambda s: list(s)
        mocked_encoding.return_value = encoding_obj
        
        self.chat_conf = ChatRequestConfiguraion("gpt-3.5", max_tokens=10)
    
    def test_add_message_ok(self):
        self.chat_conf.add_message("user", "привет")
        self.assertEqual(len(self.chat_conf.messages), 1)
        self.assertEqual(self.chat_conf.messages[0]['role'], "user")
        self.assertEqual(self.chat_conf.messages[0]['content'], "привет")

    def test_role_validation(self):
        with self.assertRaises(IncorrectRole):
            self.chat_conf.add_message("admin", "лол")

    def test_content_validation(self):
        with self.assertRaises(IncorrectContent):
            self.chat_conf.add_message("user", 123)

    def test_token_limit(self):
        with self.assertRaises(ReachTokenLimit):
            self.chat_conf.add_message("user", "x" * 15)

    def test_remove_and_change(self):
        self.chat_conf.add_message("user", "на связи!")
        self.chat_conf.add_message("assistant", "ок")
        self.chat_conf.remove_message(0)
        self.assertEqual(len(self.chat_conf.messages), 1)
        self.assertEqual(self.chat_conf.messages[0]['role'], "assistant")

        self.chat_conf.change_content(0, "новый ответ")
        self.assertIn("новый", self.chat_conf.messages[0]['content'])

    def test_remove_incorrect_id(self):
        with self.assertRaises(IncorrectMessageID):
            self.chat_conf.remove_message(15)

    def test_schema_validation_fail(self):
        fake_bad_schema = '{"model": 123, "messages": "messages", "max_tokens": "max_tokens"}'
        with patch("builtins.open", mock_open(read_data=fake_bad_schema)):
            with self.assertRaises(Exception):  # InvalidSchemaTypes
                conf = ChatRequestConfiguraion("test_model")

    def test_broken_file(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with self.assertRaises(BrokenFileError):
                conf = ChatRequestConfiguraion("test_model")

    def test_generate_config(self):
        self.chat_conf.add_message("system", "кто тут?")
        conf_dict = self.chat_conf.generate_config()
        self.assertIn("model", conf_dict)
        self.assertIn("messages", conf_dict)
        self.assertIn("max_tokens", conf_dict)

if __name__ == "__main__":
    unittest.main()
