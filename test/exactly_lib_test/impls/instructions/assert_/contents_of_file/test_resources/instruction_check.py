from exactly_lib.impls.instructions.assert_ import contents_of_file as sut
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.section_document.test_resources import parse_checker

CHECKER = instruction_check.Checker(sut.parser('the-instruction-name'))

PARSE_CHECKER = parse_checker.Checker(sut.parser('the-instruction-name'))
