from exactly_lib.execution import phase_step

CONFIGURATION__MAIN = phase_step.CONFIGURATION__MAIN.simple

SETUP__VALIDATE_SYMBOLS = phase_step.SETUP__VALIDATE_SYMBOLS.simple
SETUP__VALIDATE_PRE_SDS = phase_step.SETUP__VALIDATE_PRE_SDS.simple
SETUP__VALIDATE_POST_SETUP = phase_step.SETUP__VALIDATE_POST_SETUP.simple
SETUP__MAIN = phase_step.SETUP__MAIN.simple

ALL_SETUP_WITH_ENV_ARG = (SETUP__VALIDATE_PRE_SDS,
                          SETUP__VALIDATE_POST_SETUP,
                          SETUP__MAIN)

ACT__PARSE = phase_step.ACT__PARSE.simple
ACT__VALIDATE_SYMBOLS = phase_step.ACT__VALIDATE_SYMBOLS.simple
ACT__VALIDATE_PRE_SDS = phase_step.ACT__VALIDATE_PRE_SDS.simple
ACT__VALIDATE_POST_SETUP = phase_step.ACT__VALIDATE_POST_SETUP.simple
ACT__PREPARE = phase_step.ACT__PREPARE.simple
ACT__EXECUTE = phase_step.ACT__EXECUTE.simple

ALL_ACT_AFTER_PARSE = (ACT__VALIDATE_PRE_SDS,
                       ACT__VALIDATE_POST_SETUP,
                       ACT__PREPARE,
                       ACT__EXECUTE)
ALL_ACT_WITH_ENV_ARG = (ACT__PARSE,) + ALL_ACT_AFTER_PARSE

BEFORE_ASSERT__VALIDATE_SYMBOLS = phase_step.BEFORE_ASSERT__VALIDATE_SYMBOLS.simple
BEFORE_ASSERT__VALIDATE_PRE_SDS = phase_step.BEFORE_ASSERT__VALIDATE_PRE_SDS.simple
BEFORE_ASSERT__VALIDATE_POST_SETUP = phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP.simple
BEFORE_ASSERT__MAIN = phase_step.BEFORE_ASSERT__MAIN.simple

ALL_BEFORE_ASSERT_WITH_ENV_ARG = (BEFORE_ASSERT__VALIDATE_PRE_SDS,
                                  BEFORE_ASSERT__VALIDATE_POST_SETUP,
                                  BEFORE_ASSERT__MAIN)

ASSERT__VALIDATE_SYMBOLS = phase_step.ASSERT__VALIDATE_SYMBOLS.simple
ASSERT__VALIDATE_PRE_SDS = phase_step.ASSERT__VALIDATE_PRE_SDS.simple
ASSERT__VALIDATE_POST_SETUP = phase_step.ASSERT__VALIDATE_POST_SETUP.simple
ASSERT__MAIN = phase_step.ASSERT__MAIN.simple

ALL_ASSERT_WITH_ENV_ARG = (ASSERT__VALIDATE_PRE_SDS,
                           ASSERT__VALIDATE_POST_SETUP,
                           ASSERT__MAIN)

CLEANUP__VALIDATE_SYMBOLS = phase_step.CLEANUP__VALIDATE_SYMBOLS.simple
CLEANUP__VALIDATE_PRE_SDS = phase_step.CLEANUP__VALIDATE_PRE_SDS.simple
CLEANUP__MAIN = phase_step.CLEANUP__MAIN.simple

ALL_CLEANUP_WITH_ENV_ARG = (CLEANUP__VALIDATE_PRE_SDS,
                            CLEANUP__MAIN)