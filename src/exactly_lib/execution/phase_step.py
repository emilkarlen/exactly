from exactly_lib.test_case import phase_identifier

STEP__VALIDATE_SYMBOLS = '1:validate-symbols'
STEP__VALIDATE_PRE_SDS = '2:validate-pre-sds'
STEP__VALIDATE_POST_SETUP = '3:validate-post-setup'
STEP__MAIN = '9:main'
STEP__ACT__PARSE = '0:act-parse'
STEP__ACT__VALIDATE_EXE_INPUT = '4:act-validate-exe-input'
STEP__ACT__PREPARE = '5:act-prepare'
STEP__ACT__EXECUTE = '6:act-execute'


class SimplePhaseStep(tuple):
    def __new__(cls,
                phase: phase_identifier.PhaseEnum,
                step: str):
        return tuple.__new__(cls, (phase, step))

    @property
    def phase(self) -> phase_identifier.PhaseEnum:
        return self[0]

    @property
    def step(self) -> str:
        return self[1]

    def __str__(self):
        return self[0].name + '/' + self[1]

    def __repr__(self):
        return str(self)


class PhaseStep(tuple):
    def __new__(cls,
                phase: phase_identifier.Phase,
                step: str):
        return tuple.__new__(cls, (phase, step))

    @property
    def phase(self) -> phase_identifier.Phase:
        return self[0]

    @property
    def step(self) -> str:
        return self[1]

    @property
    def simple(self) -> SimplePhaseStep:
        return SimplePhaseStep(self.phase.the_enum, self.step)

    def __str__(self):
        tail = '' if not self.step else '/' + self.step
        return self.phase.identifier + tail


def _main_step(phase: phase_identifier.Phase) -> PhaseStep:
    return PhaseStep(phase, STEP__MAIN)


def _validate_symbols_step(phase: phase_identifier.Phase) -> PhaseStep:
    return PhaseStep(phase, STEP__VALIDATE_SYMBOLS)


def _validate_pre_sds_step(phase: phase_identifier.Phase) -> PhaseStep:
    return PhaseStep(phase, STEP__VALIDATE_PRE_SDS)


def _validate_post_setup_step(phase: phase_identifier.Phase) -> PhaseStep:
    return PhaseStep(phase, STEP__VALIDATE_POST_SETUP)


CONFIGURATION__MAIN = _main_step(phase_identifier.CONFIGURATION)

SETUP__VALIDATE_SYMBOLS = _validate_symbols_step(phase_identifier.SETUP)
SETUP__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.SETUP)
SETUP__VALIDATE_POST_SETUP = _validate_post_setup_step(phase_identifier.SETUP)
SETUP__MAIN = _main_step(phase_identifier.SETUP)

ACT__PARSE = PhaseStep(phase_identifier.ACT, STEP__ACT__PARSE)
ACT__VALIDATE_SYMBOLS = _validate_symbols_step(phase_identifier.ACT)
ACT__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.ACT)
ACT__VALIDATE_POST_SETUP = _validate_post_setup_step(phase_identifier.ACT)
ACT__VALIDATE_EXE_INPUT = PhaseStep(phase_identifier.ACT, STEP__ACT__VALIDATE_EXE_INPUT)
ACT__PREPARE = PhaseStep(phase_identifier.ACT, STEP__ACT__PREPARE)
ACT__EXECUTE = PhaseStep(phase_identifier.ACT, STEP__ACT__EXECUTE)

BEFORE_ASSERT__VALIDATE_SYMBOLS = _validate_symbols_step(phase_identifier.BEFORE_ASSERT)
BEFORE_ASSERT__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.BEFORE_ASSERT)
BEFORE_ASSERT__VALIDATE_POST_SETUP = _validate_post_setup_step(phase_identifier.BEFORE_ASSERT)
BEFORE_ASSERT__MAIN = _main_step(phase_identifier.BEFORE_ASSERT)

ASSERT__VALIDATE_SYMBOLS = _validate_symbols_step(phase_identifier.ASSERT)
ASSERT__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.ASSERT)
ASSERT__VALIDATE_POST_SETUP = _validate_post_setup_step(phase_identifier.ASSERT)
ASSERT__MAIN = _main_step(phase_identifier.ASSERT)

CLEANUP__VALIDATE_SYMBOLS = _validate_symbols_step(phase_identifier.CLEANUP)
CLEANUP__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.CLEANUP)
CLEANUP__MAIN = _main_step(phase_identifier.CLEANUP)
