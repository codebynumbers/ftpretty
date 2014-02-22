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

    def test_list(self):
        self.mock_ftp._set_files(['a.txt', 'b.txt'])
        self.assertEquals(len(self.pretty.list()), 2)

    def test_put(self):
        size = self.pretty.put('AUTHORS.rst', 'AUTHORS.rst')
        self.assertEquals(size, os.path.getsize('AUTHORS.rst'))
    
    def test_get(self):
        self.pretty.get('remote_file.txt', 'local_copy.txt')
        self.assertTrue(os.path.isfile('local_copy.txt'))
        os.unlink('local_copy.txt')
                
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



def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(FtprettyTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

