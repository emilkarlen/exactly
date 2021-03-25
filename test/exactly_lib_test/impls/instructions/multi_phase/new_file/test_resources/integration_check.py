from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.instructions.multi_phase import new_file as sut
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.section_document.test_resources import parse_checker

PARSE_CHECKER = parse_checker.Checker(sut.EmbryoParser(False))

CHECKER__BEFORE_ACT = embryo_check.Checker(sut.EmbryoParser(False))
CHECKER__AFTER_ACT = embryo_check.Checker(sut.EmbryoParser(True))

CHECKERS = {
    False: CHECKER__BEFORE_ACT,
    True: CHECKER__AFTER_ACT,
}


def checker(phase_is_after_act: bool) -> embryo_check.Checker[Optional[TextRenderer]]:
    return CHECKERS[phase_is_after_act]
