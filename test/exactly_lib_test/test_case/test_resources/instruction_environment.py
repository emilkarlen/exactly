from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_hds, fake_sds


def fake_pre_sds_environment() -> InstructionEnvironmentForPreSdsStep:
    return InstructionEnvironmentForPreSdsStep(fake_hds(),
                                               {})


def fake_post_sds_environment() -> InstructionEnvironmentForPostSdsStep:
    return InstructionEnvironmentForPostSdsStep(fake_hds(),
                                                {},
                                                fake_sds(),
                                                'the-phase-identifier')
