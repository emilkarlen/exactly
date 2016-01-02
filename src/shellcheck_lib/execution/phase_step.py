from shellcheck_lib.execution import phases


class PhaseStep(tuple):
    def __new__(cls,
                phase: phases.Phase,
                step: str):
        return tuple.__new__(cls, (phase, step))

    @property
    def phase(self) -> phases.Phase:
        return self[0]

    @property
    def step(self) -> str:
        return self[1]

    def __str__(self):
        tail = '' if not self.step else '/' + self.step
        return self.phase.identifier + tail


def new_without_step(phase: phases.Phase) -> PhaseStep:
    return PhaseStep(phase, None)


VALIDATE = 'validate'
PRE_EDS_VALIDATE = 'pre-validate'
POST_VALIDATE = 'post-validate'
MAIN = 'main'


def __phase_step(phase: str, step: str) -> str:
    return phase + '/' + step


ANONYMOUS = '<INIT>'

SETUP = 'SETUP'

SETUP_pre_validate = 'pre-validate'
SETUP_main = MAIN
SETUP_post_validate = 'post-validate'

SETUP__PRE_VALIDATE = __phase_step(SETUP, SETUP_pre_validate)
SETUP__MAIN = __phase_step(SETUP, SETUP_main)
SETUP__POST_VALIDATE = __phase_step(SETUP, SETUP_post_validate)

ACT = 'ACT'

ACT_validate = VALIDATE
ACT_script_generate = 'script-generation'
ACT_script_validate = 'script-validation'
ACT_script_execute = 'script-execute'

ACT__VALIDATE = __phase_step(ACT, ACT_validate)
ACT__SCRIPT_GENERATE = __phase_step(ACT, ACT_script_generate)
ACT__SCRIPT_VALIDATE = __phase_step(ACT, ACT_script_validate)
ACT__SCRIPT_EXECUTE = __phase_step(ACT, ACT_script_execute)

ASSERT = 'ASSERT'

ASSERT_validate = VALIDATE
ASSERT_main = MAIN

ASSERT__VALIDATE = __phase_step(ASSERT, ASSERT_validate)
ASSERT__MAIN = __phase_step(ASSERT, ASSERT_main)

CLEANUP = 'CLEANUP'

ANONYMOUS_MAIN = new_without_step(phases.ANONYMOUS)

SETUP_PRE_VALIDATE = PhaseStep(phases.SETUP, PRE_EDS_VALIDATE)
SETUP_MAIN = PhaseStep(phases.SETUP, MAIN)
SETUP_POST_VALIDATE = PhaseStep(phases.SETUP, POST_VALIDATE)

ACT_VALIDATE = PhaseStep(phases.ACT, VALIDATE)
ACT_SCRIPT_GENERATION = PhaseStep(phases.ACT, ACT_script_generate)
ACT_SCRIPT_EXECUTION = PhaseStep(phases.ACT, ACT_script_execute)

ASSERT_VALIDATE = PhaseStep(phases.ASSERT, VALIDATE)
ASSERT_MAIN = PhaseStep(phases.ASSERT, MAIN)

CLEANUP_VALIDATE_PRE_EDS = PhaseStep(phases.CLEANUP, PRE_EDS_VALIDATE)
CLEANUP_MAIN = PhaseStep(phases.CLEANUP, MAIN)
