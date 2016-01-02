from shellcheck_lib.execution import phase_step

PRE_EDS_VALIDATION_STEPS = [
    phase_step.SETUP__PRE_VALIDATE,
    str(phase_step.CLEANUP_VALIDATE_PRE_EDS),
]
