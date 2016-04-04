import unittest

from shellcheck_lib.util.textformat.formatting.text import wrapper as sut


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


class TestNoWordWrap(unittest.TestCase):
    def test_empty_lines(self):
        # ARRANGE #
        wrapper = sut.Wrapper(page_width=5)
        # ACT #
        lines = wrapper.no_word_wrap(['',
                                      ''])
        # ASSERT #
        self.assertEqual(['',
                          ''],
                         lines)

    def test_input_lines_that_all_fit_on_single_output_line(self):
        # ARRANGE #
        wrapper = sut.Wrapper(page_width=5)
        # ACT #
        lines = wrapper.no_word_wrap(['12',
                                      '',
                                      'ab'])
        # ASSERT #
        self.assertEqual(['12',
                          '',
                          'ab'],
                         lines)

    def test_input_lines_that_do_not_fit_on_single_output_line(self):
        # ARRANGE #
        wrapper = sut.Wrapper(page_width=5)
        # ACT #
        lines = wrapper.no_word_wrap(['123 567',
                                      'abc efg'])
        # ASSERT #
        self.assertEqual(['123 5',
                          '67',
                          'abc e',
                          'fg'],
                         lines)

    def test_indentation_when_all_input_lines_fit_on_single_output_line(self):
        # ARRANGE #
        wrapper = sut.Wrapper(page_width=5)
        indent = sut.Indent('>',
                            '>>')
        wrapper.push_indent(indent)
        # ACT #
        lines = wrapper.no_word_wrap(['fst', 'snd'])
        # ASSERT #
        self.assertEqual(['>fst',
                          '>>snd'],
                         lines)

    def test_indentation_when_first_input_line_do_not_fit_on_single_output_line(self):
        # ARRANGE #
        wrapper = sut.Wrapper(page_width=5)
        indent = sut.Indent('>',
                            '>>')
        wrapper.push_indent(indent)
        # ACT #
        lines = wrapper.no_word_wrap(['2345678'])
        # ASSERT #
        self.assertEqual(['>2345',
                          '>>678'],
                         lines)


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


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestIndent))
    ret_val.addTest(unittest.makeSuite(TestIndentIncreaseContextManager))
    ret_val.addTest(unittest.makeSuite(TestNoWordWrap))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
