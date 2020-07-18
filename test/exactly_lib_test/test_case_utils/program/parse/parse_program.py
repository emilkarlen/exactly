import unittest

from exactly_lib.test_case_utils.program.parse import parse_program as sut
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_utils.program.parse import parse_system_program
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseSystemProgram)


class TestParseSystemProgram(unittest.TestCase):
    def test(self):
        # ARRANGE #
        program_name_case = parse_system_program.ProgramNameCase(
            'constant name',
            source_element='program_name',
            expected_resolved_value='program_name',
            expected_symbol_references=[],
        )
        arguments_case = parse_system_program.ArgumentsCase('single constant argument',
                                                            source_elements=['the_argument'],
                                                            expected_resolved_values=lambda tcds: ['the_argument'],
                                                            expected_symbol_references=[])

        for consume_last_line_if_is_at_eol_after_parse in [False, True]:
            parser = sut.program_parser(consume_last_line_if_is_at_eol_after_parse)
            with self.subTest(consume_last_line_if_is_at_eol_after_parse=
                              consume_last_line_if_is_at_eol_after_parse):
                parse_system_program.check_parsing_of_program(self,
                                                              parser,
                                                              pgm_args.system_program_argument_elements,
                                                              program_name_case,
                                                              arguments_case,
                                                              SymbolTable({}))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
