import pathlib
import unittest

from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util import dir_contents_selection as sut
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, sym_link
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAllFiles),
        unittest.makeSuite(TestNamePattern),
        unittest.makeSuite(TestFileType),
        unittest.makeSuite(TestAnd),
    ])


DESCRIPTION_IS_SINGLE_STR = asrt.matches_sequence([asrt.is_instance(str)])


def number_of_descriptions(n: int) -> asrt.ValueAssertion:
    return asrt.matches_sequence(n * [asrt.is_instance(str)])


class Arrangement:
    def __init__(self,
                 selector_is_mandatory):
        self.selector_is_mandatory = selector_is_mandatory


class Expectation:
    def __init__(self,
                 file_system_elements: list,
                 description: asrt.ValueAssertion,
                 ):
        self.file_system_elements = file_system_elements
        self.description = description


class TestCaseBase(unittest.TestCase):
    def _check_selector(self,
                        selectors: sut.Selectors,
                        dir_to_select_from: pathlib.Path,
                        expectation: Expectation):
        # ACT #

        actual = sut.get_selection(dir_to_select_from, selectors)

        # ASSERT #

        expected = [f.name for f in expectation.file_system_elements]

        actual_as_set = set(actual)

        expected_as_set = set(expected)

        self.assertEqual(expected_as_set,
                         actual_as_set)

        expectation.description.apply_with_message(self, selectors.selection_descriptions,
                                                   'descriptions')


class TestAllFiles(TestCaseBase):
    full_dir_contents = DirContents([
        empty_file('file-1'),
        empty_dir('dir-1'),
        sym_link('sym-link', 'dir-1'),
        sym_link('broken-sym-link', 'non-existing-file'),
    ])

    def test(self):
        with tmp_dir(self.full_dir_contents) as dir_to_select_from:
            self._check_selector(
                sut.all_files(),
                dir_to_select_from,
                Expectation(
                    file_system_elements=self.full_dir_contents.file_system_elements,
                    description=asrt.is_empty_list,
                ))


class TestNamePattern(TestCaseBase):
    pattern = 'include*'
    included = [
        empty_file('include-file'),
        empty_dir('include-dir'),
        sym_link('include-sym-link', 'include-file'),
        sym_link('include-broken-sym-link', 'non-existing-file'),
    ]
    excluded = [
        empty_file('exclude-file'),
        empty_dir('exclude-dir'),
        sym_link('exclude-sym-link', 'include-file'),
        sym_link('exclude-broken-sym-link', 'non-existing-file'),
    ]
    full_dir_contents = DirContents(included + excluded)

    def test(self):
        with tmp_dir(self.full_dir_contents) as dir_to_select_from:
            selector = sut.name_matches_pattern(self.pattern)
            self._check_selector(
                selector,
                dir_to_select_from,
                Expectation(
                    file_system_elements=self.included,
                    description=DESCRIPTION_IS_SINGLE_STR,
                ),
            )


class TestFileType(TestCaseBase):
    regular_file = empty_file('a file')
    directory = empty_dir('a dir')
    sym_link_to_regular_file = sym_link('a sym-link to file', regular_file.name)
    sym_link_to_directory = sym_link('a sym-link to dir', directory.name)
    sym_link_with_non_existing_target = sym_link('broken-sym-link', 'non-existing-file')

    full_dir_contents = DirContents([
        regular_file,
        directory,
        sym_link_to_regular_file,
        sym_link_to_directory,
        sym_link_with_non_existing_target,
    ])

    file_type_cases = [
        (
            file_properties.FileType.REGULAR,
            [
                regular_file,
                sym_link_to_regular_file,
            ],
        ),
        (
            file_properties.FileType.DIRECTORY,
            [
                directory,
                sym_link_to_directory,
            ],
        ),
        (
            file_properties.FileType.SYMLINK,
            [
                sym_link_to_regular_file,
                sym_link_to_directory,
                sym_link_with_non_existing_target,
            ],
        ),
    ]

    def test(self):
        with tmp_dir(self.full_dir_contents) as dir_to_select_from:
            for file_type, expected_file_system_elements in self.file_type_cases:
                selector = sut.file_type_is(file_type)
                with self.subTest(file_type=str(file_type)):
                    self._check_selector(
                        selector,
                        dir_to_select_from,
                        Expectation(
                            file_system_elements=expected_file_system_elements,
                            description=DESCRIPTION_IS_SINGLE_STR,
                        )
                    )


class TestAnd(TestCaseBase):
    sym_link_name_pattern = '*sym-link*'
    directory_name_pattern = '*dir*'

    regular_file = empty_file('a file')
    directory = empty_dir('a dir')
    sym_link_to_regular_file = sym_link('a sym-link to a file', regular_file.name)
    sym_link_to_directory = sym_link('a sym-link to a dir', directory.name)
    sym_link_with_non_existing_target = sym_link('broken sym-link', 'non-existing-file')

    regular_files = [
        regular_file,
        sym_link_to_regular_file,

    ]
    full_dir_contents = DirContents([
        regular_file,
        directory,
        sym_link_to_regular_file,
        sym_link_to_directory,
        sym_link_with_non_existing_target,
    ])

    def test_WHEN_file_types_are_disjoint_THEN_selection_SHOULD_be_empty(self):
        cases = [
            NameAndValue('no other selection',
                         sut.all_files(),
                         ),
            NameAndValue('one other selection that is a name pattern',
                         sut.name_matches_pattern('*'),
                         ),
            NameAndValue('one other selection that is a type restriction',
                         sut.file_type_is(FileType.SYMLINK),
                         ),
            NameAndValue('an additional selector for every type',
                         sut.and_also(sut.file_type_is(FileType.SYMLINK),
                                      sut.name_matches_pattern('*')),
                         ),
        ]
        disjoint_file_type_selector = sut.and_also(
            sut.file_type_is(file_properties.FileType.REGULAR),
            sut.file_type_is(file_properties.FileType.DIRECTORY),
        )
        with tmp_dir(self.full_dir_contents) as dir_to_select_from:
            for case in cases:
                selector = sut.and_also(disjoint_file_type_selector,
                                        case.value)
                with self.subTest(case_name=case.name):
                    self._check_selector(
                        selector,
                        dir_to_select_from,
                        Expectation(
                            file_system_elements=[],
                            description=asrt.anything_goes(),
                        )
                    )

    def test_many_name_patterns(self):
        selector = sut.and_also(
            sut.name_matches_pattern(self.sym_link_name_pattern),
            sut.name_matches_pattern(self.directory_name_pattern),
        )
        with tmp_dir(self.full_dir_contents) as dir_to_select_from:
            self._check_selector(
                selector,
                dir_to_select_from,
                Expectation(
                    file_system_elements=[self.sym_link_to_directory],
                    description=number_of_descriptions(2),
                )
            )

    def test_many_name_selectors_AND_single_type_selectors(self):
        name_selectors = sut.and_also(
            sut.name_matches_pattern(self.sym_link_name_pattern),
            sut.name_matches_pattern(self.directory_name_pattern),
        )
        type_selector = sut.file_type_is(FileType.DIRECTORY)

        selector = sut.and_also(name_selectors,
                                type_selector)
        with tmp_dir(self.full_dir_contents) as dir_to_select_from:
            self._check_selector(
                selector,
                dir_to_select_from,
                Expectation(
                    file_system_elements=[self.sym_link_to_directory],
                    description=number_of_descriptions(3),
                )
            )

    def test_type_selectors_that_are_not_disjoint(self):
        cases = [
            NameAndValue('no other selection',
                         sut.all_files(),
                         ),
            NameAndValue('one other selection that is a name pattern',
                         sut.name_matches_pattern('*'),
                         ),
        ]
        file_types_selector = sut.and_also(
            sut.file_type_is(file_properties.FileType.DIRECTORY),
            sut.file_type_is(file_properties.FileType.SYMLINK),
        )
        with tmp_dir(self.full_dir_contents) as dir_to_select_from:
            for case in cases:
                selector = sut.and_also(file_types_selector,
                                        case.value)
                with self.subTest(case_name=case.name):
                    self._check_selector(
                        selector,
                        dir_to_select_from,
                        Expectation(
                            file_system_elements=[self.sym_link_to_directory],
                            description=asrt.anything_goes(),
                        )
                    )
