import unittest


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestInvalidSymbolNameArguments)


class TestInvalidSymbolNameArguments(unittest.TestCase):
    def test_more_than_one_name(self):
        pass


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
