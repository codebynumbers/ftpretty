import os
import unittest
import shutil
from datetime import datetime
from ftpretty import ftpretty
from compat import PY2
from .mock_ftp import MockFTP


class FtprettyTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_ftp = MockFTP()
        self.pretty = ftpretty(None, None, None, ftp_conn=self.mock_ftp)

    def test_cd(self):
        self.pretty.cd('photos/nature/mountains')
        self.assertEqual(self.pretty.pwd(), 'photos/nature/mountains')
        self.pretty._set_exists(False)
        self.assertRaises(Exception, self.pretty.cd('blah'))

    def test_cd_up(self):
        self.pretty.cd('photos/nature/mountains')
        self.pretty.cd('../..')
        self.assertEqual(self.pretty.pwd(), 'photos')

    def test_make_directory(self):
        self.pretty.cd('photos')
        self.pretty.mkdir('family')
        self.pretty.cd('family')
        self.assertEqual(self.pretty.pwd(), 'photos/family')

    def test_descend(self):
        self.pretty._set_exists(False)
        self.pretty.descend('photos/nature', True)
        self.pretty._set_exists(True)
        self.pretty.cd('mountains')
        self.assertEqual(self.pretty.pwd(), 'photos/nature/mountains')

    def test_list(self):
        self.mock_ftp._set_files(['a.txt', 'b.txt'])
        self.assertEqual(len(self.pretty.list()), 2)

    def test_list_relative_paths(self):
        self.mock_ftp._set_files(['.', '..', 'a.txt'])
        self.assertEqual(len(self.pretty.list(remove_relative_paths=True)), 1)

    def test_put_filename(self):
        size = self.pretty.put('AUTHORS.rst', 'AUTHORS.rst')
        self.assertEqual(size, os.path.getsize('AUTHORS.rst'))

    def test_put_file(self):
        with open('AUTHORS.rst') as file_:
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

        os.mkdir("tree")
        f = open("tree/foo.txt", "w")
        f.write("message")
        os.mkdir("tree/bar")
        f = open("tree/bar/baz.txt", "w")
        f.write("another message")
        tree = self.pretty.upload_tree("tree", "/tree")
        self.assertEqual(tree, "/tree")
        shutil.rmtree("tree")

    def test_get(self):
        if PY2:
            self.mock_ftp._set_contents('hello_get')
        else:
            self.mock_ftp._set_contents(b'hello_get')
        if os.path.exists('local_copy.txt'):
            os.unlink('local_copy.txt')
        self.assertFalse(os.path.isfile('local_copy.txt'))
        self.pretty.get('remote_file.txt', 'local_copy.txt')
        self.assertTrue(os.path.isfile('local_copy.txt'))
        with open('local_copy.txt') as file:
            self.assertEqual(file.read(), 'hello_get')
        os.unlink('local_copy.txt')

    def test_get_filehandle(self):
        self.mock_ftp._set_contents('hello_file')
        if os.path.exists('local_copy.txt'):
            os.unlink('local_copy.txt')
        self.assertFalse(os.path.isfile('local_copy.txt'))
        outfile = open('local_copy.txt', 'w')
        self.pretty.get('remote_file.txt', outfile)
        outfile.close()
        self.assertTrue(os.path.isfile('local_copy.txt'))
        with open('local_copy.txt') as file:
            self.assertEqual(file.read(), 'hello_file')
        os.unlink('local_copy.txt')

    def test_get_contents(self):
        if PY2:
            file_contents = 'hello'
        else:
            file_contents = b'hello'
        self.mock_ftp._set_contents(file_contents)
        contents = self.pretty.get('remote_file.txt')
        self.assertEqual(contents, file_contents)

    def test_delete(self):
        self.assertTrue(self.pretty.delete('remote_file.txt'))
        self.pretty._set_exists(False)
        self.assertRaises(Exception, self.pretty.delete('photos/nature/remote.txt'))

    def test_dir_parse(self):
        self.mock_ftp._set_dirlist("-rw-rw-r-- 1 rharrigan www   47 Feb 20 11:39 Cool.txt\n" +
                       "-rw-rw-r-- 1 rharrigan nobody 2085 Feb 21 13:27 multi word name.png\n" +
                       "-rw-rw-r-- 1 rharrigan wheel  195 Feb 20 2013 README.txt\n")
        files = self.pretty.list(extra=True)
        self.assertEqual(len(files), 3)

        current_year = int(datetime.now().strftime('%Y'))
        self.assertEqual(files[1]['name'], 'multi word name.png')
        self.assertEqual(files[1]['datetime'], datetime(current_year, 2, 21, 13, 27, 0))

        self.assertEqual(files[2]['datetime'], datetime(2013, 2, 20, 0, 0, 0))
        self.assertEqual(files[2]['size'], 195)
        self.assertEqual(files[2]['name'], 'README.txt')
        self.assertEqual(files[2]['owner'], 'rharrigan')
        self.assertEqual(files[2]['group'], 'wheel')

    def test_dir_parse_windows(self):
        self.mock_ftp._set_dirlist(
            "01-02-20  01:39PM             25429393 ABC.csv\n"
            "01-03-20  01:34PM             25450295 def-ghi.csv\n" +
            "01-06-20  02:28PM             25504938 data.csv\n"
        )

        files = self.pretty.list(extra=True)
        self.assertEqual(len(files), 3)

        self.assertEqual(files[2]['datetime'], datetime(2020, 1, 6, 14, 28, 0))
        self.assertEqual(files[2]['size'], 25504938)
        self.assertEqual(files[2]['name'], 'data.csv')
        self.assertEqual(files[2]['owner'], None)
        self.assertEqual(files[2]['group'], None)

    def test_dir_parse_patched_regex(self):
        self.mock_ftp._set_dirlist("-rw-rw-r-- 1 rharrigan read-only   47 Feb 20 11:39 Cool.txt\n" +
                       "-rw-rw-r-- 1 rharrigan nobody 2085 Feb 21 13:27 multi word name.png\n" +
                       "-rw-rw-r-- 1 rharrigan dodgy-group-name  195 Feb 20 2013 README.txt\n")
        files = self.pretty.list(extra=True)
        self.assertEqual(len(files), 3)

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
        self.mock_ftp._set_dirlist("-rw-rw-r-- 1 rharrigan read-only   47 Feb 20 11:39 Cool.txt\n" +
                                   "-rw-rw-r-- 1 rharrigan nobody 2085 Feb 21 13:27 multi word name.png\n" +
                                   "-rw-rw-r-- 1 rharrigan dodgy-group-name  195 Feb 20 2013 README.txt\n"
                                   "drwxr-xr-t 2 rharrigan rharrigan 4096 Jan 31  2019 dist\n")
        files = self.pretty.list(extra=True)
        self.assertEqual(len(files), 4)

        current_year = int(datetime.now().strftime('%Y'))
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
