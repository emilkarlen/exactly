import os
import unittest
from typing import Optional, Tuple

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_utils.files_matcher.new_model_impl import FilesMatcherModelForDir
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher, FilesMatcherDdv
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.file_utils import preserved_cwd, TmpDirFileSpaceAsDirCreatedOnDemand, TmpDirFileSpace
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ActEnvironment
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import Model
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: Parser[FilesMatcherSdv],
               source: ParseSource,
               model: Model,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        check(self, parser, source, model, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: Parser[FilesMatcherSdv],
          source: ParseSource,
          model: Model,
          arrangement: ArrangementPostAct,
          expectation: Expectation):
    _Executor(put, parser, model, arrangement, expectation).execute(source)


class _CheckIsDoneException(Exception):
    pass


class _Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 parser: Parser[FilesMatcherSdv],
                 model: Model,
                 arrangement: ArrangementPostAct,
                 expectation: Expectation):
        self.model = model
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

            with preserved_cwd():
                os.chdir(str(tcds.hds.case_dir))

                environment = PathResolvingEnvironmentPreSds(tcds.hds,
                                                             self.arrangement.symbols)
                validate_result = self._execute_validate_pre_sds(environment, sdv)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  sdv.references,
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if validate_result is not None:
                    return

            environment = PathResolvingEnvironmentPreOrPostSds(
                tcds,
                self.arrangement.symbols)
            validate_result = self._execute_validate_post_setup(environment, sdv)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              sdv.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return
            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(tcds))
            write_act_result(tcds.sds, act_result)
            dir_file_space, files_source = self._new_model(environment)

            matcher_value = self._resolve(sdv, environment)
            matcher = matcher_value.value_of_any_dependency(tcds).construct(dir_file_space)

            self._execute_main(files_source, matcher)

            self.expectation.main_side_effects_on_sds.apply(self.put, environment.sds)
            self.expectation.main_side_effects_on_tcds.apply(self.put, tcds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              sdv.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _parse(self, source: ParseSource) -> FilesMatcherSdv:
        sdv = self.parser.parse(source)
        self.put.assertIsNotNone(sdv,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(sdv,
                                  FilesMatcherSdv,
                                  'The SDV must be an instance of ' + str(FilesMatcherSdv))
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(sdv, FilesMatcherSdv)
        return sdv

    def _resolve(self,
                 sdv: FilesMatcherSdv,
                 environment: PathResolvingEnvironmentPreOrPostSds) -> FilesMatcherDdv:

        matcher_ddv = sdv.resolve(environment.symbols)
        assert isinstance(matcher_ddv, FilesMatcherDdv)

        return matcher_ddv

    def _execute_validate_pre_sds(self,
                                  environment: PathResolvingEnvironmentPreSds,
                                  sdv: FilesMatcherSdv) -> Optional[TextRenderer]:
        result = sdv.validator().validate_pre_sds_if_applicable(environment)
        self.expectation.validation_pre_sds.apply_with_message(self.put, result,
                                                               'result of validate/pre sds')
        return result

    def _execute_validate_post_setup(self,
                                     environment: PathResolvingEnvironmentPostSds,
                                     sdv: FilesMatcherSdv) -> Optional[TextRenderer]:
        result = sdv.validator().validate_post_sds_if_applicable(environment)
        self.expectation.validation_post_sds.apply_with_message(self.put, result,
                                                                'result of validate/post setup')
        return result

    def _execute_main(self,
                      files_source: FilesMatcherModel,
                      matcher: FilesMatcher):
        try:
            main_result__emr = matcher.matches_emr(files_source)
            main_result__trace = matcher.matches_w_trace(files_source)

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
            assertion_on_text_renderer.apply_with_message(self.put, result.error,
                                                          'error message for hard error')
            raise _CheckIsDoneException()
        else:
            self.put.fail('Unexpected HARD_ERROR')

    def _new_model(self, environment: PathResolvingEnvironmentPreOrPostSds
                   ) -> Tuple[TmpDirFileSpace, FilesMatcherModel]:
        tmp_file_space = TmpDirFileSpaceAsDirCreatedOnDemand(environment.sds.log_dir)
        return (
            tmp_file_space,
            FilesMatcherModelForDir(
                tmp_file_space,
                self.model.dir_path_sdv.resolve(environment.symbols)
                    .value_of_any_dependency__d(environment.tcds),
                self.model.files_selection,
            ),
        )

    def _assert_is_matching_result_for(self,
                                       expected_value: bool,
                                       actual: MatchingResult,
                                       ):
        asrt_matching_result.matches_value(expected_value).apply_with_message(self.put,
                                                                              actual,
                                                                              'matching result')
