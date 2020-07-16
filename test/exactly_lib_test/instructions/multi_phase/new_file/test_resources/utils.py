from enum import Enum

from exactly_lib.instructions.multi_phase import new_file as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelNonHdsOptionType, \
    PathRelativityVariants
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_non_hds, \
    default_conf_rel_non_hds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Step(Enum):
    VALIDATE_PRE_SDS = 1
    MAIN = 2


DISALLOWED_RELATIVITIES = [
    RelOptionType.REL_RESULT,
    RelOptionType.REL_HDS_CASE,
    RelOptionType.REL_HDS_ACT,
]

AN_ALLOWED_DST_FILE_RELATIVITY = conf_rel_non_hds(RelNonHdsOptionType.REL_TMP)

ALLOWED_DST_FILE_RELATIVITIES = [
    conf_rel_non_hds(RelNonHdsOptionType.REL_ACT),
    conf_rel_non_hds(RelNonHdsOptionType.REL_TMP),
    conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
    default_conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),

]

ACCEPTED_RELATIVITY_VARIANTS = PathRelativityVariants({RelOptionType.REL_ACT,
                                                       RelOptionType.REL_TMP,
                                                       RelOptionType.REL_CWD},
                                                      absolute=False)

IS_FAILURE_OF_VALIDATION = validation.is_arbitrary_validation_failure()
IS_FAILURE = asrt_text_doc.is_any_text()
IS_SUCCESS = asrt.is_none


def just_parse(source: ParseSource,
               phase_is_after_act: bool = True):
    sut.EmbryoParser(phase_is_after_act).parse(ARBITRARY_FS_LOCATION_INFO, source)
