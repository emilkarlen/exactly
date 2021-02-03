from exactly_lib.impls.instructions.assert_.process_output import exit_code as sut
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Checker
from exactly_lib_test.section_document.test_resources import parse_checker

CHECKER = Checker(sut.Parser())

PARSE_CHECKER = parse_checker.Checker(sut.Parser())
