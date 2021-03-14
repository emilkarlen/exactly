import unittest

from exactly_lib.impls.instructions.multi_phase import new_file as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax


def just_parse(source: ParseSource,
               phase_is_after_act: bool = True):
    sut.EmbryoParser(phase_is_after_act).parse(ARBITRARY_FS_LOCATION_INFO, source)


PARSE_CHECKER__BEFORE_ACT = parse_checker.Checker(sut.EmbryoParser(False))
PARSE_CHECKER__AFTER_ACT = parse_checker.Checker(sut.EmbryoParser(True))


def check_invalid_syntax(put: unittest.TestCase, source: ParseSource):
    for phase_is_after_act in [False, True]:
        checker = PARSE_CHECKERS[phase_is_after_act]
        with put.subTest(phase_is_after_act=phase_is_after_act):
            checker.check_invalid_arguments(put, source)


def check_invalid_syntax__abs_stx(put: unittest.TestCase, source: AbstractSyntax):
    for phase_is_after_act in [False, True]:
        checker = PARSE_CHECKERS[phase_is_after_act]
        with put.subTest(phase_is_after_act=phase_is_after_act):
            checker.check_invalid_syntax__abs_stx(put, source)


PARSE_CHECKERS = {
    False: PARSE_CHECKER__BEFORE_ACT,
    True: PARSE_CHECKER__AFTER_ACT,
}
