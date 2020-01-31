import unittest
from pathlib import Path
from typing import Sequence, Mapping

from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.matcher.impls import sdv_components, combinator_sdvs
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib_test.common.test_resources import text_doc_assertions
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherSymbolContext
from exactly_lib_test.test_case_utils.condition.integer.test_resources.arguments_building import int_condition
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args, file_matchers
from exactly_lib_test.test_case_utils.file_matcher.test_resources.file_matchers import FileMatcherTestImplBase
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import model_checker
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import test_data
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg, \
    SymbolReference
from exactly_lib_test.test_case_utils.files_matcher.test_resources.helper import \
    IntegrationCheckHelper
from exactly_lib_test.test_case_utils.matcher.test_resources import assertion_applier
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import ExecutionExpectation, Expectation, \
    ParseExpectation, Arrangement, EXECUTION_IS_PASS
from exactly_lib_test.test_resources.files.file_structure import empty_file, empty_dir, sym_link, Dir, FileSystemElement
from exactly_lib_test.test_resources.matcher_argument import Conjunction, Parenthesis
from exactly_lib_test.test_resources.test_utils import NEA, NExArr, NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources import matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRecursiveWithJustPrune),
        TestRecursiveWithPruneAndSelection(),
        TestRecursiveWithPruneAndDepthLimitations(),
        TestRecursiveWithPruneAndBinaryOperator(),
        TestPruneShouldBeIgnoredWhenModelIsNotRecursive(),
    ])


def _name_starts_with__and_hard_error_if_applied_to_non_directory(name: str,
                                                                  expected_name_prefix: str,
                                                                  ) -> FileMatcherSymbolContext:
    return FileMatcherSymbolContext.of_generic(
        name,
        combinator_sdvs.Conjunction([
            sdv_components.matcher_sdv_from_constant_primitive(
                file_matchers.BaseNameStartsWithMatcher(expected_name_prefix)
            ),
            sdv_components.matcher_sdv_from_constant_primitive(
                _HardErrorIfAppliedToNonDirectory()
            ),
        ]
        )
    )


class _HardErrorIfAppliedToNonDirectory(FileMatcherTestImplBase):
    def __init__(self):
        super().__init__()

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        if not isinstance(model, FileMatcherModel):
            raise HardErrorException(text_doc_assertions.new_single_string_text_for_test(
                'Model is not a {}: {}'.format(type(FileMatcherModel), model)
            ))

        if not model.file_type_access.is_type(FileType.DIRECTORY):
            raise HardErrorException(text_doc_assertions.new_single_string_text_for_test(
                'Test failure: File is not a directory'
            ))

        return matching_result.of(True)


NAME_STARTS_WITH__P1 = _name_starts_with__and_hard_error_if_applied_to_non_directory(
    'name_starts_with_P1',
    'P1'
)

NAME_STARTS_WITH__P2 = _name_starts_with__and_hard_error_if_applied_to_non_directory(
    'name_starts_with_P2',
    'P2',
)

NAME_STARTS_WITH__S1 = FileMatcherSymbolContext.of_generic(
    'name_starts_with_S1',
    sdv_components.matcher_sdv_from_constant_primitive(
        file_matchers.BaseNameStartsWithMatcher('S1')
    )
)

NO_ACTION_ON_FILES_THEMSELVES__CONTENTS = [
    empty_file('P1-f'),
    empty_dir('P1-d'),
    sym_link('P1-s', 'P1-f'),
    sym_link('P1-sb', 'no-P2-existing'),
]

FILES_SHOULD_BE_INCLUDED_EVEN_IF_MATCH__DEPTH_0 = NEA.new_identical_expected_and_actual(
    'files should be included even if match / depth 0',
    NO_ACTION_ON_FILES_THEMSELVES__CONTENTS,
)

FILES_SHOULD_BE_INCLUDED_EVEN_IF_MATCH__DEPTH_1 = NEA.new_identical_expected_and_actual(
    'files should be included even if match / depth 1',
    [
        Dir('x',
            NO_ACTION_ON_FILES_THEMSELVES__CONTENTS
            )
    ],
)

EXCLUDE_CONTENTS_OF_MATCHING_DIR__DEPTH_0 = NEA(
    'exclude contents of dir iff matches/depth 0',
    expected=[
        empty_dir('P1-match'),
        Dir('x-no-match',
            [
                empty_file('f1'),
                empty_dir('d1-no-match'),
            ]),
    ],
    actual=[
        Dir('P1-match',
            [
                empty_file('f1'),
                empty_dir('d1-no-match'),
            ]),
        Dir('x-no-match',
            [
                empty_file('f1'),
                empty_dir('d1-no-match'),
            ]),
    ],
)

EXCLUDE_CONTENTS_OF_MATCHING_DIR__DEPTH_1 = NEA(
    'exclude contents of dir iff matches',
    expected=[
        Dir('d-no-match',
            EXCLUDE_CONTENTS_OF_MATCHING_DIR__DEPTH_0.expected
            ),
    ],
    actual=[
        Dir('d-no-match',
            EXCLUDE_CONTENTS_OF_MATCHING_DIR__DEPTH_0.actual
            ),
    ],
)

SINGLE_PRUNE_CASES = [
    FILES_SHOULD_BE_INCLUDED_EVEN_IF_MATCH__DEPTH_0,
    FILES_SHOULD_BE_INCLUDED_EVEN_IF_MATCH__DEPTH_1,
    EXCLUDE_CONTENTS_OF_MATCHING_DIR__DEPTH_0,
    EXCLUDE_CONTENTS_OF_MATCHING_DIR__DEPTH_1,
]

COMBINATION_SHOULD_PRUNE_DIRS_MATCHED_BY_ANY_MATCHER__DEPTH_0 = NEA(
    'combination should prune dirs matched by any matcher',
    expected=[
        empty_dir('P1-match'),
        empty_dir('P2-match'),
    ],
    actual=[
        Dir('P1-match', [
            empty_file('f'),
        ]),
        Dir('P2-match', [
            empty_file('g'),
        ]),
    ],
)

COMBINATION_SHOULD_PRUNE_DIRS_MATCHED_BY_ANY_MATCHER__DEPTH_1 = NEA(
    'exclude contents of dir iff matches',
    expected=[
        Dir('d-no-match',
            COMBINATION_SHOULD_PRUNE_DIRS_MATCHED_BY_ANY_MATCHER__DEPTH_0.expected
            ),
    ],
    actual=[
        Dir('d-no-match',
            COMBINATION_SHOULD_PRUNE_DIRS_MATCHED_BY_ANY_MATCHER__DEPTH_0.actual
            ),
    ],
)

MULTIPLE_PRUNE_CASES = [
    FILES_SHOULD_BE_INCLUDED_EVEN_IF_MATCH__DEPTH_0,
    FILES_SHOULD_BE_INCLUDED_EVEN_IF_MATCH__DEPTH_1,
    COMBINATION_SHOULD_PRUNE_DIRS_MATCHED_BY_ANY_MATCHER__DEPTH_0,
    COMBINATION_SHOULD_PRUNE_DIRS_MATCHED_BY_ANY_MATCHER__DEPTH_1,
]

COMBINATION_OF_PRUNE_AND_SELECTION = NEA(
    'combination of prune and selection',
    actual=[
        Dir('P1-match',
            [
                empty_file('S1-match'),
                empty_file('no-S1-match'),
            ]),
        Dir('no-P1-match',
            [
                empty_file('S1-match'),
                empty_file('no-S1-match'),
            ]),
    ],
    expected=[
        Path('no-P1-match') / 'S1-match',
    ],
)

COMBINATION_OF_PRUNE_AND_DEPTH_LIMITATIONS__DEPTH_MUST_BE_1 = NEA(
    'combination of prune and depth limitations / depth must be 1',
    actual=[
        Dir('P1-match',
            [
                empty_file('DEPTH-match'),
            ]),
        Dir('no-P1-match',
            [
                empty_file('DEPTH-match'),
                Dir('no-P1-match--DEPTH-match',
                    [
                        empty_file('no-DEPTH-match'),
                    ]
                    ),
            ]),
    ],
    expected=[
        Path('no-P1-match') / 'DEPTH-match',
        Path('no-P1-match') / 'no-P1-match--DEPTH-match',
    ],
)

COMBINATION_OF_PRUNE_AND_DEPTH_LIMITATIONS__DEPTH_MUST_BE_2 = NEA(
    'combination of prune and depth limitations / depth must be 2',
    actual=[
        Dir('no-P1-match--depth-0',
            COMBINATION_OF_PRUNE_AND_DEPTH_LIMITATIONS__DEPTH_MUST_BE_1.actual
            ),
    ],
    expected=[
        Path('no-P1-match--depth-0') / p
        for p in COMBINATION_OF_PRUNE_AND_DEPTH_LIMITATIONS__DEPTH_MUST_BE_1.expected
    ],
)

COMBINATION_OF_PRUNE_AND_DEPTH_LIMITATIONS = [
    (1, COMBINATION_OF_PRUNE_AND_DEPTH_LIMITATIONS__DEPTH_MUST_BE_1),
    (2, COMBINATION_OF_PRUNE_AND_DEPTH_LIMITATIONS__DEPTH_MUST_BE_2),
]

NON_RECURSIVE__ACTUAL = [
    Dir('non-empty-dir',
        [
            empty_file('file-in-dir'),
        ]),
    empty_dir('empty-dir'),
    empty_file('regular file'),
    sym_link('sym-link', 'regular file'),
    sym_link('broken-sym-link', 'non-existing'),
]


class TestRecursiveWithJustPrune(unittest.TestCase):
    def test_single_prune(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        # ACT & ASSERT #

        _check_multi(
            self,
            helper,
            arguments=
            fms_args.Prune(
                fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
                helper.files_matcher_sym_ref_arg()
            ),
            symbols_common_to_all_cases={
                NAME_STARTS_WITH__P1.name: NAME_STARTS_WITH__P1.sdv
            },
            symbol_references=asrt.matches_sequence([
                NAME_STARTS_WITH__P1.reference_assertion,
                helper.symbol_reference_assertion,
            ]
            ),
            execution_cases=SINGLE_PRUNE_CASES,
        )

    def test_multiple_prune_SHOULD_be_prune_dirs_matching_any_matcher(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        # ACT & ASSERT #

        _check_multi(
            self,
            helper,
            arguments=
            fms_args.Prune(
                fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
                fms_args.Prune(
                    fm_args.SymbolReference(NAME_STARTS_WITH__P2.name),
                    helper.files_matcher_sym_ref_arg(),
                ),
            ),
            symbols_common_to_all_cases={
                NAME_STARTS_WITH__P1.name: NAME_STARTS_WITH__P1.sdv,
                NAME_STARTS_WITH__P2.name: NAME_STARTS_WITH__P2.sdv,
            },
            symbol_references=asrt.matches_sequence([
                NAME_STARTS_WITH__P1.reference_assertion,
                NAME_STARTS_WITH__P2.reference_assertion,
                helper.symbol_reference_assertion,
            ]
            ),
            execution_cases=MULTIPLE_PRUNE_CASES,
        )


class TestRecursiveWithPruneAndSelection(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        argument_cases = [
            NIE(
                'prune followed by selection',
                input_value=fms_args.Prune(
                    fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
                    fms_args.Selection(
                        fm_args.SymbolReference(NAME_STARTS_WITH__S1.name),
                        helper.files_matcher_sym_ref_arg(),
                    ),
                ),
                expected_value=asrt.matches_sequence([
                    NAME_STARTS_WITH__P1.reference_assertion,
                    NAME_STARTS_WITH__S1.reference_assertion,
                    helper.symbol_reference_assertion,
                ]),
            ),
            NIE(
                'selection followed by prune',
                input_value=fms_args.Selection(
                    fm_args.SymbolReference(NAME_STARTS_WITH__S1.name),
                    fms_args.Prune(
                        fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
                        helper.files_matcher_sym_ref_arg(),
                    ),
                ),
                expected_value=asrt.matches_sequence([
                    NAME_STARTS_WITH__S1.reference_assertion,
                    NAME_STARTS_WITH__P1.reference_assertion,
                    helper.symbol_reference_assertion,
                ]),
            ),
        ]

        contents_case = COMBINATION_OF_PRUNE_AND_SELECTION

        # ACT & ASSERT #

        for argument_case in argument_cases:
            with self.subTest(argument_case.name):
                integration_check.CHECKER.check__w_source_variants(
                    self,
                    arguments=
                    argument_case.input_value.as_arguments,
                    model_constructor=
                    helper.model_constructor_for_checked_dir__recursive(),
                    arrangement=
                    helper.arrangement_for_contents_of_model(
                        checked_dir_contents=contents_case.actual,
                        files_matcher_symbol_value=
                        model_checker.matcher(
                            self,
                            helper.dir_arg.path_sdv,
                            contents_case.expected,
                        ),
                        additional_symbols={
                            NAME_STARTS_WITH__P1.name: NAME_STARTS_WITH__P1.sdv,
                            NAME_STARTS_WITH__S1.name: NAME_STARTS_WITH__S1.sdv,
                        },
                    ),
                    expectation=Expectation(
                        ParseExpectation(
                            symbol_references=argument_case.expected_value,
                        )
                    ),
                )


class TestRecursiveWithPruneAndDepthLimitations(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        arguments = fms_args.Prune(
            fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
            helper.files_matcher_sym_ref_arg(),
        ).as_arguments

        # ACT & ASSERT #

        for depth, nie in COMBINATION_OF_PRUNE_AND_DEPTH_LIMITATIONS:
            with self.subTest(data=nie.name,
                              depth=depth):
                integration_check.CHECKER.check__w_source_variants(
                    self,
                    arguments=
                    arguments,
                    model_constructor=
                    helper.model_constructor_for_checked_dir__recursive(min_depth=depth,
                                                                        max_depth=depth),
                    arrangement=
                    helper.arrangement_for_contents_of_model(
                        checked_dir_contents=nie.actual,
                        files_matcher_symbol_value=
                        model_checker.matcher(
                            self,
                            helper.dir_arg.path_sdv,
                            nie.expected,
                        ),
                        additional_symbols={
                            NAME_STARTS_WITH__P1.name: NAME_STARTS_WITH__P1.sdv,
                        },
                    ),
                    expectation=Expectation(
                        ParseExpectation(
                            symbol_references=asrt.matches_sequence([
                                NAME_STARTS_WITH__P1.reference_assertion,
                                helper.symbol_reference_assertion,
                            ]),
                        )
                    ),
                )


class TestRecursiveWithPruneAndBinaryOperator(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        helper = IntegrationCheckHelper()

        actual_contents = [
            Dir('P1-matches',
                [
                    empty_file('file-in-pruned-dir'),
                ])
        ]

        arguments = Conjunction([
            Parenthesis(
                fms_args.Prune(
                    fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
                    fms_args.NumFiles(int_condition(comparators.EQ, 1))
                )),
            fms_args.NumFiles(int_condition(comparators.EQ, 2)),
        ])

        # ACT & ASSERT #

        integration_check.CHECKER.check__w_source_variants(
            self,
            arguments=
            arguments.as_arguments,
            model_constructor=
            helper.model_constructor_for_checked_dir__recursive(),
            arrangement=
            Arrangement(
                symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                    NAME_STARTS_WITH__P1.name: NAME_STARTS_WITH__P1.sdv,
                }),
                tcds=helper.dir_arg.tcds_arrangement_dir_with_contents(actual_contents)
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        NAME_STARTS_WITH__P1.reference_assertion,
                    ])
                ),
                EXECUTION_IS_PASS,
            )
        )


class TestPruneShouldBeIgnoredWhenModelIsNotRecursive(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        helper = IntegrationCheckHelper()

        test_fails_if_applied__matcher = test_fails_if_applied(self)

        arguments = fms_args.Prune(
            fm_args.SymbolReference(test_fails_if_applied__matcher.name),
            helper.files_matcher_sym_ref_arg(),
        )

        # ACT & ASSERT #

        integration_check.CHECKER.check(
            self,
            source=
            arguments.as_remaining_source,
            model_constructor=
            helper.model_constructor_for_checked_dir__non_recursive(),
            arrangement=
            helper.arrangement_for_contents_of_model(
                checked_dir_contents=NON_RECURSIVE__ACTUAL,
                files_matcher_symbol_value=
                model_checker.matcher(
                    self,
                    helper.dir_arg.path_sdv,
                    test_data.strip_file_type_info(
                        test_data.expected_is_actual_down_to_max_depth(0, NON_RECURSIVE__ACTUAL).expected
                    ),
                ),
                additional_symbols={
                    test_fails_if_applied__matcher.name: test_fails_if_applied__matcher.sdv,
                },
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        test_fails_if_applied__matcher.reference_assertion,
                        helper.symbol_reference_assertion,
                    ])
                ),
                EXECUTION_IS_PASS,
            )
        )


def _check_multi(
        put: unittest.TestCase,
        helper: IntegrationCheckHelper,
        arguments: FilesMatcherArg,
        symbols_common_to_all_cases: Mapping[str, SymbolDependentValue],
        symbol_references: ValueAssertion[Sequence[SymbolReference]],
        execution_cases: Sequence[NEA[Sequence[FileSystemElement], Sequence[FileSystemElement]]]):
    integration_check.CHECKER.check_multi__w_source_variants(
        put,
        arguments=arguments.as_arguments,
        symbol_references=symbol_references,
        model_constructor=
        helper.model_constructor_for_checked_dir__recursive(),
        execution=[
            NExArr(
                case.name,
                ExecutionExpectation(),
                helper.arrangement_for_contents_of_model(
                    checked_dir_contents=case.actual,
                    files_matcher_symbol_value=
                    model_checker.matcher(
                        put,
                        helper.dir_arg.path_sdv,
                        test_data.strip_file_type_info(
                            test_data.flatten_directories(case.expected)
                        ),
                    ),
                    additional_symbols=symbols_common_to_all_cases,
                ),
            )
            for case in execution_cases
        ],
    )


def test_fails_if_applied(put: unittest.TestCase) -> FileMatcherSymbolContext:
    return FileMatcherSymbolContext.of_generic(
        'test_fails_if_applied',
        sdv_components.matcher_sdv_from_constant_primitive(
            assertion_applier.MatcherThatAppliesValueAssertion(
                put,
                asrt.fail('must not be applied'),
                lambda x: x,
                asrt.MessageBuilder.new_empty(),
                True,
            )
        )
    )
