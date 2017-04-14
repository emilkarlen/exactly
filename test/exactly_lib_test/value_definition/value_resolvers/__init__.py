import unittest

from exactly_lib_test.value_definition.value_resolvers import path_part_resolvers


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(path_part_resolvers.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
