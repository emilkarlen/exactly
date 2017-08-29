import unittest


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMisc),
    ])


class TestMisc(unittest.TestCase):
    def test(self):
        # ARRANGE #
        self.fail('todo')
