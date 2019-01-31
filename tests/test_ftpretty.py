from datetime import datetime
from ftpretty import ftpretty
from io import BytesIO
from .mock_ftp import MockFTP
from os import mkdir, path, remove, rmdir
from unittest import TestCase, TestLoader, TestSuite, TextTestRunner

class FtprettyTestCase(TestCase):

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

    def test_put_contents(self):
        with open("/dev/urandom","rb") as stream:
            put_contents = stream.read(256)
        size = self.pretty.put(None, 'foobar.txt', put_contents)
        self.assertEqual(size, len(BytesIO(put_contents).getvalue()))

    def test_put_file(self):
        with open('foobar.txt', 'rb') as file_:
            size = self.pretty.put(file_, 'foobar.txt')
        self.assertEqual(size, path.getsize('foobar.txt'))

    def test_put_filename(self):
        size = self.pretty.put('foobar.txt', 'foobar.txt')
        self.assertEqual(size, path.getsize('foobar.txt'))
        remove('foobar.txt')

    def test_put_r(self):
        with open("/dev/urandom","rb") as stream:
            contents = stream.read(256)
        mkdir('tree')
        mkdir('tree/bar')
        with open('tree/foo.txt', 'wb') as file:
            file.write(contents)
        with open('tree/bar/baz.txt', 'wb') as file:
            file.write(contents)
        tree = self.pretty.put_r('tree', '/tree')
        self.assertEqual(tree, '/tree')
        remove('tree/bar/baz.txt')
        remove('tree/foo.txt')
        rmdir('tree/bar')
        rmdir('tree')

    def test_get_contents(self):
        with open("/dev/urandom","rb") as stream:
            get_contents = stream.read(256)
        if path.exists('remote_file.txt'):
            remove('remote_file.txt')
        with open('remote_file.txt', 'wb') as file:
            file.write(get_contents)
        self.mock_ftp._set_contents(get_contents)
        contents = self.pretty.get('remote_file.txt')
        self.assertEqual(contents, get_contents)
        remove('remote_file.txt')

    def test_get(self):
        with open("/dev/urandom","rb") as stream:
            get_contents = stream.read(256)
        self.mock_ftp._set_contents(get_contents)
        if path.exists('local_copy.txt'):
            remove('local_copy.txt')
        if path.exists('remote_file.txt'):
            remove('remote_file.txt')
        self.assertFalse(path.isfile('local_copy.txt'))
        self.assertFalse(path.isfile('remote_file.txt'))
        with open('remote_file.txt', 'wb') as file:
            file.write(get_contents)
        self.pretty.get('remote_file.txt', 'local_copy.txt')
        self.assertTrue(path.isfile('local_copy.txt'))
        with open('local_copy.txt', 'rb') as file:
            self.assertEqual(file.read(), get_contents)
        remove('local_copy.txt')
        remove('remote_file.txt')

    def test_get_filehandle(self):
        with open("/dev/urandom","rb") as stream:
            get_contents = stream.read(256)
        self.mock_ftp._set_contents(get_contents)
        if path.exists('local_copy.txt'):
            remove('local_copy.txt')
        if path.exists('remote_file.txt'):
            remove('remote_file.txt')
        self.assertFalse(path.isfile('local_copy.txt'))
        self.assertFalse(path.isfile('remote_file.txt'))
        with open('remote_file.txt', 'wb') as file:
            file.write(get_contents)
        with open('local_copy.txt', 'wb') as outfile:
            self.pretty.get('remote_file.txt', outfile)
        self.assertTrue(path.isfile('local_copy.txt'))
        with open('local_copy.txt', 'rb') as file:
            self.assertEqual(file.read(), get_contents)
        remove('local_copy.txt')
        remove('remote_file.txt')

    def test_delete(self):
        with open("/dev/urandom","rb") as stream:
            delete_contents = stream.read(256)
        if path.exists('delete_file.txt'):
            remove('delete_file.txt')
        with open('delete_file.txt', 'wb') as file:
            file.write(delete_contents)
        self.assertTrue(self.pretty.delete('delete_file.txt'))
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

    def test_fallthrough(self):
        self.assertTrue(self.pretty.sendcmd('hello'), 'hello')

    def test_set_pasv(self):
        ftpretty(None, None, None, ftp_conn=self.mock_ftp, passive=False)

    def test_close(self):
        self.pretty.close()


def suite():
    loader = TestLoader()
    suite = TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(FtprettyTestCase))
    return suite


if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite())
