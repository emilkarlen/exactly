from shellcheck_lib.execution import phase_step

PRE_EDS_VALIDATION_STEPS = [
    phase_step.SETUP__VALIDATE_PRE_EDS,
    phase_step.ACT__VALIDATE_PRE_EDS,
    phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS,
    phase_step.ASSERT__VALIDATE_PRE_EDS,
    phase_step.CLEANUP__VALIDATE_PRE_EDS,
]
