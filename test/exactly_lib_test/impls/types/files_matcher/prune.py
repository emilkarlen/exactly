import pathlib
import unittest
from pathlib import Path
from typing import Sequence

from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.matcher.impls import combinator_matchers
from exactly_lib.impls.types.matcher.impls import sdv_components, combinator_sdvs
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.common.test_resources import text_doc_assertions
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args, file_matchers
from exactly_lib_test.impls.types.file_matcher.test_resources.file_matchers import FileMatcherTestImplBase
from exactly_lib_test.impls.types.files_matcher.models.test_resources import model_checker
from exactly_lib_test.impls.types.files_matcher.models.test_resources import test_data
from exactly_lib_test.impls.types.files_matcher.test_resources import arguments_building as fsm_args
from exactly_lib_test.impls.types.files_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.files_matcher.test_resources import model as models
from exactly_lib_test.impls.types.files_matcher.test_resources.arguments_building import FilesMatcherArg, \
    SymbolReference
from exactly_lib_test.impls.types.files_matcher.test_resources.integration_check_helper import \
    IntegrationCheckHelper
from exactly_lib_test.impls.types.files_matcher.test_resources.parsers import TOP_LEVEL_PARSER_CASES
from exactly_lib_test.impls.types.integer.test_resources.arguments_building import int_condition
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    PrimAndExeExpectation, Expectation, arrangement_w_tcds, ExecutionExpectation
from exactly_lib_test.impls.types.matcher.test_resources import matcher_w_init_action
from exactly_lib_test.impls.types.matcher.test_resources.integration_check import EXECUTION_IS_PASS
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_confs, matcher_assertions
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources import matcher_argument
from exactly_lib_test.test_resources.files.file_structure import sym_link, Dir, \
    FileSystemElement, File, DirContents
from exactly_lib_test.test_resources.matcher_argument import conjunction, Parentheses
from exactly_lib_test.test_resources.test_utils import NEA, NExArr, NIE, EA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.symbol_context import FileMatcherSymbolContext, \
    FileMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources import files_matchers as files_matcher_test_impl
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext
from exactly_lib_test.type_val_prims.matcher.test_resources import matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRecursiveWithJustPrune),
        TestRecursiveWithPruneAndSelection(),
        TestRecursiveWithPruneAndDepthLimitations(),
        TestRecursiveWithPruneAndBinaryOperator(),
        TestPruneShouldBeIgnoredWhenModelIsNotRecursive(),
        TestDetectionOfSymLink(),
        TestBrokenSymLinksShouldBeTreatedAsNonDirFiles(),
        TestFileMatcherShouldBeParsedAsSimpleExpression(),
        TestFilesMatcherShouldBeParsedAsSimpleExpression(),
    ])


def _name_starts_with__and_hard_error_if_applied_to_non_directory(name: str,
                                                                  expected_name_prefix: str,
                                                                  ) -> FileMatcherSymbolContext:
    return FileMatcherSymbolContext.of_sdv(
        name,
        combinator_sdvs.Conjunction([
            sdv_components.matcher_sdv_from_constant_primitive(
                file_matchers.BaseNameStartsWithMatcher(expected_name_prefix)
            ),
            sdv_components.matcher_sdv_from_constant_primitive(
                _HardErrorIfAppliedToNonDirectory()
            ),
        ],
            combinator_matchers.no_op_freezer,
        )
    )


class TestFileMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        file_matcher_argument = fm_args.conjunction(
            [
                fm_args.SymbolReferenceWReferenceSyntax('FILE_MATCHER_SYMBOL_1'),
                fm_args.SymbolReferenceWReferenceSyntax('FILE_MATCHER_SYMBOL_2'),
            ],
        )
        files_matcher_argument = fsm_args.Empty()

        arguments = fsm_args.Prune(
            file_matcher_argument,
            files_matcher_argument
        )
        for top_level_parser_case in TOP_LEVEL_PARSER_CASES:
            with self.subTest(top_level_parser_case.name):
                # ACT & ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    top_level_parser_case.value.parse(arguments.as_remaining_source)


class TestFilesMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_contents = DirContents([
            Dir('a-dir', [
                File.empty('a-file-in-pruned-dir')
            ]),
        ])

        file_matcher = FileMatcherSymbolContextOfPrimitiveConstant(
            'FILE_MATCHER_SYMBOL',
            True,
        )
        files_matcher__parsed = FilesMatcherSymbolContext.of_primitive(
            'FILES_MATCHER_1',
            files_matcher_test_impl.FilesMatcherNumFilesTestImpl(1)
        )
        symbols = [file_matcher, files_matcher__parsed]

        files_matcher_bin_op_expr = fsm_args.conjunction([
            fm_args.SymbolReferenceWReferenceSyntax(files_matcher__parsed.name),
            fsm_args.Custom('after bin op'),
        ])

        arguments = fsm_args.Prune(
            fm_args.SymbolReferenceWReferenceSyntax(file_matcher.name),
            files_matcher_bin_op_expr,
        )
        model_rel_opt_conf = rel_opt_confs.conf_rel_any(RelOptionType.REL_ACT)
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            arguments.as_remaining_source,
            models.model_constructor__recursive(model_rel_opt_conf.path_sdv_for_root_dir()),
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
                tcds_contents=model_rel_opt_conf.populator_for_relativity_option_root(model_contents)
            ),
            Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_line(
                        current_line_number=1,
                        remaining_part_of_current_line=' '.join([
                            files_matcher_bin_op_expr.operator,
                            files_matcher_bin_op_expr.operands[1].as_str,
                        ])
                    ),
                    symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                ),
                ExecutionExpectation(
                    main_result=matcher_assertions.is_matching_success(),
                ),
            ),
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

NAME_STARTS_WITH__S1 = FileMatcherSymbolContext.of_sdv(
    'name_starts_with_S1',
    sdv_components.matcher_sdv_from_constant_primitive(
        file_matchers.BaseNameStartsWithMatcher('S1')
    )
)

NO_ACTION_ON_FILES_THEMSELVES__CONTENTS = [
    File.empty('P1-f'),
    Dir.empty('P1-d'),
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
        Dir.empty('P1-match'),
        Dir('x-no-match',
            [
                File.empty('f1'),
                Dir.empty('d1-no-match'),
            ]),
    ],
    actual=[
        Dir('P1-match',
            [
                File.empty('f1'),
                Dir.empty('d1-no-match'),
            ]),
        Dir('x-no-match',
            [
                File.empty('f1'),
                Dir.empty('d1-no-match'),
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
        Dir.empty('P1-match'),
        Dir.empty('P2-match'),
    ],
    actual=[
        Dir('P1-match', [
            File.empty('f'),
        ]),
        Dir('P2-match', [
            File.empty('g'),
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
                File.empty('S1-match'),
                File.empty('no-S1-match'),
            ]),
        Dir('no-P1-match',
            [
                File.empty('S1-match'),
                File.empty('no-S1-match'),
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
                File.empty('DEPTH-match'),
            ]),
        Dir('no-P1-match',
            [
                File.empty('DEPTH-match'),
                Dir('no-P1-match--DEPTH-match',
                    [
                        File.empty('no-DEPTH-match'),
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
            File.empty('file-in-dir'),
        ]),
    Dir.empty('empty-dir'),
    File.empty('regular file'),
    sym_link('sym-link', 'regular file'),
    sym_link('broken-sym-link', 'non-existing'),
]

PRUNE_TYPE_SYM_LINK = EA(
    [
        pathlib.Path('non-empty-dir'),
        pathlib.Path('non-empty-dir') / 'regular-in-non-empty-dir',
        pathlib.Path('sym-link-to-non-empty-dir'),
    ],
    [
        Dir('non-empty-dir', [
            File.empty('regular-in-non-empty-dir'),
        ]),
        sym_link('sym-link-to-non-empty-dir', 'non-empty-dir')
    ]
)

BROKEN_SYM_LINKS_SHOULD_BE_TREATED_AS_NON_DIR_FILES = EA(
    [
        pathlib.Path('non-empty-dir'),
        pathlib.Path('non-empty-dir') / 'regular-in-non-empty-dir',
        pathlib.Path('broken-sym-link'),
    ],
    [
        Dir('non-empty-dir', [
            File.empty('regular-in-non-empty-dir'),
        ]),
        sym_link('broken-sym-link', 'non-existing-target')
    ]
)


class TestRecursiveWithJustPrune(unittest.TestCase):
    def test_single_prune(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        # ACT & ASSERT #

        _check_multi(
            self,
            helper,
            arguments=
            fsm_args.Prune(
                fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
                helper.files_matcher_sym_ref_arg()
            ),
            symbols_common_to_all_cases=[
                NAME_STARTS_WITH__P1
            ],
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
            fsm_args.Prune(
                fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
                fsm_args.Prune(
                    fm_args.SymbolReference(NAME_STARTS_WITH__P2.name),
                    helper.files_matcher_sym_ref_arg(),
                ),
            ),
            symbols_common_to_all_cases=[
                NAME_STARTS_WITH__P1,
                NAME_STARTS_WITH__P2,
            ],
            symbol_references=asrt.matches_sequence([
                NAME_STARTS_WITH__P1.reference_assertion,
                NAME_STARTS_WITH__P2.reference_assertion,
                helper.symbol_reference_assertion,
            ]
            ),
            execution_cases=MULTIPLE_PRUNE_CASES,
        )


class TestDetectionOfSymLink(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check(
            self,
            source=fsm_args.Prune(
                fm_args.Type(FileType.SYMLINK),
                helper.files_matcher_sym_ref_arg(),
            ).as_remaining_source,
            input_=
            helper.model_constructor_for_checked_dir__recursive(),
            arrangement=helper.arrangement_for_contents_of_model(
                checked_dir_contents=PRUNE_TYPE_SYM_LINK.actual,
                files_matcher_symbol_value=
                model_checker.matcher(
                    self,
                    helper.dir_arg.path_sdv,
                    PRUNE_TYPE_SYM_LINK.expected,
                ),
            ),
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=helper.symbol_references_expectation(),
                ),
                EXECUTION_IS_PASS,
            ),
        )


class TestBrokenSymLinksShouldBeTreatedAsNonDirFiles(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check(
            self,
            source=fsm_args.Prune(
                matcher_argument.Constant(False),
                helper.files_matcher_sym_ref_arg(),
            ).as_remaining_source,
            input_=
            helper.model_constructor_for_checked_dir__recursive(),
            arrangement=helper.arrangement_for_contents_of_model(
                checked_dir_contents=BROKEN_SYM_LINKS_SHOULD_BE_TREATED_AS_NON_DIR_FILES.actual,
                files_matcher_symbol_value=
                model_checker.matcher(
                    self,
                    helper.dir_arg.path_sdv,
                    BROKEN_SYM_LINKS_SHOULD_BE_TREATED_AS_NON_DIR_FILES.expected,
                ),
            ),
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=helper.symbol_references_expectation(),
                ),
                EXECUTION_IS_PASS,
            ),
        )


class TestRecursiveWithPruneAndSelection(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        helper = IntegrationCheckHelper()

        argument_cases = [
            NIE(
                'prune followed by selection',
                input_value=fsm_args.Prune(
                    fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
                    fsm_args.Selection(
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
                input_value=fsm_args.Selection(
                    fm_args.SymbolReference(NAME_STARTS_WITH__S1.name),
                    fsm_args.Prune(
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
                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    arguments=
                    argument_case.input_value.as_arguments,
                    input_=
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
                        additional_symbols=[
                            NAME_STARTS_WITH__P1,
                            NAME_STARTS_WITH__S1,
                        ],
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

        arguments = fsm_args.Prune(
            fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
            helper.files_matcher_sym_ref_arg(),
        ).as_arguments

        # ACT & ASSERT #

        for depth, nie in COMBINATION_OF_PRUNE_AND_DEPTH_LIMITATIONS:
            with self.subTest(data=nie.name,
                              depth=depth):
                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    arguments=
                    arguments,
                    input_=
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
                        additional_symbols=[
                            NAME_STARTS_WITH__P1
                        ],
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
                    File.empty('file-in-pruned-dir'),
                ])
        ]

        arguments = conjunction([
            Parentheses(
                fsm_args.Prune(
                    fm_args.SymbolReference(NAME_STARTS_WITH__P1.name),
                    fsm_args.NumFiles(int_condition(comparators.EQ, 1))
                )),
            fsm_args.NumFiles(int_condition(comparators.EQ, 2)),
        ])

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            arguments=
            arguments.as_arguments,
            input_=
            helper.model_constructor_for_checked_dir__recursive(),
            arrangement=
            Arrangement(
                symbols=NAME_STARTS_WITH__P1.symbol_table,
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

        test_fails_if_applied__matcher_symbol_context = test_fails_if_applied(self)

        arguments = fsm_args.Prune(
            fm_args.SymbolReference(test_fails_if_applied__matcher_symbol_context.name),
            helper.files_matcher_sym_ref_arg(),
        )

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check(
            self,
            source=
            arguments.as_remaining_source,
            input_=
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
                additional_symbols=[
                    test_fails_if_applied__matcher_symbol_context
                ],
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        test_fails_if_applied__matcher_symbol_context.reference_assertion,
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
        symbols_common_to_all_cases: Sequence[SymbolContext],
        symbol_references: Assertion[Sequence[SymbolReference]],
        execution_cases: Sequence[NEA[Sequence[FileSystemElement], Sequence[FileSystemElement]]]):
    integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
        put,
        arguments=arguments.as_arguments,
        symbol_references=symbol_references,
        input_=
        helper.model_constructor_for_checked_dir__recursive(),
        execution=[
            NExArr(
                case.name,
                PrimAndExeExpectation.of_exe(),
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
    return FileMatcherSymbolContext.of_sdv(
        'test_fails_if_applied',
        sdv_components.matcher_sdv_from_constant_primitive(
            matcher_w_init_action.matcher_that_applies_assertion(
                put,
                asrt.fail('must not be applied'),
                lambda x: x,
                asrt.MessageBuilder.new_empty(),
                True,
            )
        )
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
