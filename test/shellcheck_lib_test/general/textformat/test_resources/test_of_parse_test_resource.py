import unittest


class TestFailingScenarios(unittest.TestCase):
    pass


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    return ret_val


if __name__ == '__main__':
    unittest.main()
