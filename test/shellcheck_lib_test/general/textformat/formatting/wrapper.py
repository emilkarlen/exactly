import unittest

from shellcheck_lib.general.textformat.formatting import wrapper as sut


class TestIndent(unittest.TestCase):
    def test_construction(self):
        wrapper = sut.Wrapper(page_width=10)
        self.assertEqual(10,
                         wrapper.text_wrapper.width)
        _check_current_indent(self, wrapper, sut.Indent('', ''))
        self.assertFalse(wrapper.saved_indents_stack,
                         'Saved indent stack')

    def test_push_indent(self):
        wrapper = sut.Wrapper()
        indent = sut.Indent('first line',
                            'following lines')
        wrapper.push_indent(indent)
        _check_current_indent(self, wrapper, indent)
        self.assertEqual([sut.Indent('', '')],
                         wrapper.saved_indents_stack,
                         'Saved indent stack')

    def test_push_indent_increase(self):
        wrapper = sut.Wrapper()
        first_indent = sut.Indent('a1',
                                  'a2')
        delta = sut.Indent('b1',
                           'b2')
        wrapper.push_indent(first_indent)
        wrapper.push_indent_increase(delta)

        sum_indent = sut.Indent(first_indent.first_line + delta.first_line,
                                first_indent.following_lines + delta.following_lines)

        _check_current_indent(self, wrapper, sum_indent)
        self.assertEqual([first_indent, sut.Indent('', '')],
                         wrapper.saved_indents_stack,
                         'Saved first_indent stack')

    def test_pop_indent(self):
        wrapper = sut.Wrapper()
        indent1 = sut.Indent('a1',
                             'a2')
        wrapper.push_indent(indent1)
        wrapper.push_indent(sut.Indent('b1', 'b2'))
        wrapper.pop_indent()
        _check_current_indent(self, wrapper, indent1)
        self.assertEqual([sut.Indent('', '')],
                         wrapper.saved_indents_stack,
                         'Saved indent1 stack')


class TestIndentIncreaseContextManager(unittest.TestCase):
    def test(self):
        wrapper = sut.Wrapper(page_width=100)
        with wrapper.indent_increase(sut.identical_indent('[INDENT]')):
            lines = wrapper.wrap('text')
        self.assertEqual(['[INDENT]text'],
                         lines,
                         'Resulting lines')
        _check_indent(self,
                      wrapper,
                      sut.identical_indent(''),
                      [])


def _check_indent(put: unittest.TestCase,
                  wrapper: sut.Wrapper,
                  expected_current_indent: sut.Indent,
                  expected_saved_stack: list):
    _check_current_indent(put, wrapper, expected_current_indent)
    put.assertEqual(expected_saved_stack,
                    wrapper.saved_indents_stack,
                    'Saved indent stack')


def _check_current_indent(put: unittest.TestCase,
                          wrapper: sut.Wrapper,
                          expected: sut.Indent):
    put.assertEqual(expected.first_line,
                    wrapper.text_wrapper.initial_indent,
                    'Initial indent of TextWrapper')
    put.assertEqual(expected.following_lines,
                    wrapper.text_wrapper.subsequent_indent,
                    'Subsequent indent of TextWrapper')
    put.assertEqual(expected,
                    wrapper.current_indent,
                    'Current indent')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestIndent))
    ret_val.addTest(unittest.makeSuite(TestIndentIncreaseContextManager))
    return ret_val


if __name__ == '__main__':
    unittest.main()
