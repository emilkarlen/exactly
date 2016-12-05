from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.entity_names import SUITE_REPORTER_ENTITY_TYPE_NAME
from exactly_lib.help.utils.name_and_cross_ref import SingularNameAndCrossReference


def suite_reporter_cross_ref(reporter_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(SUITE_REPORTER_ENTITY_TYPE_NAME, reporter_name)


PROGRESS_REPORTER = SingularNameAndCrossReference('progress',
                                                  suite_reporter_cross_ref('progress'))
JUNIT_REPORTER = SingularNameAndCrossReference('junit',
                                               suite_reporter_cross_ref('junit'))

ALL_SUITE_REPORTERS = [
    PROGRESS_REPORTER,
    JUNIT_REPORTER,
]

ALL_SUITE_REPORTERS_DICT = {
    PROGRESS_REPORTER.singular_name: PROGRESS_REPORTER,
    JUNIT_REPORTER.singular_name: JUNIT_REPORTER,
}

DEFAULT_REPORTER = PROGRESS_REPORTER


def all_suite_reporters_cross_refs() -> list:
    return [reporter.cross_reference_target
            for reporter in ALL_SUITE_REPORTERS]
