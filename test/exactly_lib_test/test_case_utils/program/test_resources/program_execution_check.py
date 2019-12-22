import unittest
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case import executable_factories
from exactly_lib.test_case.executable_factory import ExecutableFactory
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.program.execution import store_result_in_instruction_tmp_dir as pgm_execution
from exactly_lib.test_case_utils.program.parse import parse_program as sut
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.program.program import Program, ProgramDdv
from exactly_lib.util import file_utils
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, with_no_timeout
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation, all_validations_passes
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction, tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertion, \
    ValueAssertionBase
from exactly_lib_test.type_system.trace.test_resources import trace_rendering_assertions as asrt_trace_rendering


class ResultWithTransformationData:
    def __init__(self,
                 process_result: SubProcessResult,
                 result_of_transformation: str):
        self.process_result = process_result
        self.result_of_transformation = result_of_transformation


def assert_process_result_data(exitcode: ValueAssertion[int] = asrt.anything_goes(),
                               stdout_contents: ValueAssertion[str] = asrt.anything_goes(),
                               stderr_contents: ValueAssertion[str] = asrt.anything_goes(),
                               contents_after_transformation: ValueAssertion[str] = asrt.anything_goes(),
                               ) -> ValueAssertion[ResultWithTransformationData]:
    return ResultWithTransformationDataAssertion(exitcode,
                                                 stdout_contents,
                                                 stderr_contents,
                                                 contents_after_transformation)


class ResultWithTransformationDataAssertion(ValueAssertionBase[ResultWithTransformationData]):
    def __init__(self,
                 exitcode: ValueAssertion[int] = asrt.anything_goes(),
                 stdout_contents: ValueAssertion[str] = asrt.anything_goes(),
                 stderr_contents: ValueAssertion[str] = asrt.anything_goes(),
                 contents_after_transformation: ValueAssertion[str] = asrt.anything_goes()
                 ):
        self.exitcode = exitcode
        self.stdout_contents = stdout_contents
        self.stderr_contents = stderr_contents
        self.contents_after_transformation = contents_after_transformation

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, ResultWithTransformationData,
                             message_builder.apply("result object class"))
        assert isinstance(value, ResultWithTransformationData)  # Type info for IDE
        pr = value.process_result
        self.exitcode.apply(put,
                            pr.exitcode,
                            message_builder.for_sub_component('exitcode'))
        self.stdout_contents.apply(put,
                                   pr.stdout,
                                   message_builder.for_sub_component('stdout'))
        self.stderr_contents.apply(put,
                                   pr.stderr,
                                   message_builder.for_sub_component('stderr'))
        self.contents_after_transformation.apply(put,
                                                 value.result_of_transformation,
                                                 message_builder.for_sub_component('contents_after_transformation'))


class Arrangement(ArrangementWithSds):
    def __init__(self,
                 output_file_to_transform: ProcOutputFile = ProcOutputFile.STDOUT,
                 pre_contents_population_action: TcdsAction = TcdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents_before_main: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 executable_factory: ExecutableFactory = executable_factories.get_factory_for_current_operating_system(),
                 symbols: SymbolTable = None,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         hds_contents=hds_contents,
                         sds_contents=sds_contents_before_main,
                         non_hds_contents=non_hds_contents_before_main,
                         tcds_contents=tcds_contents,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         symbols=symbols)
        self.output_file_to_transform = output_file_to_transform
        self.executable_factory = executable_factory


class Expectation:
    def __init__(self,
                 result: ValueAssertion[ResultWithTransformationData] = assert_process_result_data(),
                 validation: ValidationExpectation = all_validations_passes(),
                 symbol_references: ValueAssertion = asrt.is_empty_sequence,
                 main_side_effects_on_sds: ValueAssertion = asrt.anything_goes(),
                 main_side_effects_on_tcds: ValueAssertion = asrt.anything_goes(),
                 source: ValueAssertion = asrt.anything_goes(),
                 ):
        self.source = source
        self.symbol_references = symbol_references
        self.validation = validation
        self.result = result
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.main_side_effects_on_sds = main_side_effects_on_sds


def check(put: unittest.TestCase,
          source: ParseSource,
          arrangement: Arrangement,
          expectation: Expectation):
    Executor(put, arrangement, expectation).execute(sut.program_parser(), source)


def check_custom_parser(put: unittest.TestCase,
                        parser: Parser[ProgramSdv],
                        source: ParseSource,
                        arrangement: Arrangement,
                        expectation: Expectation):
    Executor(put, arrangement, expectation).execute(parser, source)


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 expectation: Expectation):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation

    def execute(self,
                parser: Parser[ProgramSdv],
                source: ParseSource):
        program_sdv = parser.parse(source)
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(program_sdv, ProgramSdv)
        self.expectation.symbol_references.apply_with_message(self.put,
                                                              program_sdv.references,
                                                              'symbol-usages after parse')
        with tcds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_hds_contents=self.arrangement.non_hds_contents,
                tcds_contents=self.arrangement.tcds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)

            application_environment = ApplicationEnvironment(
                TmpDirFileSpaceAsDirCreatedOnDemand(
                    path_resolving_environment.tcds.sds.internal_tmp_dir / 'tmp-file-space')
            )
            resolving_environment = FullResolvingEnvironment(self.arrangement.symbols,
                                                             path_resolving_environment.tcds,
                                                             application_environment)
            self.check(resolving_environment, program_sdv)

    def check(self,
              environment: FullResolvingEnvironment,
              program_sdv: ProgramSdv):

        program_ddv = program_sdv.resolve(environment.symbols)
        is_valid_node_renderer = asrt_trace_rendering.matches_node_renderer()
        structure_renderer = program_ddv.structure()
        is_valid_node_renderer.apply_with_message(self.put, structure_renderer,
                                                  'structure of ddv')

        result = self._execute_pre_validate(environment.tcds.hds,
                                            program_ddv)
        if result is not None:
            return

        result = self._execute_post_sds_validate(environment.tcds, program_ddv)
        if result is not None:
            return

        self._execute_program(environment, program_ddv)

    def _execute_pre_validate(self,
                              hds: HomeDirectoryStructure,
                              program: ProgramDdv) -> Optional[TextRenderer]:
        actual = program.validator.validate_pre_sds_if_applicable(hds)
        self.expectation.validation.pre_sds.apply_with_message(self.put, actual, 'validation-pre-sds')
        return actual

    def _execute_post_sds_validate(self,
                                   tcds: Tcds,
                                   program: ProgramDdv) -> Optional[TextRenderer]:
        actual = program.validator.validate_post_sds_if_applicable(tcds)
        self.expectation.validation.post_sds.apply_with_message(self.put, actual, 'validation-post-sds')
        return actual

    def _execute_program(self,
                         environment: FullResolvingEnvironment,
                         program_sdv: ProgramDdv):
        result = self._execute(environment, program_sdv)

        self.expectation.result.apply(self.put, result)
        self.expectation.main_side_effects_on_sds.apply(self.put, environment.tcds.sds)
        self.expectation.main_side_effects_on_tcds.apply(self.put, environment.tcds)

    def _execute(self, environment: FullResolvingEnvironment, program_ddv: ProgramDdv) -> ResultWithTransformationData:
        program_adv = program_ddv.value_of_any_dependency(environment.tcds)
        program = program_adv.applier(environment.application_environment)
        pgm_output_dir = environment.application_environment.tmp_files_space.new_path_as_existing_dir()
        assert isinstance(program, Program)
        execution_result = pgm_execution.make_transformed_file_from_output(pgm_output_dir,
                                                                           self.arrangement.process_execution_settings,
                                                                           self.arrangement.executable_factory,
                                                                           self.arrangement.output_file_to_transform,
                                                                           program)
        proc_exe_result = execution_result.process_result
        stderr_contents = file_utils.contents_of(proc_exe_result.path_of(ProcOutputFile.STDERR))
        stdout_contents = file_utils.contents_of(proc_exe_result.path_of(ProcOutputFile.STDOUT))
        result_of_transformation = file_utils.contents_of(execution_result.path_of_file_with_transformed_contents)
        proc_result_data = SubProcessResult(proc_exe_result.exit_code,
                                            stdout_contents,
                                            stderr_contents)
        return ResultWithTransformationData(proc_result_data,
                                            result_of_transformation)
