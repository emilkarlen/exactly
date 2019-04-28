from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_hds, fake_sds, fake_home_and_sds


def fake_pre_sds_environment() -> InstructionEnvironmentForPreSdsStep:
    return InstructionEnvironmentForPreSdsStep(fake_hds(),
                                               {})


def fake_post_sds_environment() -> InstructionEnvironmentForPostSdsStep:
    return InstructionEnvironmentForPostSdsStep(fake_hds(),
                                                {},
                                                fake_sds(),
                                                'the-phase-identifier')


def fake_error_message_resolving_environment() -> ErrorMessageResolvingEnvironment:
    return ErrorMessageResolvingEnvironment(fake_home_and_sds(),
                                            None)
