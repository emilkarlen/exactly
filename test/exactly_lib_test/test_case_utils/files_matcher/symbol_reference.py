import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib.test_case_utils.files_matcher.impl.emptiness import emptiness_matcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher, \
    FilesMatcherResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolsArrAndExpectSetup
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fm_args, model
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources import tr
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArgumentsSetup
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success, pass_or_fail_from_bool
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_validator import ValidatorThat
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_sds
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        unittest.makeSuite(TestReferencedMatcherShouldBeValidated),

        unittest.makeSuite(TestSymbolReferences),

        unittest.makeSuite(TestResultShouldBeEqualToResultOfReferencedMatcher),
        unittest.makeSuite(TestDifferentSourceVariants),
    ])


SYMBOL_NAME = 'FILES_MATCHER_SYMBOL'
EXPECTED_REFERENCE = is_reference_to_files_matcher(SYMBOL_NAME)


class TestWithAssertionVariantForSymbolReference(tr.TestWithAssertionVariantBase):
    @property
    def assertion_variant(self) -> FilesMatcherArgumentsSetup:
        return FilesMatcherArgumentsSetup(
            fm_args.SymbolReferenceAssertionVariant(SYMBOL_NAME),
            symbols_in_arrangement={
                SYMBOL_NAME: emptiness_matcher(ExpectationType.POSITIVE)
            },
            expected_references=[EXPECTED_REFERENCE]
        )


class TestParseInvalidSyntax(tr.TestParseInvalidSyntaxWithMissingSelectorArgCaseBase,
                             TestWithAssertionVariantForSymbolReference):
    pass


class TestSymbolReferences(tr.TestCommonSymbolReferencesBase,
                           TestWithAssertionVariantForSymbolReference):
    pass


class TestReferencedMatcherShouldBeValidated(tr.TestCaseBaseForParser):
    def runTest(self):
        err_msg_from_validator = 'error from validator pre sds'
        name_of_referenced_symbol = 'FILES_MATCHER_SYMBOL'

        expected_symbol_usages = asrt.matches_sequence(
            [is_reference_to_files_matcher(name_of_referenced_symbol)])

        arguments_constructor = fm_args.argument_constructor_for_symbol_reference(name_of_referenced_symbol)
        arguments = arguments_constructor.apply(expectation_type_config__non_is_success(ExpectationType.POSITIVE))

        cases = [
            NEA('pre sds validation',
                expected=
                Expectation(
                    validation_pre_sds=asrt_validation.matches_validation_failure(asrt.equals(err_msg_from_validator)),
                    symbol_usages=expected_symbol_usages,
                ),
                actual=
                ValidatorThat(
                    pre_sds_return_value=asrt_text_doc.new_single_string_text_for_test(err_msg_from_validator)
                )
                ),
            NEA('post sds validation',
                expected=
                Expectation(
                    validation_post_sds=asrt_validation.matches_validation_failure(asrt.equals(err_msg_from_validator)),
                    symbol_usages=expected_symbol_usages,
                ),
                actual=
                ValidatorThat(
                    post_setup_return_value=asrt_text_doc.new_single_string_text_for_test(err_msg_from_validator)
                )
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                instruction_source = remaining_source(arguments)
                integration_check.check(
                    self,
                    sut.files_matcher_parser(),
                    instruction_source,
                    model.arbitrary_model(),
                    ArrangementPostAct(
                        symbols=SymbolTable({
                            name_of_referenced_symbol:
                                container(FilesMatcherResolverConstantTestImpl(
                                    resolved_value=True,
                                    validator=case.actual,
                                ))
                        }),
                    ),
                    expectation=case.expected)


class TestResultShouldBeEqualToResultOfReferencedMatcher(tr.TestCaseBaseForParser):
    def runTest(self):
        # ARRANGE #
        name_of_referenced_symbol = 'FILES_MATCHER_SYMBOL'
        existing_dir = empty_dir('existing-dir')

        arbitrary_valid_rel_opt_conf = conf_rel_sds(RelSdsOptionType.REL_ACT)

        sds_populator = arbitrary_valid_rel_opt_conf.populator_for_relativity_option_root__sds(
            DirContents([existing_dir]))

        expected_symbol_usages = asrt.matches_sequence([
            is_reference_to_files_matcher(name_of_referenced_symbol)
        ])

        arguments_constructor = fm_args.argument_constructor_for_symbol_reference(name_of_referenced_symbol)

        for result_of_referenced_matcher in [False, True]:
            referenced_matcher = FilesMatcherResolverConstantTestImpl(
                resolved_value=result_of_referenced_matcher
            )
            symbols = SymbolTable({name_of_referenced_symbol: container(referenced_matcher)})

            for expectation_type in ExpectationType:
                etc = expectation_type_config__non_is_success(expectation_type)

                arguments = arguments_constructor.apply(etc)
                instruction_source = remaining_source(arguments)

                arrangement = ArrangementPostAct(
                    sds_contents=sds_populator,
                    symbols=symbols,
                )
                expectation = Expectation(
                    main_result=etc.main_result(pass_or_fail_from_bool(result_of_referenced_matcher)),
                    symbol_usages=expected_symbol_usages,
                )

                with self.subTest(result_of_referenced_matcher=result_of_referenced_matcher,
                                  expectation_type=expectation_type):
                    # ACT & ASSERT #
                    integration_check.check(
                        self,
                        sut.files_matcher_parser(),
                        instruction_source,
                        model.arbitrary_model(),
                        arrangement,
                        expectation)


class TestDifferentSourceVariants(tr.TestCaseBaseForParser):
    def runTest(self):
        # ACT #
        existing_dir = empty_dir('name-of-existing-dir')
        contents_of_relativity_option_root = DirContents([existing_dir])

        result_of_referenced_matcher = True

        referenced_symbol = NameAndValue(
            'REFERENCED_FILES_MATCHER',
            FilesMatcherResolverConstantTestImpl(
                resolved_value=result_of_referenced_matcher
            ))

        following_symbols_setup = SymbolsArrAndExpectSetup(
            symbols_in_arrangement={
                referenced_symbol.name: referenced_symbol.value,
            },
            expected_references=[
                is_reference_to_files_matcher(referenced_symbol.name)
            ],
        )

        instruction_argument_constructor = fm_args.argument_constructor_for_symbol_reference(referenced_symbol.name)

        # ACT & ASSERT #
        self.checker.check_parsing_with_different_source_variants(
            instruction_argument_constructor,
            model.arbitrary_model_constructor(),
            default_relativity=RelOptionType.REL_CWD,
            non_default_relativity=RelOptionType.REL_TMP,
            main_result_for_positive_expectation=pass_or_fail_from_bool(result_of_referenced_matcher),
            contents_of_relativity_option_root=contents_of_relativity_option_root,
            following_symbols_setup=following_symbols_setup,
        )


AN_ACCEPTED_SDS_REL_OPT_CONFIG = rel_opt_conf.conf_rel_sds(RelSdsOptionType.REL_TMP)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
