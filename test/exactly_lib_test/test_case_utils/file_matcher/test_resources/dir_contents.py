import unittest
from pathlib import Path
from typing import Sequence, List

from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls.sdv_components import MatcherSdvFromParts, \
    MatcherDdvFromPartsWConstantAdv
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FilesMatcherDdv, FilesMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents, empty_file, sym_link, \
    FileSystemElement, Dir, empty_dir
from exactly_lib_test.test_resources.test_utils import NEA


def invalid_file_cases(model_file_name: str) -> Sequence[NameAndValue[DirContents]]:
    return [
        NameAndValue(
            'file does not exist',
            empty_dir_contents(),
        ),
        NameAndValue(
            'file is regular file',
            DirContents([
                empty_file(model_file_name)
            ]),
        ),
        NameAndValue(
            'file is broken sym link',
            DirContents([
                sym_link(model_file_name, 'non-existing-target')
            ]),
        ),
        NameAndValue(
            'file is sym link to regular file',
            DirContents([
                sym_link(model_file_name, 'regular file'),
                empty_file('regular file')
            ]),
        ),
    ]


def model_contents_cases() -> Sequence[NameAndValue[List[FileSystemElement]]]:
    return [
        NameAndValue(
            'empty',
            [],
        ),
        NameAndValue(
            'single regular file',
            [empty_file('an-empty-file')],
        ),
        NameAndValue(
            'directory with contents - one level',
            [
                empty_file('an-empty-file'),
                Dir('non-empty-dir',
                    [
                        empty_file('file-in-dir'),
                        empty_dir('dir-in-dir'),
                    ]),
            ]
        ),
        NameAndValue(
            'directory with contents - one level',
            [
                Dir('non-empty-dir-1',
                    [empty_file('file-in-dir-1')]
                    ),
                Dir('non-empty-dir-2',
                    [
                        empty_file('file-in-dir-2'),
                        Dir('non-empty-dir-2-1',
                            [
                                empty_file('file-in-dir-2-1'),
                                empty_dir('dir-in-dir-2-1'),
                            ])
                    ]
                    ),
            ]
        ),
    ]


def identical_expected_and_actual(name: str,
                                  actual: List[FileSystemElement],
                                  ) -> NEA[List[FileSystemElement], List[FileSystemElement]]:
    return NEA(name, actual, actual)


def expected_is_actual_with_empty_dirs(name: str,
                                       actual: List[FileSystemElement],
                                       ) -> NEA[List[FileSystemElement], List[FileSystemElement]]:
    def with_empty_dir(x: FileSystemElement) -> FileSystemElement:
        if isinstance(x, Dir):
            return empty_dir(x.name)
        else:
            return x

    expected = [
        with_empty_dir(element)
        for element in actual
    ]

    return NEA(name, expected, actual)


def model_contents_checker(put: unittest.TestCase,
                           expected_contents: List[FileSystemElement]) -> FilesMatcherSdv:
    def make_ddv(symbols: SymbolTable) -> FilesMatcherDdv:
        def make_matcher(tcds: Tcds) -> MatcherWTraceAndNegation[FilesMatcherModel]:
            return _ModelContentsChecker(
                put,
                expected_contents,
            )

        return MatcherDdvFromPartsWConstantAdv(
            make_matcher,
            _ModelContentsChecker.STRUCTURE,
        )

    return FilesMatcherSdv(
        MatcherSdvFromParts(
            (),
            make_ddv,
        )
    )


class _ModelContentsChecker(MatcherWTraceAndNegation[FilesMatcherModel]):
    STRUCTURE = renderers.header_only('_ModelContentsChecker')

    def __init__(self,
                 put: unittest.TestCase,
                 expected_contents: List[FileSystemElement],
                 ):
        self._put = put
        self._expected_contents = expected_contents

    @property
    def name(self) -> str:
        return str(type(self))

    def structure(self) -> StructureRenderer:
        return self.STRUCTURE

    @property
    def negation(self) -> MatcherWTraceAndNegation[FilesMatcherModel]:
        raise NotImplementedError('unsupported')

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        expected = self._expected_paths()
        actual = self._actual_paths(model)

        self._put.assertEqual(expected, actual)

        return self._matching_result()

    def _matching_result(self) -> MatchingResult:
        result = True
        return MatchingResult(result,
                              renderers.Constant(
                                  tree.Node.empty(self.name, result)
                              ))

    @staticmethod
    def _actual_paths(model: FilesMatcherModel) -> List[Path]:
        ret_val = [
            f.relative_to_root_dir
            for f in model.files()
        ]
        ret_val.sort()
        return ret_val

    def _expected_paths(self) -> List[Path]:
        ret_val = self._expected_contents_of_dir(Path('.'), self._expected_contents)

        ret_val.sort()

        return ret_val

    def _expected_contents_of_dir(self,
                                  the_dir: Path,
                                  contents: List[FileSystemElement],
                                  ) -> List[Path]:
        ret_val = []
        for element in contents:
            ret_val.append(the_dir / element.name)
            if isinstance(element, Dir):
                ret_val += self._expected_contents_of_dir(the_dir / element.name, element.file_system_element_contents)

        return ret_val
