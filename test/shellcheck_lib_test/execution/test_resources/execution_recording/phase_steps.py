from shellcheck_lib.execution import phase_step

PRE_EDS_VALIDATION_STEPS = [
    phase_step.SETUP_PRE_VALIDATE,
    phase_step.ACT_VALIDATE_PRE_EDS,
    phase_step.ASSERT_VALIDATE_PRE_EDS,
    phase_step.CLEANUP_VALIDATE_PRE_EDS,
]
