import copy
import pathlib
import tempfile
from time import strftime, localtime
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.sections.anonymous import AnonymousPhaseInstruction, ConfigurationBuilder
from shellcheck_lib_test.util import file_structure
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.configuration.test_resources import configuration_check as config_check


class Flow:
    def __init__(self,
                 parser: SingleInstructionParser,
                 home_dir_contents: file_structure.DirContents=file_structure.DirContents([]),
                 initial_configuration_builder: ConfigurationBuilder=ConfigurationBuilder(pathlib.Path('.')),
                 expected_main_result: sh_check.Assertion=sh_check.AnythingGoes(),
                 expected_configuration: config_check.Assertion=config_check.AnythingGoes(),
                 ):
        self.parser = parser
        self.home_dir_contents = home_dir_contents
        self.initial_configuration_builder = initial_configuration_builder
        self.expected_main_result = expected_main_result
        self.expected_configuration = expected_configuration


class TestCaseBase(unittest.TestCase):
    def _check(self,
               check: Flow,
               source: SingleInstructionParserSource):
        execute(self, check, source)


def execute(put: unittest.TestCase,
            setup: Flow,
            source: SingleInstructionParserSource):
    instruction = setup.parser.apply(source)
    put.assertIsNotNone(instruction,
                        'Result from parser cannot be None')
    put.assertIsInstance(instruction,
                         AnonymousPhaseInstruction,
                         'The instruction must be an instance of ' + str(AnonymousPhaseInstruction))
    assert isinstance(instruction, AnonymousPhaseInstruction)
    prefix = strftime("shellcheck-test-%Y-%m-%d-%H-%M-%S", localtime())
    with tempfile.TemporaryDirectory(prefix=prefix + "-home-") as home_dir_name:
        home_dir_path = pathlib.Path(home_dir_name)
        setup.home_dir_contents.write_to(home_dir_path)
        configuration_builder = setup.initial_configuration_builder
        configuration_builder.set_home_dir(home_dir_path)
        _execute_main(configuration_builder,
                      instruction, put, setup)


def _execute_main(configuration_builder: ConfigurationBuilder,
                  instruction: AnonymousPhaseInstruction,
                  put,
                  setup: Flow) -> sh.SuccessOrHardError:
    initial_configuration_builder = copy.deepcopy(configuration_builder)
    main_result = instruction.main(None, configuration_builder)
    put.assertIsNotNone(main_result,
                        'Result from main method cannot be None')
    setup.expected_main_result.apply(put, main_result)
    setup.expected_configuration.apply(put,
                                       initial_configuration_builder,
                                       configuration_builder)
    return main_result
