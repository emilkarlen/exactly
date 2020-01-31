import unittest
from typing import Sequence, Mapping

from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherSymbolContext
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args, file_matchers
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import model_checker
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import test_data
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg, \
    SymbolReference
from exactly_lib_test.test_case_utils.files_matcher.test_resources.helper import \
    IntegrationCheckHelper
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import ExecutionExpectation
from exactly_lib_test.test_resources.files.file_structure import empty_file, empty_dir, sym_link, Dir, FileSystemElement
from exactly_lib_test.test_resources.test_utils import NEA, NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRecursiveWithJustPrune),
    ])


NAME_PREFIX_THAT_MATCHES_BASE_NAME__M = 'M'
NAME_PREFIX_THAT_MATCHES_BASE_NAME__N = 'N'

NO_ACTION_ON_FILES_THEMSELVES__CONTENTS = [
    empty_file('M-f'),
    empty_dir('M-d'),
    sym_link('M-s', 'M-f'),
    sym_link('M-sb', 'non-existing'),
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
        empty_dir('M-match'),
        Dir('x-no-match',
            [
                empty_file('f1'),
                empty_dir('d1-no-match'),
            ]),
    ],
    actual=[
        Dir('M-match',
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
        empty_dir('M-match'),
        empty_dir('N-match'),
    ],
    actual=[
        Dir('M-match', [
            empty_file('f'),
        ]),
        Dir('N-match', [
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


class TestRecursiveWithJustPrune(unittest.TestCase):
    def test_single_prune(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        name_starts_with__m__matcher = FileMatcherSymbolContext.of_generic(
            'name_starts_with_m_matcher',
            sdv_components.matcher_sdv_from_constant_primitive(
                file_matchers.BaseNameStartsWithMatcher(NAME_PREFIX_THAT_MATCHES_BASE_NAME__M)
            )
        )

        # ACT & ASSERT #

        _check_multi(
            self,
            helper,
            arguments=
            fms_args.Prune(
                fm_args.SymbolReference(name_starts_with__m__matcher.name),
                helper.files_matcher_sym_ref_arg()
            ),
            symbols_common_to_all_cases={
                name_starts_with__m__matcher.name: name_starts_with__m__matcher.sdv
            },
            symbol_references=asrt.matches_sequence([
                name_starts_with__m__matcher.reference_assertion,
                helper.symbol_reference_assertion,
            ]
            ),
            execution_cases=SINGLE_PRUNE_CASES,
        )

    def test_multiple_prune_SHOULD_be_prune_dirs_matching_any_matcher(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        name_starts_with__m__matcher = FileMatcherSymbolContext.of_generic(
            'name_starts_with_M_matcher',
            sdv_components.matcher_sdv_from_constant_primitive(
                file_matchers.BaseNameStartsWithMatcher(NAME_PREFIX_THAT_MATCHES_BASE_NAME__M)
            )
        )

        name_starts_with__n__matcher = FileMatcherSymbolContext.of_generic(
            'name_starts_with_N_matcher',
            sdv_components.matcher_sdv_from_constant_primitive(
                file_matchers.BaseNameStartsWithMatcher(NAME_PREFIX_THAT_MATCHES_BASE_NAME__N)
            )
        )

        # ACT & ASSERT #

        _check_multi(
            self,
            helper,
            arguments=
            fms_args.Prune(
                fm_args.SymbolReference(name_starts_with__m__matcher.name),
                fms_args.Prune(
                    fm_args.SymbolReference(name_starts_with__n__matcher.name),
                    helper.files_matcher_sym_ref_arg(),
                ),
            ),
            symbols_common_to_all_cases={
                name_starts_with__m__matcher.name: name_starts_with__m__matcher.sdv,
                name_starts_with__n__matcher.name: name_starts_with__n__matcher.sdv,
            },
            symbol_references=asrt.matches_sequence([
                name_starts_with__m__matcher.reference_assertion,
                name_starts_with__n__matcher.reference_assertion,
                helper.symbol_reference_assertion,
            ]
            ),
            execution_cases=MULTIPLE_PRUNE_CASES,
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
