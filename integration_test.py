import unittest
from ftpretty import ftpretty
import shutil
import os

conn = ftpretty('127.0.0.1')
conn.login(anonymous=True)
class FtprettyIntegration(unittest.TestCase):
    def test_get(self):
        self.assertEqual([], conn.list(extra=True))
        conn.put(None, 'b/b.txt', b'blah')
        self.assertEqual(set(['b.txt']), set([f.name for f in conn.list('b', extra=True)]))
        contents = conn.get('b/b.txt')    
        self.assertEqual(b'blah', contents)   
        conn.delete('b/b.txt')
        conn.delete('b')
 
    def test_welcome(self):
        self.assertTrue(conn.get_welcome())

    def test_put(self):
        self.assertEqual([], conn.list(extra=True))
        conn.put(None, 'a.txt', b'blah')
        conn.put(None, 'b/b.txt', b'blah')
        self.assertEqual(set(['a.txt', 'b']), set([f.name for f in conn.list(extra=True)]))
        self.assertEqual(set(['b.txt']), set([f.name for f in conn.list('b', extra=True)]))
        conn.delete('a.txt')
        conn.delete('b/b.txt')
        conn.delete('b')
        self.assertEqual([], conn.list(extra=True))

    def test_is_file(self):
        conn.put(None, 'a/deeply/nested/folder/file.log', b'log content')
        conn.descend('a/deeply/nested/folder')
        self.assertEqual(conn.is_file('file.log'), True)
    
    def test_is_folder(self):
        conn.put(None, 'a/deeply/nested/folder', b'log content')
        conn.descend('a/deeply/nested/')
        self.assertEqual(conn.is_folder('folder'), True)

    def test_ascend(self):
        conn.put(None, 'a/deeply/nested/folder/file.log', b'log content')
        conn.descend('a/deeply/nested/folder')
        conn.ascend()
        self.assertEqual(set([conn.pwd()]), set(['a/deeply/nested']))
        conn.cd('../../..')
        self.assertEqual([], conn.list('a/deeply/nested/folder', extra=True))
        conn.delete('a/deeply/nested')
        conn.delete('a/deeply')
        conn.delete('a')
        self.assertEqual([], conn.list(extra=True))

    def test_put_tree(self):
        os.mkdir('testdata')
        os.mkdir('testdata/a')        
        os.mkdir('testdata/a/b')        
        os.mkdir('testdata/a/b/c')  
        with open('testdata/a/a.txt', 'wb') as fh:
            fh.write(b'blah')
        with open('testdata/a/b/b.txt', 'wb') as fh:
            fh.write(b'blah')
        with open('testdata/a/b/c/c.txt', 'wb') as fh:
            fh.write(b'blah')
        conn.put_tree('testdata', '.')
        conn.descend('a/b/c')
        self.assertEqual(set(['c.txt']), set([f.name for f in conn.list(extra=True)]))
        conn.delete('c.txt')
        conn.cd('..')
        self.assertEqual(set(['c','b.txt']), set([f.name for f in conn.list(extra=True)]))
        conn.delete('c')
        conn.delete('b.txt')
        conn.cd('..')
        self.assertEqual(set(['b', 'a.txt']), set([f.name for f in conn.list(extra=True)]))
        conn.delete('b')
        conn.delete('a.txt')
        conn.cd('..')
        self.assertEqual(set(['a']), set([f.name for f in conn.list(extra=True)]))
        conn.delete('a')
        self.assertEqual([], conn.list(extra=True))
        shutil.rmtree("testdata")

    def test_get_tree(self):
        conn.put(None, 'a/b/c/c.log', b'log content')
        conn.put(None, 'a/b/b.log', b'log content')
        conn.put(None, 'a/a.log', b'log content')
        os.mkdir('testdata')
        conn.get_tree('.', 'testdata')
        self.assertTrue(os.path.exists('testdata/a/b/c/c.log'))
        self.assertTrue(os.path.exists('testdata/a/b/b.log'))
        self.assertTrue(os.path.exists('testdata/a/a.log'))
        conn.delete('a/b/c/c.log')
        conn.delete('a/b/c')
        conn.delete('a/b/b.log')
        conn.delete('a/b')
        conn.delete('a/a.log')
        conn.delete('a')
        self.assertEqual([], conn.list(extra=True))
        shutil.rmtree("testdata")

    def test_list(self):
        self.assertEqual([], conn.list(extra=True))
        conn.put(None, 'a.txt', b'blah')
        conn.put(None, 'b/b.txt', b'blah')
        self.assertEqual(set(['a.txt', 'b']), set([f.name for f in conn.list(extra=True)]))
        self.assertEqual(set(['b.txt']), set([f.name for f in conn.list('b', extra=True)]))
        conn.delete('a.txt')
        conn.delete('b/b.txt')
        conn.delete('b')
        self.assertEqual([], conn.list(extra=True))

    def test_descend(self):
        conn.put(None, 'a/deeply/nested/folder/file.log', b'log content')
        conn.descend('a/deeply/nested/folder')
        self.assertEqual(set(['file.log']), set([f.name for f in conn.list(extra=True)]))
        content = conn.get('file.log')
        self.assertEqual(b'log content', content)
        conn.cd('../../../..')
        conn.delete('a/deeply/nested/folder/file.log')
        self.assertEqual([], conn.list('a/deeply/nested/folder', extra=True))
        conn.delete('a/deeply/nested/folder')
        conn.delete('a/deeply/nested')
        conn.delete('a/deeply')
        conn.delete('a')
        self.assertEqual([], conn.list(extra=True))

    def test_delete(self):
        self.assertEqual([], conn.list(extra=True))
        conn.put(None, 'b/b.txt', b'blah')
        self.assertEqual(set(['b.txt']), set([f.name for f in conn.list('b', extra=True)]))
        conn.delete('b/b.txt')
        conn.delete('b')
        self.assertEqual([], conn.list(extra=True))

    def test_cd(self):
        conn.put(None, 'a/deeply/nested/folder/file.log', b'log content')
        conn.cd('a')
        conn.cd('deeply/nested')
        conn.cd('folder')
        self.assertEqual(set(['file.log']), set([f.name for f in conn.list(extra=True)]))
        conn.cd('..')
        self.assertEqual(set(['folder']), set([f.name for f in conn.list(extra=True)]))
        conn.cd('../../..')
        conn.delete('a/deeply/nested/folder/file.log')
        conn.delete('a/deeply/nested/folder')
        conn.delete('a/deeply/nested')
        conn.delete('a/deeply')
        conn.delete('a')
        self.assertEqual([], conn.list(extra=True))

    def test_pwd(self):
        conn.put(None, 'a/deeply/nested/folder/file.log', b'log content')
        conn.cd('a')
        conn.cd('deeply/nested')
        conn.cd('folder')
        self.assertEqual('/a/deeply/nested/folder', conn.pwd())
        conn.cd('../../../..')
        conn.delete('a/deeply/nested/folder/file.log')
        conn.delete('a/deeply/nested/folder')
        conn.delete('a/deeply/nested')
        conn.delete('a/deeply')
        conn.delete('a')
        self.assertEqual([], conn.list(extra=True))

    def test_rename(self):
        conn.put(None, 'file.log', b'log content')
        conn.rename('file.log', 'renamed.txt')
        self.assertEqual(set(['renamed.txt']), set([f.name for f in conn.list(extra=True)]))
        conn.delete('renamed.txt')
        self.assertEqual([], conn.list(extra=True))

    def test_mkdir(self):
        conn.mkdir('a')
        self.assertEqual(set(['a']), set([f.name for f in conn.list(extra=True)]))
        conn.delete('a')
        self.assertEqual([], conn.list(extra=True))


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(FtprettyIntegration))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())