import os
import io
import unittest
from libfaketime import fake_time, reexec_if_needed
import shutil
from datetime import datetime
from ftpretty import ftpretty, split_file_info
from compat import PY2
from .mock_ftp import MockFTP

reexec_if_needed()

class FtprettyTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_ftp = MockFTP()
        self.pretty = ftpretty(None, None, None, ftp_conn=self.mock_ftp)

    def createFixtures(self):
        self.mock_ftp.mkd('photos')
        self.mock_ftp.cwd('photos')
        self.mock_ftp.mkd('nature')
        self.mock_ftp.cwd('nature')
        self.mock_ftp.mkd('mountains')
        self.mock_ftp.cwd('..')
        self.mock_ftp.cwd('..')
        self.assertEqual(self.pretty.pwd(), '')

    def test_cd(self):
        self.createFixtures()
        self.pretty.cd('photos/nature/mountains')
        self.assertEqual(self.pretty.pwd(), 'photos/nature/mountains')
        self.assertRaises(Exception, self.pretty.cd('blah'))

    def test_cd_up(self):
        self.createFixtures()
        self.pretty.cd('photos/nature/mountains')
        self.assertEqual(self.pretty.pwd(), 'photos/nature/mountains')
        self.pretty.cd('../..')
        self.assertEqual(self.pretty.pwd(), 'photos')

    def test_make_directory(self):
        self.pretty.mkdir('photos')
        self.pretty.cd('photos')
        self.pretty.mkdir('family')
        self.pretty.cd('family')
        self.assertEqual(self.pretty.pwd(), 'photos/family')

    def test_descend(self):
        self.pretty.descend('photos/nature', True)
        self.pretty.mkdir('mountains')
        self.pretty.cd('mountains')
        self.assertEqual(self.pretty.pwd(), 'photos/nature/mountains')

    def test_list(self):
        self.pretty.mkdir('photos')
        self.pretty.cd('photos')
        self.assertEqual(self.pretty.pwd(), 'photos')
        file_contents = 'blah' if PY2 else b'blah'
        self.pretty.put(None, 'a.txt', file_contents)
        self.pretty.put(None, 'b.txt', file_contents)
        self.assertEqual(len(self.pretty.list()), 2)

    def test_list_relative_paths(self):
        file_contents = 'blah' if PY2 else b'blah'
        self.pretty.put(None, 'a.txt', file_contents)
        self.assertEqual(len(self.pretty.list(remove_relative_paths=True)), 1)

    def test_put_filename(self):
        size = self.pretty.put('AUTHORS.rst', 'AUTHORS.rst')
        self.assertEqual(size, os.path.getsize('AUTHORS.rst'))

    def test_put_file(self):
        with open('AUTHORS.rst', 'rb') as file_:
            size = self.pretty.put(file_, 'AUTHORS.rst')
            self.assertEqual(size, os.path.getsize('AUTHORS.rst'))

    def test_put_contents(self):
        if PY2:
            put_contents = 'test_string'
        else:
            put_contents = b'test_string'
        size = self.pretty.put(None, 'AUTHORS.rst', put_contents)
        self.assertEqual(size, len(put_contents))

    def test_upload_tree(self):
        os.mkdir("testdata")
        os.mkdir("testdata/tree")
        with open("testdata/tree/foo.txt", "w") as f:
            f.write("message")
        os.mkdir("testdata/tree/bar")
        with open("testdata/tree/bar/baz.txt", "w") as f:
            f.write("another message")
        tree = self.pretty.upload_tree("testdata/tree", "/tree")
        self.assertEqual(tree, "/tree")
        self.assertEqual(['tree'], self.pretty.list('.'))
        self.assertEqual(['foo.txt', 'bar'], self.pretty.list('tree'))
        self.assertEqual(['baz.txt'], self.pretty.list('tree/bar'))
        shutil.rmtree("testdata")

    def test_get(self):
        file_contents = 'hello_get' if PY2 else b'hello_get'
        self.pretty.put(None, 'remote_file.txt', file_contents)
        if os.path.exists('local_copy.txt'):
            os.unlink('local_copy.txt')
        self.assertFalse(os.path.isfile('local_copy.txt'))

        self.pretty.get('remote_file.txt', 'local_copy.txt')
        self.assertTrue(os.path.isfile('local_copy.txt'))
        with open('local_copy.txt') as file:
            self.assertEqual(file.read(), 'hello_get')
        os.unlink('local_copy.txt')

    def test_get_tree(self):
        os.mkdir("testdata")
        self.createFixtures()
        self.pretty.cd('photos/nature/mountains')
        self.assertEqual(self.pretty.pwd(), 'photos/nature/mountains')
        file_contents = 'blah' if PY2 else b'blah'
        self.pretty.put(None, 'travel.log', file_contents)

        self.pretty.cd('../../..')
        self.pretty.get_tree('.', 'testdata')
        self.assertTrue(os.path.exists('testdata/photos/nature/mountains/travel.log'))
        self.assertEqual(4, os.path.getsize('testdata/photos/nature/mountains/travel.log'))

        shutil.rmtree("testdata")


    def test_get_filehandle(self):
        file_contents = 'hello_file' if PY2 else b'hello_file'
        self.pretty.put(None, 'remote_file.txt', file_contents)
        if os.path.exists('local_copy.txt'):
            os.unlink('local_copy.txt')
        self.assertFalse(os.path.isfile('local_copy.txt'))

        outfile = open('local_copy.txt', 'wb')
        self.pretty.get('remote_file.txt', outfile)
        outfile.close()
        self.assertTrue(os.path.isfile('local_copy.txt'))
        with open('local_copy.txt') as file:
            self.assertEqual(file.read(), 'hello_file')
        os.unlink('local_copy.txt')

    def test_get_contents(self):
        file_contents = 'test_string' if PY2 else b'test_string'
        self.pretty.put(None, 'remote_file.txt', file_contents)
        contents = self.pretty.get('remote_file.txt')
        self.assertEqual(contents, file_contents)

    def test_delete(self):
        size = self.pretty.put('AUTHORS.rst', 'remote_file.txt')
        self.assertTrue(self.pretty.delete('remote_file.txt'))
        self.assertRaises(Exception, self.pretty.delete('photos/nature/remote.txt'))

    def test_dir_parse(self):
        fileinfo = [
            "-rw-rw-r-- 1 rharrigan www   47 Feb 20 11:39 Cool.txt\n",
            "-rw-rw-r-- 1 rharrigan nobody 2085 Feb 21 13:27 multi word name.png\n",
            "-rw-rw-r-- 1 rharrigan wheel  195 Feb 20 2013 README.txt\n"
        ]
        files = split_file_info(fileinfo)
        self.assertEqual(len(files), 3)

        with fake_time('2021-02-22 12:01:01'):
            current_year = int(datetime.now().strftime('%Y'))

        self.assertEqual(files[1]['name'], 'multi word name.png')
        self.assertEqual(files[1]['datetime'], datetime(current_year, 2, 21, 13, 27, 0))
        self.assertEqual(files[2]['datetime'], datetime(2013, 2, 20, 0, 0, 0))
        self.assertEqual(files[2]['size'], 195)
        self.assertEqual(files[2]['name'], 'README.txt')
        self.assertEqual(files[2]['owner'], 'rharrigan')
        self.assertEqual(files[2]['group'], 'wheel')

    def test_dir_parse_with_past_year(self):
        fileinfo = [
            "-rw-rw-r-- 1 rharrigan www   47 Feb 20 11:39 Cool.txt\n",
            "-rw-rw-r-- 1 rharrigan nobody 2085 Dec 21 13:27 multi word name.png\n",
            "-rw-rw-r-- 1 rharrigan wheel  195 Feb 20 2013 README.txt\n"
        ]
        files = split_file_info(fileinfo)
        self.assertEqual(len(files), 3)
        self.assertEqual(files[1]['name'], 'multi word name.png')
        self.assertEqual(files[1]['datetime'], datetime(2020, 12, 21, 13, 27, 0))
        self.assertEqual(files[2]['datetime'], datetime(2013, 2, 20, 0, 0, 0))
        self.assertEqual(files[2]['size'], 195)
        self.assertEqual(files[2]['name'], 'README.txt')
        self.assertEqual(files[2]['owner'], 'rharrigan')
        self.assertEqual(files[2]['group'], 'wheel')

    def test_dir_parse_windows(self):
        fileinfo = [
            "01-02-20  01:39PM             25429393 ABC.csv\n",
            "01-03-20  01:34PM             25450295 def-ghi.csv\n",
            "01-06-20  02:28PM             25504938 data.csv\n"
        ]

        files = split_file_info(fileinfo)
        self.assertEqual(len(files), 3)
        self.assertEqual(files[2]['datetime'], datetime(2020, 1, 6, 14, 28, 0))
        self.assertEqual(files[2]['size'], 25504938)
        self.assertEqual(files[2]['name'], 'data.csv')
        self.assertEqual(files[2]['owner'], None)
        self.assertEqual(files[2]['group'], None)

    def test_dir_parse_patched_regex(self):
        fileinfo = [
            "-rw-rw-r-- 1 rharrigan read-only   47 Feb 20 11:39 Cool.txt\n",
            "-rw-rw-r-- 1 rharrigan nobody 2085 Feb 21 13:27 multi word name.png\n",
            "-rw-rw-r-- 1 rharrigan dodgy-group-name  195 Feb 20 2013 README.txt\n"
        ]

        files = split_file_info(fileinfo)
        self.assertEqual(len(files), 3)

        with fake_time('2021-02-22 12:01:01'):
            current_year = int(datetime.now().strftime('%Y'))

        self.assertEqual(files[0]['group'], 'read-only')
        self.assertEqual(files[1]['name'], 'multi word name.png')
        self.assertEqual(files[1]['datetime'], datetime(current_year, 2, 21, 13, 27, 0))
        self.assertEqual(files[2]['datetime'], datetime(2013, 2, 20, 0, 0, 0))
        self.assertEqual(files[2]['size'], 195)
        self.assertEqual(files[2]['name'], 'README.txt')
        self.assertEqual(files[2]['owner'], 'rharrigan')
        self.assertEqual(files[2]['group'], 'dodgy-group-name')

    def test_dir_parse_sticky_bit(self):
        fileinfo = [
            "-rw-rw-r-- 1 rharrigan read-only   47 Feb 20 11:39 Cool.txt\n",
            "-rw-rw-r-- 1 rharrigan nobody 2085 Feb 21 13:27 multi word name.png\n",
            "-rw-rw-r-- 1 rharrigan dodgy-group-name  195 Feb 20 2013 README.txt\n",
            "drwxr-xr-t 2 rharrigan rharrigan 4096 Jan 31  2019 dist\n"
        ]
        with fake_time('2021-02-22 12:01:01'):
            current_year = int(datetime.now().strftime('%Y'))

        files = split_file_info(fileinfo)
        self.assertEqual(len(files), 4)
        self.assertEqual(files[0]['group'], 'read-only')
        self.assertEqual(files[1]['name'], 'multi word name.png')
        self.assertEqual(files[1]['datetime'], datetime(current_year, 2, 21, 13, 27, 0))
        self.assertEqual(files[2]['datetime'], datetime(2013, 2, 20, 0, 0, 0))
        self.assertEqual(files[2]['size'], 195)
        self.assertEqual(files[2]['name'], 'README.txt')
        self.assertEqual(files[2]['owner'], 'rharrigan')
        self.assertEqual(files[2]['group'], 'dodgy-group-name')

    def test_fallthrough(self):
        self.assertTrue(self.pretty.sendcmd('hello'), 'hello')

    def test_set_pasv(self):
        ftpretty(None, None, None, ftp_conn=self.mock_ftp, passive=False)

    def test_custom_port(self):
        ftpretty(None, None, None, ftp_conn=self.mock_ftp, port=2121)

    def test_close(self):
        self.pretty.close()


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(FtprettyTestCase))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
