import os
import unittest
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv, FileMatcherModel
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTraceAndNegation, MatcherDdv
from exactly_lib.util.file_utils import preserved_cwd, TmpDirFileSpaceAsDirCreatedOnDemand
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.symbol.test_resources import sdv_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ActEnvironment
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.file_matcher.test_resources import ddv_assertions as asrt_file_matcher
from exactly_lib_test.test_case_utils.file_matcher.test_resources.model_construction import ModelConstructor
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def check(put: unittest.TestCase,
          parser: Parser[FileMatcherSdv],
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
                 parser: Parser[FileMatcherSdv],
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
        sdv = self._parse(source)

        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          sdv.references,
                                                          'symbol-usages after parse')

        with tcds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_hds_contents=self.arrangement.non_hds_contents,
                tcds_contents=self.arrangement.tcds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:

            self.arrangement.post_sds_population_action.apply(path_resolving_environment)
            tcds = path_resolving_environment.tcds

            environment = PathResolvingEnvironmentPreOrPostSds(
                tcds,
                self.arrangement.symbols)

            matcher_value = self._resolve_value(sdv, environment)

            with preserved_cwd():
                os.chdir(str(tcds.hds.case_dir))

                validate_result = self._execute_validate_pre_sds(environment, matcher_value)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  sdv.references,
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if validate_result is not None:
                    return

            validate_result = self._execute_validate_post_setup(environment, matcher_value)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              sdv.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return

            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(tcds))
            write_act_result(tcds.sds, act_result)

            matcher = self._resolve_primitive(matcher_value, environment)

            self._execute_main(tcds, matcher)

            self.expectation.main_side_effects_on_sds.apply(self.put, environment.sds)
            self.expectation.main_side_effects_on_tcds.apply(self.put, tcds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              sdv.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _parse(self, source: ParseSource) -> FileMatcherSdv:
        sdv = self.parser.parse(source)
        self.put.assertIsNotNone(sdv,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(sdv,
                                  FileMatcherSdv,
                                  'The SDV must be an instance of ' + str(FileMatcherSdv))
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(sdv, FileMatcherSdv)
        return sdv

    def _resolve_value(self,
                       sdv: FileMatcherSdv,
                       environment: PathResolvingEnvironmentPreOrPostSds) -> FileMatcherDdv:

        sdv_health_check = sdv_assertions.matches_sdv_of_file_matcher(
            resolved_value=asrt_file_matcher.matches_file_matcher_ddv(),
            references=asrt.is_sequence_of(asrt.is_instance(SymbolReference)),
            symbols=environment.symbols)

        sdv_health_check.apply_with_message(self.put, sdv,
                                            'SDV structure')

        matcher_ddv = sdv.resolve(environment.symbols)
        assert isinstance(matcher_ddv, MatcherDdv)

        return matcher_ddv

    @staticmethod
    def _resolve_primitive(ddv: FileMatcherDdv,
                           environment: PathResolvingEnvironmentPreOrPostSds) -> FileMatcher:

        matcher = ddv.value_of_any_dependency(environment.tcds)
        assert isinstance(matcher, MatcherWTraceAndNegation)

        return matcher

    def _execute_validate_pre_sds(self,
                                  environment: PathResolvingEnvironmentPreOrPostSds,
                                  ddv: FileMatcherDdv) -> Optional[TextRenderer]:
        result = ddv.validator.validate_pre_sds_if_applicable(environment.hds)
        self.expectation.validation_pre_sds.apply(self.put, result,
                                                  asrt.MessageBuilder('result of validate/pre sds'))
        return result

    def _execute_validate_post_setup(self,
                                     environment: PathResolvingEnvironmentPreOrPostSds,
                                     ddv: FileMatcherDdv) -> Optional[TextRenderer]:
        result = ddv.validator.validate_post_sds_if_applicable(environment.tcds)
        self.expectation.validation_post_sds.apply(self.put, result,
                                                   asrt.MessageBuilder('result of validate/post setup'))
        return result

    def _execute_main(self,
                      tcds: Tcds,
                      matcher: FileMatcher):
        model = self._new_model(tcds)
        try:
            main_result__trace = matcher.matches_w_trace(model)

            self._check_main_result(main_result__trace)
        except HardErrorException as ex:
            self._check_hard_error(ex)

    def _check_main_result(self, result: MatchingResult):
        if self.expectation.is_hard_error is not None:
            self.put.fail('HARD_ERROR not reported (raised)')

        self.expectation.main_result.apply_with_message(self.put,
                                                        result,
                                                        'main result')

    def _check_hard_error(self, result: HardErrorException):
        if self.expectation.is_hard_error is not None:
            assertion_on_text_renderer = asrt_text_doc.is_string_for_test(self.expectation.is_hard_error)
            assertion_on_text_renderer.apply_with_message(self.put,
                                                          result.error,
                                                          'error message for hard error')
            raise _CheckIsDoneException()
        else:
            self.put.fail('Unexpected HARD_ERROR')

    def _new_model(self, tcds: Tcds) -> FileMatcherModel:
        return FileMatcherModelForPrimitivePath(
            TmpDirFileSpaceAsDirCreatedOnDemand(tcds.sds.internal_tmp_dir),
            self.model_constructor(tcds)
        )
