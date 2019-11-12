import os
import unittest
from typing import Optional

from exactly_lib.execution import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherDdv, FileToCheck
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ActEnvironment
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.string_matcher.test_resources.assertions import matches_string_matcher_resolver, \
    matches_string_matcher_attributes
from exactly_lib_test.test_case_utils.string_matcher.test_resources.model_construction import ModelBuilder, \
    ModelConstructor
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: Parser[StringMatcherResolver],
               source: ParseSource,
               model: ModelBuilder,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        check(self, parser, source, model, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: Parser[StringMatcherResolver],
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
                 parser: Parser[StringMatcherResolver],
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
        resolver = self._parse(source)

        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          resolver.references,
                                                          'symbol-usages after parse')

        matches_string_matcher_attributes(
            references=asrt.anything_goes()).apply_with_message(self.put, resolver,
                                                                'resolver structure')

        with home_and_sds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_home_contents=self.arrangement.non_home_contents,
                home_or_sds_contents=self.arrangement.home_or_sds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)
            home_and_sds = path_resolving_environment.home_and_sds

            with preserved_cwd():
                os.chdir(str(home_and_sds.hds.case_dir))

                environment = PathResolvingEnvironmentPreSds(home_and_sds.hds,
                                                             self.arrangement.symbols)
                validate_result = self._execute_validate_pre_sds(environment, resolver)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  resolver.references,
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if validate_result is not None:
                    return

            environment = PathResolvingEnvironmentPreOrPostSds(
                home_and_sds,
                self.arrangement.symbols)
            validate_result = self._execute_validate_post_setup(environment, resolver)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              resolver.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return
            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_sds))
            write_act_result(home_and_sds.sds, act_result)
            matcher = self._resolve(resolver, environment)
            model = self._new_model(environment.sds)
            self._execute_main(model, matcher)
            self.expectation.main_side_effects_on_sds.apply(self.put, environment.sds)
            self.expectation.main_side_effects_on_home_and_sds.apply(self.put, home_and_sds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              resolver.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _parse(self, source: ParseSource) -> StringMatcherResolver:
        resolver = self.parser.parse(source)
        self.put.assertIsNotNone(resolver,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(resolver,
                                  StringMatcherResolver,
                                  'The resolver must be an instance of ' + str(StringMatcherResolver))
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(resolver, StringMatcherResolver)
        return resolver

    def _resolve(self,
                 resolver: StringMatcherResolver,
                 environment: PathResolvingEnvironmentPreOrPostSds) -> StringMatcher:

        resolver_health_check = matches_string_matcher_resolver(references=asrt.anything_goes(),
                                                                symbols=environment.symbols,
                                                                tcds=environment.home_and_sds)
        resolver_health_check.apply_with_message(self.put, resolver,
                                                 'resolver structure')

        matcher_value = resolver.resolve(environment.symbols)
        assert isinstance(matcher_value, StringMatcherDdv)

        structure_tree_of_ddv = matcher_value.structure().render()

        asrt_d_tree.matches_node().apply_with_message(self.put,
                                                      structure_tree_of_ddv,
                                                      'structure of ddv')

        matcher = matcher_value.value_of_any_dependency(environment.home_and_sds)
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
                                  environment: PathResolvingEnvironmentPreSds,
                                  resolver: StringMatcherResolver) -> Optional[str]:
        result = resolver.validator.validate_pre_sds_if_applicable(environment)
        self.expectation.validation_pre_sds.apply(self.put, result,
                                                  asrt.MessageBuilder('result of validate/pre sds'))
        return result

    def _execute_validate_post_setup(self,
                                     environment: PathResolvingEnvironmentPostSds,
                                     resolver: StringMatcherResolver) -> Optional[str]:
        result = resolver.validator.validate_post_sds_if_applicable(environment)
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

    def _check_main_result(self,
                           result__trace: MatchingResult,
                           ):
        if self.expectation.is_hard_error is not None:
            self.put.fail('HARD_ERROR not reported (raised)')

        if self.expectation.main_result is None:
            self._assert_is_matching_result_for(True, result__trace)
        else:
            self._assert_is_matching_result_for(False, result__trace)

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

    def _assert_is_matching_result_for(self,
                                       expected_value: bool,
                                       actual: MatchingResult,
                                       ):
        asrt_matching_result.matches_value(expected_value).apply_with_message(self.put,
                                                                              actual,
                                                                              'matching result')
