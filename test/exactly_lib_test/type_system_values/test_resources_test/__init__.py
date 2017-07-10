import unittest


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
