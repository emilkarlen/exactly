from exactly_lib.impls.instructions.multi_phase.timeout import parse as sut
from exactly_lib_test.impls.instructions.multi_phase.test_resources import instruction_embryo_check as embryo_check
from exactly_lib_test.section_document.test_resources import parse_checker

CHECKER = embryo_check.Checker(sut.EmbryoParser())

PARSE_CHECKER = parse_checker.Checker(sut.EmbryoParser())
