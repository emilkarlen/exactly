import unittest
from xml.etree.ElementTree import Element

from exactly_lib.util.textformat.formatting.html.paragraph_item import table as sut
from exactly_lib.util.textformat.structure.structures import paras
from exactly_lib.util.textformat.structure.table import Table, TableFormat
from shellcheck_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import ConstantPRenderer
from shellcheck_lib_test.util.textformat.formatting.html.test_resources import as_unicode_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEmptyTable),
        unittest.makeSuite(TestMultipleRowsMultipleColumn),
        unittest.makeSuite(TestHeaderRowTable),
        unittest.makeSuite(TestHeaderColumnTable),
        unittest.makeSuite(TestHeaderRowAndColumnTable),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestEmptyTable(unittest.TestCase):
    def test_empty(self):
        # ARRANGE #
        root = Element('root')
        table = Table(TableFormat(),
                      [])
        # ACT #
        ret_val = sut.render(ConstantPRenderer('para text'),
                             root, table)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root />',
                         xml_string)
        self.assertIs(root,
                      ret_val)

    def test_single_empty_row(self):
        # ARRANGE #
        root = Element('root')
        table = Table(TableFormat(),
                      [[]])
        # ACT #
        ret_val = sut.render(ConstantPRenderer('para text'),
                             root, table)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root />',
                         xml_string)
        self.assertIs(root,
                      ret_val)


class TestMultipleRowsMultipleColumn(unittest.TestCase):
    def test_just_header_row_single_cell(self):
        # ARRANGE #
        root = Element('root')
        table = Table(TableFormat(),
                      [
                          [paras('ignored'), paras('ignored')],
                          [paras('ignored'), paras('ignored')],
                      ])
        # ACT #
        ret_val = sut.render(ConstantPRenderer('para text'),
                             root, table)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<table>'
                         '<tr>'
                         '<td><p>para text</p></td>'
                         '<td><p>para text</p></td>'
                         '</tr>'
                         '<tr>'
                         '<td><p>para text</p></td>'
                         '<td><p>para text</p></td>'
                         '</tr>'
                         '</table>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)


class TestHeaderRowTable(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        root = Element('root')
        table = Table(TableFormat(first_row_is_header=True),
                      [
                          [paras('ignored'), paras('ignored')],
                          [paras('ignored'), paras('ignored')],
                      ])
        # ACT #
        ret_val = sut.render(ConstantPRenderer('para text'),
                             root, table)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<table>'
                         '<tr>'
                         '<th><p>para text</p></th>'
                         '<th><p>para text</p></th>'
                         '</tr>'
                         '<tr>'
                         '<td><p>para text</p></td>'
                         '<td><p>para text</p></td>'
                         '</tr>'
                         '</table>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)


class TestHeaderColumnTable(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        root = Element('root')
        table = Table(TableFormat(first_column_is_header=True),
                      [
                          [paras('ignored'), paras('ignored')],
                          [paras('ignored'), paras('ignored')],
                      ])
        # ACT #
        ret_val = sut.render(ConstantPRenderer('para text'),
                             root, table)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<table>'
                         '<tr>'
                         '<th><p>para text</p></th>'
                         '<td><p>para text</p></td>'
                         '</tr>'
                         '<tr>'
                         '<th><p>para text</p></th>'
                         '<td><p>para text</p></td>'
                         '</tr>'
                         '</table>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)


class TestHeaderRowAndColumnTable(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        root = Element('root')
        table = Table(TableFormat(first_row_is_header=True,
                                  first_column_is_header=True),
                      [
                          [paras('ignored'), paras('ignored')],
                          [paras('ignored'), paras('ignored')],
                      ])
        # ACT #
        ret_val = sut.render(ConstantPRenderer('para text'),
                             root, table)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<table>'
                         '<tr>'
                         '<th><p>para text</p></th>'
                         '<th><p>para text</p></th>'
                         '</tr>'
                         '<tr>'
                         '<th><p>para text</p></th>'
                         '<td><p>para text</p></td>'
                         '</tr>'
                         '</table>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)
