from shelltest.execution import phases
from shelltest.execution.phases import Phase


class PhaseStep(tuple):
    def __new__(cls,
                phase: Phase,
                step: str):
        return tuple.__new__(cls, (phase, step))

    @property
    def phase(self) -> Phase:
        return self[0]

    @property
    def step(self) -> str:
        return self[1]


def new_without_step(phase: Phase) -> PhaseStep:
    return PhaseStep(phase, None)


VALIDATE = 'validate'
PRE_VALIDATE = 'pre-validate'
POST_VALIDATE = 'post-validate'
EXECUTE = 'execute'


def __phase_step(phase: str, step: str) -> str:
    return phase + '/' + step


ANONYMOUS = '<INIT>'

SETUP = 'SETUP'

SETUP_pre_validate = 'pre-validate'
SETUP_execute = EXECUTE
SETUP_post_validate = 'post-validate'

SETUP__PRE_VALIDATE = __phase_step(SETUP, SETUP_pre_validate)
SETUP__EXECUTE = __phase_step(SETUP, SETUP_execute)
SETUP__POST_VALIDATE = __phase_step(SETUP, SETUP_post_validate)

ACT = 'ACT'

ACT_validate = VALIDATE
ACT_script_generation = 'script-generation'
ACT_script_execution = 'script-execution'

ACT__VALIDATE = __phase_step(ACT, ACT_validate)
ACT__SCRIPT_GENERATION = __phase_step(ACT, ACT_script_generation)
ACT__SCRIPT_EXECUTION = __phase_step(ACT, ACT_script_execution)

ASSERT = 'ASSERT'

ASSERT_validate = VALIDATE
ASSERT_execute = EXECUTE

ASSERT__VALIDATE = __phase_step(ASSERT, ASSERT_validate)
ASSERT__EXECUTE = __phase_step(ASSERT, ASSERT_execute)

CLEANUP = 'CLEANUP'

ANONYMOUS_EXECUTE = new_without_step(phases.ANONYMOUS)

SETUP_PRE_VALIDATE = PhaseStep(phases.SETUP, PRE_VALIDATE)
SETUP_EXECUTE = PhaseStep(phases.SETUP, EXECUTE)
SETUP_POST_VALIDATE = PhaseStep(phases.SETUP, POST_VALIDATE)

ACT_VALIDATE = PhaseStep(phases.ACT, VALIDATE)
ACT_SCRIPT_GENERATION = PhaseStep(phases.ACT, ACT_script_generation)
ACT_SCRIPT_EXECUTION = PhaseStep(phases.ACT, ACT_script_execution)

ASSERT_VALIDATE = PhaseStep(phases.ASSERT, VALIDATE)
ASSERT_EXECUTE = PhaseStep(phases.ASSERT, EXECUTE)

CLEANUP_EXECUTE = new_without_step(phases.CLEANUP)
