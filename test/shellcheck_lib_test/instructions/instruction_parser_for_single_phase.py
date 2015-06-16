import unittest

from shellcheck_lib.general import line_source
from shellcheck_lib.instructions import instruction_parser_for_single_phase as parse
from shellcheck_lib_test.document.test_resources import assert_equals_line


def name_argument_splitter(s: str) -> (str, str):
    return s[0], s[1:]


def new_line(text: str) -> line_source.Line:
    return line_source.Line(1, text)


class TestParse(unittest.TestCase):
    def test_when_instruction_name_not_in_dict_then_exception_should_be_raised(self):
        phase_parser = parse.InstructionParserForDictionaryOfInstructions(name_argument_splitter, {})
        line = new_line('Ia')
        with self.assertRaises(parse.UnknownInstructionException) as cm:
            phase_parser.apply(line)
            self.assertEqual('I',
                             cm.ex.instruction_name,
                             'Instruction name')
            assert_equals_line(self,
                               line,
                               cm.ex.line,
                               'Source line')


# def test_handling_of_invalid_argument_exception_from_parser(self):
# parser = exitcode.Parser()
# self.assertRaises(parse.SingleInstructionInvalidArgumentException,
#                           parser.apply,
#                           '')


# class SingleInstructionParserThatRaisesInvalidArgumentError(parse.SingleInstructionParser):
#     def __init__(self,
#                  error_message: str):
#         self.error_message = error_message
#
#     def apply(self, instruction_argument: str) -> i.Instruction:
#         raise parse.SingleInstructionInvalidArgumentException(self.error_message)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    return ret_val


if __name__ == '__main__':
    unittest.main()
