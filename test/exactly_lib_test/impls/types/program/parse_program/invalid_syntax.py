import unittest

from exactly_lib.impls.types.program.parse import parse_program as sut
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.test_resources import invalid_syntax
from exactly_lib_test.section_document.element_parsers.test_resources.parsing import ParserAsLocationAwareParser
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import \
    PgmAndArgsWArgumentsAbsStx, FullProgramAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestReferenceToProgramWithInvalidSymbolName(),
        TestInvalidArguments(),
        TestInvalidTransformer(),
        TestInvalidStdin(),
    ])


class TestReferenceToProgramWithInvalidSymbolName(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for case in invalid_syntax.plain_symbol_cases():
            with self.subTest(case.name):
                syntax = ProgramOfSymbolReferenceAbsStx(case.value)
                # ACT & ASSERT #
                PARSE_CHECKER.check_invalid_syntax__abs_stx(self, syntax)


class TestInvalidArguments(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for program_case in pgm_and_args_cases.cases__w_argument_list__including_program_reference():
            for arguments_case in invalid_syntax.arguments_cases():
                with self.subTest(program=program_case.name,
                                  arguments=arguments_case.name):
                    syntax = PgmAndArgsWArgumentsAbsStx(program_case.pgm_and_args,
                                                        arguments_case.value)
                    # ACT & ASSERT #
                    PARSE_CHECKER.check_invalid_syntax__abs_stx(self, syntax)


class TestInvalidTransformer(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for program_case in pgm_and_args_cases.cases__w_argument_list__including_program_reference():
            for transformer_case in invalid_syntax.transformer_cases():
                with self.subTest(program=program_case.name,
                                  transformer=transformer_case.name):
                    syntax = FullProgramAbsStx(program_case.pgm_and_args,
                                               transformation=transformer_case.value)
                    # ACT & ASSERT #
                    PARSE_CHECKER.check_invalid_syntax__abs_stx(self, syntax)


class TestInvalidStdin(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for program_case in pgm_and_args_cases.cases__w_argument_list__including_program_reference():
            for transformer_case in invalid_syntax.stdin_cases():
                with self.subTest(program=program_case.name,
                                  transformer=transformer_case.name):
                    syntax = FullProgramAbsStx(program_case.pgm_and_args,
                                               stdin=transformer_case.value)
                    # ACT & ASSERT #
                    PARSE_CHECKER.check_invalid_syntax__abs_stx(self, syntax)


PARSE_CHECKER = parse_checker.Checker(ParserAsLocationAwareParser(sut.program_parser()))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
