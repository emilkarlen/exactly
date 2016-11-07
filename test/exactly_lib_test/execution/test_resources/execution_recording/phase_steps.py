from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step

PRE_SDS_VALIDATION_STEPS__ONCE = [
    phase_step.SETUP__VALIDATE_PRE_SDS,
    phase_step.ACT__VALIDATE_PRE_SDS,
    phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
    phase_step.ASSERT__VALIDATE_PRE_SDS,
    phase_step.CLEANUP__VALIDATE_PRE_SDS,
]

PRE_SDS_VALIDATION_STEPS__TWICE = [
    phase_step.SETUP__VALIDATE_PRE_SDS,
    phase_step.SETUP__VALIDATE_PRE_SDS,
    phase_step.ACT__VALIDATE_PRE_SDS,
    phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
    phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS,
    phase_step.ASSERT__VALIDATE_PRE_SDS,
    phase_step.ASSERT__VALIDATE_PRE_SDS,
    phase_step.CLEANUP__VALIDATE_PRE_SDS,
    phase_step.CLEANUP__VALIDATE_PRE_SDS,
]
