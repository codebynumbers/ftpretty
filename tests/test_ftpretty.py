import os
import unittest
from datetime import datetime
from ftpretty import ftpretty
from mock_ftp import MockFTP


class FtprettyTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_ftp = MockFTP()
        self.pretty = ftpretty(None, None, None, ftp_conn=self.mock_ftp)

    def test_cd(self):
        self.pretty.cd('photos/nature/mountains')
        self.assertEquals(self.pretty.pwd(), 'photos/nature/mountains')
        self.pretty._set_exists(False)
        self.assertRaises(Exception, self.pretty.cd('blah'))

    def test_cd_up(self):
        self.pretty.cd('photos/nature/mountains')
        self.pretty.cd('../..')
        self.assertEquals(self.pretty.pwd(), 'photos')

    def test_descend(self):
        self.pretty._set_exists(False)
        self.pretty.descend('photos/nature', True)
        self.pretty._set_exists(True)
        self.pretty.cd('mountains')
        self.assertEquals(self.pretty.pwd(), 'photos/nature/mountains')

    def test_list(self):
        self.mock_ftp._set_files(['a.txt', 'b.txt'])
        self.assertEquals(len(self.pretty.list()), 2)

    def test_list_relative_paths(self):
        self.mock_ftp._set_files(['.', '..', 'a.txt'])
        self.assertEquals(len(self.pretty.list(remove_relative_paths=True)), 1)

    def test_put_filename(self):
        size = self.pretty.put('AUTHORS.rst', 'AUTHORS.rst')
        self.assertEquals(size, os.path.getsize('AUTHORS.rst'))

    def test_put_file(self):
        with open('AUTHORS.rst') as file:
            size = self.pretty.put(file, 'AUTHORS.rst')
            self.assertEquals(size, os.path.getsize('AUTHORS.rst'))

    def test_put_contents(self):
        size = self.pretty.put(None, 'AUTHORS.rst', 'test string')
        self.assertEquals(size, len('test string'))

    def test_get(self):
        self.mock_ftp._set_contents('hello_get')
        self.assertFalse(os.path.isfile('local_copy.txt'))
        self.pretty.get('remote_file.txt', 'local_copy.txt')
        self.assertTrue(os.path.isfile('local_copy.txt'))
        with open('local_copy.txt') as file:
            self.assertEquals(file.read(), 'hello_get')
        os.unlink('local_copy.txt')

    def test_get_filehandle(self):
        self.mock_ftp._set_contents('hello_file')
        self.assertFalse(os.path.isfile('local_copy.txt'))
        outfile = open('local_copy.txt', 'w')
        self.pretty.get('remote_file.txt', outfile)
        outfile.close()
        self.assertTrue(os.path.isfile('local_copy.txt'))
        with open('local_copy.txt') as file:
            self.assertEquals(file.read(), 'hello_file')
        os.unlink('local_copy.txt')

    def test_get_contents(self):
        self.mock_ftp._set_contents('hello')
        contents = self.pretty.get('remote_file.txt')
        self.assertEquals(contents, 'hello')

    def test_delete(self):
        self.assertTrue(self.pretty.delete('remote_file.txt'))
        self.pretty._set_exists(False)
        self.assertRaises(Exception, self.pretty.delete('photos/nature/remote.txt'))

    def test_dir_parse(self):
        self.mock_ftp._set_dirlist("-rw-rw-r-- 1 rharrigan www   47 Feb 20 11:39 Cool.txt\n" +
                       "-rw-rw-r-- 1 rharrigan nobody 2085 Feb 21 13:27 multi word name.png\n" +
                       "-rw-rw-r-- 1 rharrigan wheel  195 Feb 20 2013 README.txt\n")
        files = self.pretty.list(extra=True)
        self.assertEquals(len(files), 3)

        current_year = int(datetime.now().strftime('%Y'))
        self.assertEquals(files[1]['name'], 'multi word name.png')
        self.assertEquals(files[1]['datetime'], datetime(current_year, 2, 21, 13, 27, 0))

        self.assertEquals(files[2]['datetime'], datetime(2013, 2, 20, 0, 0, 0))
        self.assertEquals(files[2]['size'], 195)
        self.assertEquals(files[2]['name'], 'README.txt')
        self.assertEquals(files[2]['owner'], 'rharrigan')
        self.assertEquals(files[2]['group'], 'wheel')

    def test_dir_parse_patched_regex(self):
        self.mock_ftp._set_dirlist("-rw-rw-r-- 1 rharrigan read-only   47 Feb 20 11:39 Cool.txt\n" +
                       "-rw-rw-r-- 1 rharrigan nobody 2085 Feb 21 13:27 multi word name.png\n" +
                       "-rw-rw-r-- 1 rharrigan dodgy-group-name  195 Feb 20 2013 README.txt\n")
        files = self.pretty.list(extra=True)
        self.assertEquals(len(files), 3)

        current_year = int(datetime.now().strftime('%Y'))
        self.assertEquals(files[0]['group'], 'read-only')
        self.assertEquals(files[1]['name'], 'multi word name.png')
        self.assertEquals(files[1]['datetime'], datetime(current_year, 2, 21, 13, 27, 0))

        self.assertEquals(files[2]['datetime'], datetime(2013, 2, 20, 0, 0, 0))
        self.assertEquals(files[2]['size'], 195)
        self.assertEquals(files[2]['name'], 'README.txt')
        self.assertEquals(files[2]['owner'], 'rharrigan')
        self.assertEquals(files[2]['group'], 'dodgy-group-name')

    def test_fallthrough(self):
        self.assertTrue(self.pretty.sendcmd('hello'), 'hello')

    def test_set_pasv(self):
        ftpretty(None, None, None, ftp_conn=self.mock_ftp, passive=False)

    def test_close(self):
        self.pretty.close()


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(FtprettyTestCase))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
