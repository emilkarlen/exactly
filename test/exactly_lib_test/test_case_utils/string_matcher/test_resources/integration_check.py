import unittest

import os
from typing import Optional

from exactly_lib.execution import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherValue, FileToCheck
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ActEnvironment
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.string_matcher.test_resources.assertions import matches_string_matcher_resolver
from exactly_lib_test.test_case_utils.string_matcher.test_resources.model_construction import ModelBuilder, \
    ModelConstructor
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Expectation:
    def __init__(
            self,
            validation_post_sds: ValueAssertion[Optional[str]] = asrt.is_none,

            validation_pre_sds: ValueAssertion[Optional[str]] = asrt.is_none,

            main_result: ValueAssertion[Optional[ErrorMessageResolver]] = asrt.is_none,
            symbol_usages: ValueAssertion = asrt.is_empty_sequence,
            main_side_effects_on_sds: ValueAssertion[SandboxDirectoryStructure] = asrt.anything_goes(),
            main_side_effects_on_home_and_sds: ValueAssertion = asrt.anything_goes(),
            source: ValueAssertion = asrt.anything_goes(),
    ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_home_and_sds = main_side_effects_on_home_and_sds
        self.source = source
        self.symbol_usages = symbol_usages


def arbitrary_validation_failure() -> ValueAssertion[Optional[str]]:
    return asrt.is_instance(str)


def arbitrary_matching_failure() -> ValueAssertion[Optional[ErrorMessageResolver]]:
    return asrt.is_instance(ErrorMessageResolver)


def matching_matching_success() -> ValueAssertion[Optional[ErrorMessageResolver]]:
    return asrt.is_none


is_pass = Expectation


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
        resolver = self._parse(source)

        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          resolver.references,
                                                          'symbol-usages after parse')

        matches_string_matcher_resolver(
            references=asrt.anything_goes(),
            symbols=self.arrangement.symbols).apply_with_message(self.put, resolver,
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
                 environment: i.InstructionEnvironmentForPostSdsStep) -> StringMatcher:

        resolver_health_check = matches_string_matcher_resolver(references=asrt.anything_goes(),
                                                                symbols=environment.symbols,
                                                                tcds=environment.home_and_sds)
        resolver_health_check.apply_with_message(self.put, resolver,
                                                 'resolver structure')

        matcher_value = resolver.resolve(environment.symbols)
        assert isinstance(matcher_value, StringMatcherValue)

        matcher = matcher_value.value_of_any_dependency(environment.home_and_sds)
        assert isinstance(matcher, StringMatcher)

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
                      matcher: StringMatcher) -> Optional[ErrorMessageResolver]:
        main_result = matcher.matches(model)
        self.expectation.main_result.apply(self.put, main_result)
        return main_result

    def _new_model(self, sds: SandboxDirectoryStructure) -> FileToCheck:
        return ModelConstructor(self.model_builder, sds).construct()
