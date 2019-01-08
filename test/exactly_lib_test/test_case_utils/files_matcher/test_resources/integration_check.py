import unittest

import os
from typing import Optional, Tuple

from exactly_lib.execution import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.files_matcher import FilesMatcherResolver, FilesMatcherValue, Environment, FilesMatcherModel, \
    HardErrorException
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case_utils.files_matcher.new_model_impl import FilesMatcherModelForDir
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ActEnvironment
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import Model
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: Parser[FilesMatcherResolver],
               source: ParseSource,
               model: Model,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        check(self, parser, source, model, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: Parser[FilesMatcherResolver],
          source: ParseSource,
          model: Model,
          arrangement: ArrangementPostAct,
          expectation: Expectation):
    Executor(put, parser, model, arrangement, expectation).execute(source)


class _CheckIsDoneException(Exception):
    pass


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 parser: Parser[FilesMatcherResolver],
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
        resolver = self._parse(source)

        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          resolver.references,
                                                          'symbol-usages after parse')

        # matches_string_matcher_resolver(
        #     references=asrt.anything_goes(),
        #     symbols=self.arrangement.symbols).apply_with_message(self.put, resolver,
        #                                                          'resolver structure')

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

                environment = i.InstructionEnvironmentForPreSdsStep(home_and_sds.hds,
                                                                    self.arrangement.process_execution_settings.environ,
                                                                    symbols=self.arrangement.symbols)
                validate_result = self._execute_validate_pre_sds(environment.path_resolving_environment, resolver)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  resolver.references,
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if validate_result is not None:
                    return

            environment = i.InstructionEnvironmentForPostSdsStep(
                environment.hds,
                environment.environ,
                home_and_sds.sds,
                phase_identifier.ASSERT.identifier,
                timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                symbols=self.arrangement.symbols)
            validate_result = self._execute_validate_post_setup(environment.path_resolving_environment, resolver)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              resolver.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return
            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_sds))
            write_act_result(home_and_sds.sds, act_result)
            matcher = self._resolve(resolver, environment)

            model_env, files_source = self._new_model(environment)

            self._execute_main(model_env, files_source, matcher)

            self.expectation.main_side_effects_on_sds.apply(self.put, environment.sds)
            self.expectation.main_side_effects_on_home_and_sds.apply(self.put, home_and_sds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              resolver.references,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _parse(self, source: ParseSource) -> FilesMatcherResolver:
        resolver = self.parser.parse(source)
        self.put.assertIsNotNone(resolver,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(resolver,
                                  FilesMatcherResolver,
                                  'The resolver must be an instance of ' + str(FilesMatcherResolver))
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(resolver, FilesMatcherResolver)
        return resolver

    def _resolve(self,
                 resolver: FilesMatcherResolver,
                 environment: i.InstructionEnvironmentForPostSdsStep) -> FilesMatcherValue:

        matcher_value = resolver.resolve(environment.symbols)
        assert isinstance(matcher_value, FilesMatcherValue)

        return matcher_value

    def _execute_validate_pre_sds(self,
                                  environment: PathResolvingEnvironmentPreSds,
                                  resolver: FilesMatcherResolver) -> Optional[str]:
        result = resolver.validator().validate_pre_sds_if_applicable(environment)
        self.expectation.validation_pre_sds.apply(self.put, result,
                                                  asrt.MessageBuilder('result of validate/pre sds'))
        return result

    def _execute_validate_post_setup(self,
                                     environment: PathResolvingEnvironmentPostSds,
                                     resolver: FilesMatcherResolver) -> Optional[str]:
        result = resolver.validator().validate_post_sds_if_applicable(environment)
        self.expectation.validation_post_sds.apply(self.put, result,
                                                   asrt.MessageBuilder('result of validate/post setup'))
        return result

    def _execute_main(self,
                      environment: Environment,
                      files_source: FilesMatcherModel,
                      matcher: FilesMatcherValue) -> Optional[ErrorMessageResolver]:
        try:
            main_result = matcher.matches(environment, files_source)

            if self.expectation.is_hard_error is not None:
                self.put.fail('HARD_ERROR not reported (raised)')

            self.expectation.main_result.apply(self.put, main_result)
            return main_result
        except HardErrorException as ex:
            if self.expectation.is_hard_error is not None:
                self.expectation.is_hard_error.apply_with_message(self.put, ex.error,
                                                                  'error message for hard error')
                raise _CheckIsDoneException()
            else:
                self.put.fail('Unexpected HARD_ERROR')

    def _new_model(self, instruction_environment: i.InstructionEnvironmentForPostSdsStep
                   ) -> Tuple[Environment, FilesMatcherModel]:
        return (
            Environment(
                instruction_environment.path_resolving_environment_pre_or_post_sds,
                instruction_environment.phase_logging.space_for_instruction()
            ),
            FilesMatcherModelForDir(
                self.model.dir_path_resolver,
                instruction_environment.path_resolving_environment_pre_or_post_sds,
                self.model.files_selection,
            ),
        )
