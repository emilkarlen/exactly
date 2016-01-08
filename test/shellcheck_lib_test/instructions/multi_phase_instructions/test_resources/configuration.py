import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionParser
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources.arrangement import ArrangementBase


class ConfigurationBase:
    def run_test(self,
                 put: unittest.TestCase,
                 source: SingleInstructionParserSource,
                 arrangement,
                 expectation):
        raise NotImplementedError()

    def arrangement(self, eds_contents_before_main: eds_populator.EdsPopulator):
        raise NotImplementedError()

    def empty_arrangement(self) -> ArrangementBase:
        return self.arrangement(eds_contents_before_main=eds_populator.empty())

    def parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def expect_success(self):
        raise NotImplementedError()

    def expect_failure_of_main(self):
        raise NotImplementedError()

    def expect_failing_validation_pre_eds(self):
        raise NotImplementedError()
