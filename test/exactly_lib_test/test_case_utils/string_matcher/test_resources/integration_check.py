import os
import unittest
from typing import Optional

from exactly_lib.execution import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherDdv, FileToCheck
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ActEnvironment
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.string_matcher.test_resources.assertions import matches_string_matcher_attributes
from exactly_lib_test.test_case_utils.string_matcher.test_resources.model_construction import ModelBuilder, \
    ModelConstructor
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: Parser[StringMatcherSdv],
               source: ParseSource,
               model: ModelBuilder,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        check(self, parser, source, model, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: Parser[StringMatcherSdv],
          source: ParseSource,
          model: ModelBuilder,
          arrangement: ArrangementPostAct,
          expectation: Expectation):
    Executor(put, parser, model, arrangement, expectation).execute(source)


class _CheckIsDoneException(Exception):
    pass


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 parser: Parser[StringMatcherSdv],
                 model: ModelBuilder,
                 arrangement: ArrangementPostAct,
                 expectation: Expectation):
        self.model_builder = model
        self.put = put
        self.parser = parser
        self.arrangement = arrangement
        self.expectation = expectation

    def execute(self, source: ParseSource):
        try:
            self._execute(source)
        except _CheckIsDoneException:
            pass

    def _execute(self, source: ParseSource):
        sdv = self._parse(source)

        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          sdv.references,
                                                          'symbol-usages after parse')

        matches_string_matcher_attributes(
            references=asrt.anything_goes()).apply_with_message(self.put, sdv,
                                                                'SDV implementation structure')

        matcher_ddv = sdv.resolve(self.arrangement.symbols)

        assert isinstance(matcher_ddv, StringMatcherDdv)

        with tcds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_hds_contents=self.arrangement.non_hds_contents,
                tcds_contents=self.arrangement.tcds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)
            tcds = path_resolving_environment.tcds

            with preserved_cwd():
                os.chdir(str(tcds.hds.case_dir))

                validate_result = self._execute_validate_pre_sds(tcds.hds, matcher_ddv)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  sdv.references,
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if validate_result is not None:
                    return

            validate_result = self._execute_validate_post_setup(tcds, matcher_ddv)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              sdv.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return
            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(tcds))
            write_act_result(tcds.sds, act_result)
            matcher = self._get_value(matcher_ddv, tcds)
            model = self._new_model(tcds.sds)
            self._execute_main(model, matcher)
            self.expectation.main_side_effects_on_sds.apply(self.put, tcds.sds)
            self.expectation.main_side_effects_on_tcds.apply(self.put, tcds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              sdv.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _parse(self, source: ParseSource) -> StringMatcherSdv:
        sdv = self.parser.parse(source)
        self.put.assertIsNotNone(sdv,
                                 'Result from parser cannot be None')

        self.expectation.source.apply_with_message(self.put, source, 'source')

        sdv_health_check = matches_string_matcher_attributes(asrt.anything_goes())

        sdv_health_check.apply_with_message(self.put, sdv,
                                            'SDV structure')

        return sdv

    def _get_value(self,
                   matcher_ddv: StringMatcherDdv,
                   tcds: Tcds) -> StringMatcher:

        structure_tree_of_ddv = matcher_ddv.structure().render()

        asrt_d_tree.matches_node().apply_with_message(self.put,
                                                      structure_tree_of_ddv,
                                                      'structure of DDV')

        matcher = matcher_ddv.value_of_any_dependency(tcds)
        assert isinstance(matcher, StringMatcher)

        structure_tree_of_primitive = matcher.structure().render()

        asrt_d_tree.matches_node().apply_with_message(self.put,
                                                      structure_tree_of_primitive,
                                                      'structure of primitive')

        structure_equals_ddv = asrt_d_tree.header_data_and_children_equal_as(structure_tree_of_ddv)
        structure_equals_ddv.apply_with_message(
            self.put,
            structure_tree_of_primitive,
            'structure of primitive should be same as that of ddv')

        return matcher

    def _execute_validate_pre_sds(self,
                                  hds: HomeDirectoryStructure,
                                  ddv: StringMatcherDdv) -> Optional[str]:
        result = ddv.validator.validate_pre_sds_if_applicable(hds)
        self.expectation.validation_pre_sds.apply(self.put, result,
                                                  asrt.MessageBuilder('result of validate/pre sds'))
        return result

    def _execute_validate_post_setup(self,
                                     tcds: Tcds,
                                     ddv: StringMatcherDdv) -> Optional[str]:
        result = ddv.validator.validate_post_sds_if_applicable(tcds)
        self.expectation.validation_post_sds.apply(self.put, result,
                                                   asrt.MessageBuilder('result of validate/post setup'))
        return result

    def _execute_main(self,
                      model: FileToCheck,
                      matcher: StringMatcher):
        try:
            main_result__trace = matcher.matches_w_trace(model)

            self._check_main_result(main_result__trace)
        except HardErrorException as ex:
            self._check_hard_error(ex)

    def _check_main_result(self, result: MatchingResult):
        if self.expectation.is_hard_error is not None:
            self.put.fail('HARD_ERROR not reported (raised)')

        self.expectation.main_result.apply_with_message(self.put, result, 'matching result')

    def _check_hard_error(self, result: HardErrorException):
        if self.expectation.is_hard_error is not None:
            assertion_on_text_renderer = asrt_text_doc.is_string_for_test(self.expectation.is_hard_error)
            assertion_on_text_renderer.apply_with_message(self.put, result.error,
                                                          'error message for hard error')
            raise _CheckIsDoneException()
        else:
            self.put.fail('Unexpected HARD_ERROR')

    def _new_model(self, sds: SandboxDirectoryStructure) -> FileToCheck:
        return ModelConstructor(self.model_builder, sds).construct()
