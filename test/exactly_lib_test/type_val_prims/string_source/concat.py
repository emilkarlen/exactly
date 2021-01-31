import itertools
import unittest
from contextlib import contextmanager
from typing import Sequence, ContextManager, List

from exactly_lib.definitions.primitives import string_source
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_source.impls import concat as sut
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, Assertion
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import \
    SourceConstructorWAppEnvForTest
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_contents import \
    StringSourceContentsFromLines, StringSourceContentsWCheckOfMaxNumAccessedLines
from exactly_lib_test.type_val_prims.string_source.test_resources.string_sources import StringSourceOfContents, \
    string_source_that_must_not_be_used
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree
from exactly_lib_test.util.description_tree.test_resources import rendering_assertions as asrt_trace_rendering


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestStructure(),
        unittest.makeSuite(TestDependenceOnExternalResources),
        unittest.makeSuite(TestContents),
        unittest.makeSuite(TestAsLinesShouldBeLazy),
    ])


class TestStructure(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        expected_contents = ''
        part1 = StringSourcePartConstructor.empty(
            'part 1',
            may_depend_on_external_resources=False,
        )
        part2 = StringSourcePartConstructor.empty(
            'part 2',
            may_depend_on_external_resources=False,
        )
        part3 = StringSourcePartConstructor.empty(
            'part 3',
            may_depend_on_external_resources=False,
        )
        cases = [
            NameAndValue(
                '2 parts',
                (part1, part2),
            ),
            NameAndValue(
                '3 parts',
                (part1, part2, part3),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                parts = case.value
                source_constructor = _SourceConstructor(parts)

                structure_expectation = _matches_structure_root([part.expected_structure() for part in parts])

                expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                    expected_contents,
                    may_depend_on_external_resources=
                    asrt.anything_goes(),
                    frozen_may_depend_on_external_resources=
                    asrt.anything_goes(),
                    structure=structure_expectation,
                )

                assertion = multi_obj_assertions.assertion_of_2_seq_w_file_first_and_last(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor),
                )


class TestDependenceOnExternalResources(unittest.TestCase):
    def test_2_parts(self):
        # ARRANGE #
        for part1_deps in [False, True]:
            for part2_deps in [False, True]:
                self._check([part1_deps, part2_deps])

    def test_3_parts(self):
        # ARRANGE #
        for part1_deps in [False, True]:
            for part2_deps in [False, True]:
                for part3_deps in [False, True]:
                    self._check([part1_deps, part2_deps, part3_deps])

    def _check(self, parts_deps: Sequence[bool]):
        expected_contents = ''
        with self.subTest(dependencies=parts_deps):
            parts = [
                StringSourcePartConstructor.empty(
                    'part ' + str(part_deps),
                    may_depend_on_external_resources=part_deps,
                )
                for part_deps in parts_deps
            ]
            expected_dependencies = any(parts_deps)
            source_constructor = _SourceConstructor(parts)
            expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                expected_contents,
                may_depend_on_external_resources=
                asrt.equals(expected_dependencies),
                frozen_may_depend_on_external_resources=
                asrt.anything_goes(),
                structure=asrt.anything_goes(),
            )

            assertion = multi_obj_assertions.assertion_of_2_seq_w_file_first_and_last(expectation)
            # ACT & ASSERT #
            assertion.apply_without_message(
                self,
                multi_obj_assertions.SourceConstructors.of_common(source_constructor),
            )


class TestContents(unittest.TestCase):
    def test_2_parts(self):
        # ARRANGE #
        for part1_lines_variant in lines_variants('a'):
            for part2_lines_variant in lines_variants('b'):
                with self.subTest(part1=part1_lines_variant.name,
                                  part2=part2_lines_variant.name):
                    self._check([part1_lines_variant.value,
                                 part2_lines_variant.value])

    def test_3_parts(self):
        # ARRANGE #
        for part1_lines_variant in lines_variants('a'):
            for part2_lines_variant in lines_variants('b'):
                for part3_lines_variant in lines_variants('c'):
                    with self.subTest(part1=part1_lines_variant.name,
                                      part2=part2_lines_variant.name,
                                      part3=part3_lines_variant.name):
                        self._check([part1_lines_variant.value,
                                     part2_lines_variant.value,
                                     part3_lines_variant.value])

    def _check(self, parts_lines: Sequence[Sequence[str]]):
        parts = [
            StringSourcePartConstructor(
                'part ' + str(part_num),
                part_lines,
                may_depend_on_external_resources=False,
            )
            for part_num, part_lines in enumerate(parts_lines, 1)
        ]
        expected_contents = ''.join(itertools.chain.from_iterable([
            part_lines
            for part_lines in parts_lines
        ]))

        source_constructor = _SourceConstructor(parts)

        expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
            expected_contents,
            may_depend_on_external_resources=
            asrt.anything_goes(),
            frozen_may_depend_on_external_resources=
            asrt.anything_goes(),
            structure=asrt.anything_goes(),
        )

        assertion = multi_obj_assertions.assertion_of_2_seq_w_file_first_and_last(expectation)
        # ACT & ASSERT #
        assertion.apply_without_message(
            self,
            multi_obj_assertions.SourceConstructors.of_common(source_constructor),
        )


class TestAsLinesShouldBeLazy(unittest.TestCase):
    def test_lines_from_only_first_ss(self):
        # ARRANGE #
        lines_of_ss_1 = [
            'ss1/1\n',
            'ss1/2\n',
        ]
        for max_num_lines_to_access in [1, 2]:
            checked = sut.string_source([
                self._source_with_num_lines_check(lines_of_ss_1, max_num_lines_to_access),
                string_source_that_must_not_be_used(),
            ],
                0
            )
            with self.subTest(max_num_lines_to_access=max_num_lines_to_access):
                # ACT & ASSERT #
                with checked.contents().as_lines as lines:
                    for _ in range(max_num_lines_to_access):
                        next(lines)

    def test_last_line_of_ss1_do_not_end_w_new_line__get_1st_from_ss2(self):
        # ARRANGE #
        lines_of_ss_1 = [
            'ss1/1',
        ]
        lines_of_ss_2 = [
            'ss2/1\n',
            'ss2/2\n',
        ]
        checked = sut.string_source([
            self._source_with_num_lines_check(lines_of_ss_1, max_num_lines_to_access=1),
            self._source_with_num_lines_check(lines_of_ss_2, max_num_lines_to_access=1),
        ],
            0
        )
        # ACT & ASSERT #
        with checked.contents().as_lines as lines:
            next(lines)

    def test_last_line_of_ss1_do_not_end_w_new_line__get_2nd_from_ss2(self):
        # ARRANGE #
        lines_of_ss_1 = [
            'ss1/1',
        ]
        lines_of_ss_2 = [
            'ss2/1\n',
            'ss2/2\n',
            'ss2/3\n',
        ]
        checked = sut.string_source([
            self._source_with_num_lines_check(lines_of_ss_1, max_num_lines_to_access=1),
            self._source_with_num_lines_check(lines_of_ss_2, max_num_lines_to_access=2),
        ],
            0
        )
        # ACT & ASSERT #
        with checked.contents().as_lines as lines:
            next(lines)
            next(lines)

    def _source_with_num_lines_check(self,
                                     lines: List[str],
                                     max_num_lines_to_access: int) -> StringSource:
        contents = StringSourceContentsFromLines(
            lines,
            DirFileSpaceThatMustNoBeUsed(),
        )
        return StringSourceOfContents.of_identical(
            StringSourceContentsWCheckOfMaxNumAccessedLines(
                self,
                contents,
                max_num_lines_to_access,
            )
        )


def _matches_structure_root(children: Sequence[Assertion[Node]]) -> Assertion[NodeRenderer]:
    matches_root_node = asrt_d_tree.matches_node(
        header=asrt.equals(string_source.CONCAT_NAME),
        data=asrt.is_none,
        details=asrt.is_empty_sequence,
        children=asrt.matches_sequence(children),
    )
    return asrt_trace_rendering.matches_node_renderer(matches_root_node)


class StringSourcePartConstructor:
    def __init__(self,
                 header: str,
                 lines: Sequence[str],
                 may_depend_on_external_resources: bool,
                 ):
        self.header = header
        self.lines = lines
        self.may_depend_on_external_resources = may_depend_on_external_resources

    @staticmethod
    def empty(
            header: str,
            may_depend_on_external_resources: bool,
    ) -> 'StringSourcePartConstructor':
        return StringSourcePartConstructor(header, (), may_depend_on_external_resources)

    def construct(self, tmp_file_space: DirFileSpace) -> StringSource:
        return StringSourceOfContents.of_identical(
            StringSourceContentsFromLines(self.lines, tmp_file_space, self.may_depend_on_external_resources),
            self._new_structure_builder,
        )

    def expected_structure(self) -> Assertion[Node]:
        return asrt_d_tree.matches_node(
            header=asrt.equals(self.header),
            data=asrt.is_none,
            details=asrt.is_empty_sequence,
            children=asrt.is_empty_sequence,
        )

    def _new_structure_builder(self) -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder.of_details(self.header, ())


class _SourceConstructor(SourceConstructorWAppEnvForTest):
    def __init__(self, parts: Sequence[StringSourcePartConstructor]):
        super().__init__()
        self.parts = parts

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        parts = [
            part.construct(app_env.tmp_files_space)
            for part in self.parts
        ]
        yield sut.string_source(parts, _MEM_BUFF_SIZE)


_MEM_BUFF_SIZE = 100


def lines_variants(unique_str: str) -> Sequence[NameAndValue[Sequence[str]]]:
    # Number of lines variants: 0, 1, 2
    # Last line variants: do NOT end with new-line, DO end with new-line

    def w_nl(line_num: int) -> str:
        return unique_str + str(line_num) + '\n'

    def wo_nl(line_num: int) -> str:
        return unique_str + str(line_num)

    return [
        NameAndValue('empty', []),
        NameAndValue('1 line (last wo new-line)', [wo_nl(1)]),
        NameAndValue('1 line (last w new-line)', [w_nl(1)]),
        NameAndValue('2 lines (last wo new-line)', [w_nl(1), wo_nl(2)]),
        NameAndValue('2 lines (last w new-line)', [w_nl(1), w_nl(2)]),
        NameAndValue('2 lines (last empty)', [w_nl(1), '']),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
