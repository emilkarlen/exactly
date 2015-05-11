__VALIDATE = 'validate'
__EXECUTE = 'execute'


def __phase_step(phase: str, step: str) -> str:
    return phase + '/' + step


ANONYMOUS = '<INIT>'

SETUP = 'SETUP'

SETUP_validate = __VALIDATE
SETUP_execute = __EXECUTE

SETUP__VALIDATE = __phase_step(SETUP, SETUP_validate)
SETUP__EXECUTE = __phase_step(SETUP, SETUP_execute)

ACT = 'ACT'

ACT_validate = __VALIDATE
ACT_script_generation = 'script-generation'
ACT_script_execution = 'script-execution'

ACT__VALIDATE = __phase_step(ACT, ACT_validate)
ACT__SCRIPT_GENERATION = __phase_step(ACT, ACT_script_generation)
ACT__SCRIPT_EXECUTION = __phase_step(ACT, ACT_script_execution)

ASSERT = 'ASSERT'

ASSERT_validate = __VALIDATE
ASSERT_execute = __EXECUTE

ASSERT__VALIDATE = __phase_step(ASSERT, ASSERT_validate)
ASSERT__EXECUTE = __phase_step(ASSERT, ASSERT_execute)

CLEANUP = 'CLEANUP'
