from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.entity_names import SUITE_REPORTER_ENTITY_TYPE_NAME
from exactly_lib.help.utils.name_and_cross_ref import SingularNameAndCrossReferenceId


def suite_reporter_cross_ref(reporter_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(SUITE_REPORTER_ENTITY_TYPE_NAME, reporter_name)


def _name_and_ref(name: str) -> SingularNameAndCrossReferenceId:
    return SingularNameAndCrossReferenceId(name, suite_reporter_cross_ref(name))


PROGRESS_REPORTER = _name_and_ref('progress')
JUNIT_REPORTER = _name_and_ref('junit')

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
