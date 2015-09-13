import pathlib
import unittest

from shellcheck_lib.test_case.preprocessor import IdentityPreprocessor


class TestIdentityPreprocessor(unittest.TestCase):
    def test(self):
        processor = IdentityPreprocessor()
        path = pathlib.Path('test-case-file.txt')
        source = 'test case source'
        result = processor.apply(path, source)
        self.assertEqual(source,
                         result)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestIdentityPreprocessor))
    return ret_val


if __name__ == '__main__':
    unittest.main()
