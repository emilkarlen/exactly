from exactly_lib.common.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity_names import SUITE_REPORTER_ENTITY_TYPE_NAME
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId


def suite_reporter_cross_ref(reporter_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(SUITE_REPORTER_ENTITY_TYPE_NAME, reporter_name)


def _name_and_ref(name: str,
                  single_line_description_str: str) -> SingularNameAndCrossReferenceId:
    return SingularNameAndCrossReferenceId(name,
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
