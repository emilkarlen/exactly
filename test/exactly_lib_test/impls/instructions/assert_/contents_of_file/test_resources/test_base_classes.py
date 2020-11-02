from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfiguration
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.relativity_options import \
    TestWithConfigurationAndRelativityOptionAndNegationBase
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct


class TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase(
    TestWithConfigurationAndRelativityOptionAndNegationBase):
    def __init__(self,
                 instruction_configuration: InstructionTestConfiguration,
                 option_configuration: RelativityOptionConfiguration,
                 expectation_type: ExpectationType):
        super().__init__(instruction_configuration, option_configuration, expectation_type)

    def _check_single_instruction_line_with_source_variants(self,
                                                            instruction_argument: str,
                                                            arrangement: ArrangementPostAct,
                                                            expectation: Expectation):
        self._check_with_source_variants(
            Arguments(instruction_argument),
            arrangement,
            expectation
        )
