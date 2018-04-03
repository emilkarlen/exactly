from enum import Enum

from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib.section_document.parse_source import ParseSource

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelNonHomeOptionType, \
    PathRelativityVariants
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_non_home, \
    default_conf_rel_non_home
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Step(Enum):
    VALIDATE_PRE_SDS = 1
    MAIN = 2


DISALLOWED_RELATIVITIES = [
    RelOptionType.REL_RESULT,
    RelOptionType.REL_HOME_CASE,
    RelOptionType.REL_HOME_ACT,
]
ALLOWED_DST_FILE_RELATIVITIES = [
    conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
    conf_rel_non_home(RelNonHomeOptionType.REL_TMP),
    conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
    default_conf_rel_non_home(RelNonHomeOptionType.REL_CWD),

]
ACCEPTED_RELATIVITY_VARIANTS = PathRelativityVariants({RelOptionType.REL_ACT,
                                                       RelOptionType.REL_TMP,
                                                       RelOptionType.REL_CWD},
                                                      absolute=False)
IS_FAILURE_OF_VALIDATION = asrt.is_instance(str)
IS_FAILURE = asrt.is_instance(str)
IS_SUCCESS = asrt.is_none


def just_parse(source: ParseSource,
               phase_is_after_act: bool = True):
    sut.EmbryoParser('the-instruction-name', phase_is_after_act).parse(source)