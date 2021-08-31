import os
import hello
import unittest
import tempfile

class HelloTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, hello.app.config['DATABASE'] = tempfile.mkstemp()
        hello.app.config['TESTING'] = True
        self.app = hello.app.test_client()
        hello.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        # os.unlink(hello.app.config['DATABASE'])
        # os.unlink(hello.DATABASE)

    def test_empty_db(self):
        print('test_empty_db')
        rv = self.app.get('/')
        strdata = rv.data.decode()
        assert 'No entries here so far' in strdata


if __name__ == '__main__':
    unittest.main()