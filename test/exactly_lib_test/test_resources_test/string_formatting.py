import unittest

from exactly_lib_test.test_resources import string_formatting as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    formatter = sut.StringFormatter({'a': 'A', 'b': 'B'})

    def test_format_dict_without_extra(self):
        self.assertEqual({'a': 'A',
                          'b': 'B',
                          },
                         self.formatter.format_dict())

    def test_format_dict_with_extra(self):
        self.assertEqual({'a': 'A',
                          'b': 'B',
                          'c': 'C',
                          },
                         self.formatter.format_dict(c='C'))

    def test_format_without_extra(self):
        self.assertEqual('A B',
                         self.formatter.format('{a} {b}'))

    def test_format_with_extra(self):
        self.assertEqual('A B C',
                         self.formatter.format('{a} {b} {c}', c='C'))

    def test_format_strings_without_extra(self):
        self.assertEqual(['A _',
                          '_ B'],
                         self.formatter.format_strings(['{a} _', '_ {b}']))

    def test_format_strings_with_extra(self):
        self.assertEqual(['A _',
                          '_ B',
                          'C'],
                         self.formatter.format_strings(['{a} _', '_ {b}', '{c}'],
                                                       c='C'))

    def test_new_without_extra(self):
        formatter = sut.StringFormatter({'a': 'A', 'b': 'B'})

        new_formatter = formatter.new_with()

        self.assertEqual('A B',
                         new_formatter.format('{a} {b}'))

    def test_new_with_extra(self):
        formatter = sut.StringFormatter({'a': 'A', 'b': 'B'})

        new_formatter = formatter.new_with(c='C')

        self.assertEqual('A B C',
                         new_formatter.format('{a} {b} {c}'))
