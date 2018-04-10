from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity.all_entity_types import SUITE_REPORTER_ENTITY_TYPE_NAMES
from exactly_lib.util.textformat.structure.core import StringText


class SuiteReporterInfo(SingularNameAndCrossReferenceId):
    def __init__(self,
                 singular_name: str,
                 single_line_description_str: str,
                 cross_reference_target: CrossReferenceId):
        super().__init__(singular_name,
                         single_line_description_str,
                         cross_reference_target)

    @property
    def singular_name_text(self) -> StringText:
        return syntax_text(self._singular_name)


def suite_reporter_cross_ref(reporter_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(SUITE_REPORTER_ENTITY_TYPE_NAMES,
                                  reporter_name)


def _name_and_ref(name: str,
                  single_line_description_str: str) -> SingularNameAndCrossReferenceId:
    return SuiteReporterInfo(name,
                             single_line_description_str,
                             suite_reporter_cross_ref(name))


PROGRESS_REPORTER = _name_and_ref('progress',
                                  'Reports execution progress in a human readable form.')
JUNIT_REPORTER = _name_and_ref('junit',
                               'Outputs JUnit XML.')

ALL_SUITE_REPORTERS = [
    PROGRESS_REPORTER,
    JUNIT_REPORTER,
]

# Bad to have definition of default value in help package.
# But do not know where the best place to put it is,
# so it remains here for some time ...
DEFAULT_REPORTER = PROGRESS_REPORTER


def all_suite_reporters_cross_refs() -> list:
    return [x.cross_reference_target
            for x in ALL_SUITE_REPORTERS]
