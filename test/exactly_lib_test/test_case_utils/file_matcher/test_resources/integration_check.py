import os
import unittest
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherValue, FileMatcherModel
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.file_utils import preserved_cwd, TmpDirFileSpaceAsDirCreatedOnDemand
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.symbol.test_resources import resolver_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ActEnvironment
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.file_matcher.test_resources import value_assertions as asrt_file_matcher
from exactly_lib_test.test_case_utils.file_matcher.test_resources.model_construction import ModelConstructor
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def check(put: unittest.TestCase,
          parser: Parser[FileMatcherResolver],
          source: ParseSource,
          model: ModelConstructor,
          arrangement: ArrangementPostAct,
          expectation: Expectation):
    Executor(put, parser, model, arrangement, expectation).execute(source)


class _CheckIsDoneException(Exception):
    pass


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 parser: Parser[FileMatcherResolver],
                 model_constructor: ModelConstructor,
                 arrangement: ArrangementPostAct,
                 expectation: Expectation):
        self.model_constructor = model_constructor
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

        with home_and_sds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_home_contents=self.arrangement.non_home_contents,
                home_or_sds_contents=self.arrangement.home_or_sds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:

            self.arrangement.post_sds_population_action.apply(path_resolving_environment)
            tcds = path_resolving_environment.home_and_sds

            environment = PathResolvingEnvironmentPreOrPostSds(
                tcds,
                self.arrangement.symbols)

            matcher_value = self._resolve_value(resolver, environment)

            with preserved_cwd():
                os.chdir(str(tcds.hds.case_dir))

                validate_result = self._execute_validate_pre_sds(environment, matcher_value)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  resolver.references,
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if validate_result is not None:
                    return

            validate_result = self._execute_validate_post_setup(environment, matcher_value)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              resolver.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return

            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(tcds))
            write_act_result(tcds.sds, act_result)

            matcher = self._resolve_primitive(matcher_value, environment)

            self._execute_main(tcds, matcher)

            self.expectation.main_side_effects_on_sds.apply(self.put, environment.sds)
            self.expectation.main_side_effects_on_home_and_sds.apply(self.put, tcds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              resolver.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _parse(self, source: ParseSource) -> FileMatcherResolver:
        resolver = self.parser.parse(source)
        self.put.assertIsNotNone(resolver,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(resolver,
                                  FileMatcherResolver,
                                  'The resolver must be an instance of ' + str(FileMatcherResolver))
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(resolver, FileMatcherResolver)
        return resolver

    def _resolve_value(self,
                       resolver: FileMatcherResolver,
                       environment: PathResolvingEnvironmentPreOrPostSds) -> FileMatcherValue:

        resolver_health_check = resolver_assertions.matches_resolver_of_file_matcher(
            resolved_value=asrt_file_matcher.matches_file_matcher_value(),
            references=asrt.is_sequence_of(asrt.is_instance(SymbolReference)),
            symbols=environment.symbols)

        resolver_health_check.apply_with_message(self.put, resolver,
                                                 'resolver structure')

        matcher_value = resolver.resolve(environment.symbols)
        assert isinstance(matcher_value, FileMatcherValue)

        return matcher_value

    @staticmethod
    def _resolve_primitive(matcher_value: FileMatcherValue,
                           environment: PathResolvingEnvironmentPreOrPostSds) -> FileMatcher:

        matcher = matcher_value.value_of_any_dependency(environment.home_and_sds)
        assert isinstance(matcher, FileMatcher)

        return matcher

    def _execute_validate_pre_sds(self,
                                  environment: PathResolvingEnvironmentPreOrPostSds,
                                  value: FileMatcherValue) -> Optional[TextRenderer]:
        result = value.validator().validate_pre_sds_if_applicable(environment.hds)
        self.expectation.validation_pre_sds.apply(self.put, result,
                                                  asrt.MessageBuilder('result of validate/pre sds'))
        return result

    def _execute_validate_post_setup(self,
                                     environment: PathResolvingEnvironmentPreOrPostSds,
                                     value: FileMatcherValue) -> Optional[TextRenderer]:
        result = value.validator().validate_post_sds_if_applicable(environment.home_and_sds)
        self.expectation.validation_post_sds.apply(self.put, result,
                                                   asrt.MessageBuilder('result of validate/post setup'))
        return result

    def _execute_main(self,
                      tcds: HomeAndSds,
                      matcher: FileMatcher):
        model = self._new_model(tcds)
        try:
            main_result__emr = matcher.matches_emr(model)
            main_result__trace = matcher.matches_w_trace(model)

            self._check_main_result(main_result__emr, main_result__trace)
        except HardErrorException as ex:
            self._check_hard_error(ex)

    def _check_main_result(self,
                           result: Optional[ErrorMessageResolver],
                           result__trace: MatchingResult,
                           ):
        if self.expectation.is_hard_error is not None:
            self.put.fail('HARD_ERROR not reported (raised)')

        if self.expectation.main_result is None:
            self.put.assertIsNone(result,
                                  'result from main')
            self._assert_is_matching_result_for(True, result__trace)
        else:
            self.put.assertIsNotNone(result,
                                     'result from main')
            self._assert_is_matching_result_for(False, result__trace)
            err_msg = result.resolve()
            self.expectation.main_result.apply_with_message(self.put, err_msg,
                                                            'error result of main')

    def _check_hard_error(self, result: HardErrorException):
        if self.expectation.is_hard_error is not None:
            assertion_on_text_renderer = asrt_text_doc.is_string_for_test(self.expectation.is_hard_error)
            assertion_on_text_renderer.apply_with_message(self.put,
                                                          result.error,
                                                          'error message for hard error')
            raise _CheckIsDoneException()
        else:
            self.put.fail('Unexpected HARD_ERROR')

    def _new_model(self, tcds: HomeAndSds) -> FileMatcherModel:
        return FileMatcherModelForPrimitivePath(
            TmpDirFileSpaceAsDirCreatedOnDemand(tcds.sds.internal_tmp_dir),
            self.model_constructor(tcds)
        )

    def _assert_is_matching_result_for(self,
                                       expected_value: bool,
                                       actual: MatchingResult,
                                       ):
        asrt_matching_result.matches_value(expected_value).apply_with_message(self.put,
                                                                              actual,
                                                                              'matching result')
