# name    :  test/test_bookbot.py
# version :  0.0.1
# date    :  20230928
# author  :  Leam Hall
# desc    :  Unittests for bookbot


import os.path
import tempfile
import unittest

import bookbot as bb

class TestBookBot(unittest.TestCase):
   
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.test_dir.name, "book_config.ini")
        with open(self.config_file, 'w') as f:
            f.write("[Book]\n")
            f.write("title = Agent\n")
            f.write("author : Leam Hall\n") 

    def tearDown(self):
        self.test_dir.cleanup()
    
   
    def test_default_config(self):
        config = bb.read_config()
        self.assertEqual(config['author'], "")
        self.assertEqual(config['book_dir'], "book")
        self.assertEqual(config['reports_dir'], "reports")
        self.assertEqual(config['scene_dir'], "scenes")
        self.assertEqual(config['title'], "")
        self.assertNotIn("stuff", config.keys())
    
    def test_read_config(self):
        config = bb.read_config(config_file = self.config_file)
        self.assertEqual(config['author'], "Leam Hall")
        self.assertEqual(config['book_dir'], "book")
        self.assertEqual(config['reports_dir'], "reports")
        self.assertEqual(config['scene_dir'], "scenes")
        self.assertEqual(config['title'], "Agent")


