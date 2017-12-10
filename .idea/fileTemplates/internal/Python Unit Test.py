import unittest

def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCase),
    ])

class TestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
