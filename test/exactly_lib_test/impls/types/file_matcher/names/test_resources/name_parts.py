import pathlib
from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.impls.types.file_matcher.impl.names.doc import FileNames, file_name_examples
from exactly_lib_test.impls.types.file_matcher.names.test_resources import checkers
from exactly_lib_test.impls.types.file_matcher.names.test_resources.configuration import Configuration, TestCaseBase
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check


class Case:
    def __init__(self,
                 name: str,
                 stem: str,
                 suffixes: str,
                 suffix: str,
                 ):
        self.name = name
        self.stem = stem
        self.suffixes = suffixes
        self.suffix = suffix

    @staticmethod
    def of_eq_suffix_es(
            name: str,
            stem: str,
            suffix_es: str,
    ) -> 'Case':
        return Case(name, stem, suffix_es, suffix_es)

    @staticmethod
    def of_file_name_example(names: FileNames) -> 'Case':
        return Case(names.name, names.stem, names.suffixes, names.suffix)


class NamePartsConfiguration(Configuration, ABC):
    @abstractmethod
    def get_name_part(self, case: Case) -> str:
        raise NotImplementedError('abstract method')


class TestNamePart(TestCaseBase, ABC):
    @property
    @abstractmethod
    def conf(self) -> NamePartsConfiguration:
        raise NotImplementedError('abstract method')

    def test_glob_pattern(self):
        self._test_glob_pattern_cases(CASES)

    def test_glob_pattern_documentation_examples(self):
        self._test_glob_pattern_cases(EXAMPLE_CASES)

    def test_regex(self):
        self._test_regex_cases(CASES)

    def test_regex_documentation_examples(self):
        self._test_regex_cases(EXAMPLE_CASES)

    def _test_glob_pattern_cases(self, cases: Sequence[Case]):
        for case in cases:
            tested_part = self.conf.get_name_part(case)
            with self.subTest(name=case.name,
                              part=tested_part):
                checkers.check_glob(
                    self,
                    self.conf,
                    pattern=glob_pattern_matching_exactly(tested_part),
                    model=integration_check.constant_relative_path(
                        pathlib.Path('dir') / case.name
                    ),
                    expected_result=True,
                )

    def _test_regex_cases(self, cases: Sequence[Case]):
        for case in cases:
            tested_part = self.conf.get_name_part(case)
            with self.subTest(name=case.name,
                              part=tested_part):
                checkers.check_regex(
                    self,
                    self.conf,
                    pattern=regex_matching_exactly(tested_part),
                    ignore_case=False,
                    model=integration_check.constant_relative_path(
                        pathlib.Path('dir') / case.name
                    ),
                    expected_result=True,
                )


CASES = [
    Case.of_eq_suffix_es(
        'a',
        stem='a',
        suffix_es='',
    ),
    Case.of_eq_suffix_es(
        'a.',
        stem='a',
        suffix_es='.',
    ),
    Case.of_eq_suffix_es(
        'a.b',
        stem='a',
        suffix_es='.b',
    ),
    Case(
        'a.b.c',
        stem='a',
        suffixes='.b.c',
        suffix='.c',
    ),
    Case(
        'a.b.c.',
        stem='a',
        suffixes='.b.c.',
        suffix='.',
    ),
    Case(
        'a.b.c.d',
        stem='a',
        suffixes='.b.c.d',
        suffix='.d',
    ),
    Case.of_eq_suffix_es(
        '.b',
        stem='',
        suffix_es='.b',
    ),
    Case(
        '.b.c',
        stem='',
        suffixes='.b.c',
        suffix='.c',
    ),
    Case(
        'stem.suffix1.suffix2',
        stem='stem',
        suffixes='.suffix1.suffix2',
        suffix='.suffix2',
    ),
]

EXAMPLE_CASES = [
    Case.of_file_name_example(example)
    for example in file_name_examples()
]


def regex_matching_exactly(file_name_part: str) -> str:
    """
    Gives a regex that matches exactly the given string.

    :param file_name_part: Filename consisting of alphanum:s and dots.
    """
    return '^{}$'.format('\\.'.join(file_name_part.split('.')))


def glob_pattern_matching_exactly(file_name_part: str) -> str:
    """
    Gives a glob pattern that matches exactly the given string.

    :param file_name_part: Filename consisting of alphanum:s and dots.
    """
    return file_name_part
