from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.entity_names import SUITE_REPORTER_ENTITY_TYPE_NAME


def suite_reporter_cross_ref(reporter_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(SUITE_REPORTER_ENTITY_TYPE_NAME, reporter_name)


PROGRESS_REPORTER__NAME = 'progress'
JUNIT_REPORTER__NAME = 'junit'
PROGRESS_REPORTER__CROSS_REF = suite_reporter_cross_ref(PROGRESS_REPORTER__NAME)
JUNIT_REPORTER__CROSS_REF = suite_reporter_cross_ref(JUNIT_REPORTER__NAME)

ALL_SUITE_REPORTERS__CROSS_REFS = [
    PROGRESS_REPORTER__CROSS_REF,
    JUNIT_REPORTER__CROSS_REF,
]
