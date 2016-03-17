import unittest

from shellcheck_lib.util import monad as sut


class TestMapM(unittest.TestCase):
    def test_empty_list(self):
        actual = sut.map_m('success-result', 'argument', ())
        self.assertEqual('success-result',
                         actual)

    def test_success(self):
        actual = sut.map_m('success-result',
                           'argument',
                           (lambda x: 'success-result',))
        self.assertEqual('success-result',
                         actual)

    def test_fail(self):
        actual = sut.map_m('success-result',
                           'argument',
                           (lambda x: 'success-result',
                            lambda x: 'fail-result',
                            lambda x: 'success-result'))
        self.assertEqual('fail-result',
                         actual)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestMapM))
    return ret_val


if __name__ == '__main__':
    unittest.main()
