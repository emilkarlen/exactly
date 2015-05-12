from shelltest.phases import Phase


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
EXECUTE = 'execute'


def __phase_step(phase: str, step: str) -> str:
    return phase + '/' + step


ANONYMOUS = '<INIT>'

SETUP = 'SETUP'

SETUP_validate = VALIDATE
SETUP_execute = EXECUTE

SETUP__VALIDATE = __phase_step(SETUP, SETUP_validate)
SETUP__EXECUTE = __phase_step(SETUP, SETUP_execute)

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
