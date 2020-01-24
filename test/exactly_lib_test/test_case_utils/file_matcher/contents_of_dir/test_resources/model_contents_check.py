import pathlib
import unittest
from pathlib import Path
from typing import List, Sequence, Callable

from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.matcher.impls.sdv_components import MatcherDdvFromPartsWConstantAdv, \
    MatcherSdvFromParts
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FilesMatcherDdv, FilesMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, Dir, empty_file, empty_dir
from exactly_lib_test.test_resources.test_utils import NEA


def cases() -> Sequence[NameAndValue[List[FileSystemElement]]]:
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
            'single empty dir',
            [empty_dir('an-empty-dir')],
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
            'directory with contents - multiple levels',
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


def checker(put: unittest.TestCase,
            model_dir: PathSdv,
            expected_contents: List[FileSystemElement]) -> FilesMatcherSdv:
    def make_ddv(symbols: SymbolTable) -> FilesMatcherDdv:
        def make_matcher(tcds: Tcds) -> MatcherWTraceAndNegation[FilesMatcherModel]:
            return _ModelContentsChecker(
                put,
                model_dir.resolve(symbols).value_of_any_dependency(tcds),
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
                 contents_root: pathlib.Path,
                 expected_contents: List[FileSystemElement],
                 ):
        self._put = put
        self._contents_root = contents_root
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
        expected__rel_contents_root = self._expected_paths__rel_contents_root()
        actual__rel_contents_root = self._actual_paths__rel_contents_root(model)

        self._put.assertEqual(expected__rel_contents_root, actual__rel_contents_root,
                              'paths rel contents root')

        expected__absolute = self._expected_paths__absolute(expected__rel_contents_root)
        actual__absolute = self._actual_paths__absolute(model)

        self._put.assertEqual(expected__absolute, actual__absolute,
                              'absolute paths')

        return self._matching_result()

    def _matching_result(self) -> MatchingResult:
        result = True
        return MatchingResult(result,
                              renderers.Constant(
                                  tree.Node.empty(self.name, result)
                              ))

    @staticmethod
    def _actual_paths__rel_contents_root(model: FilesMatcherModel) -> List[Path]:
        ret_val = [
            f.relative_to_root_dir
            for f in model.files()
        ]
        ret_val.sort()
        return ret_val

    @staticmethod
    def _actual_paths__absolute(model: FilesMatcherModel) -> List[Path]:
        ret_val = [
            f.path.primitive
            for f in model.files()
        ]
        ret_val.sort()
        return ret_val

    def _expected_paths__rel_contents_root(self) -> List[Path]:
        ret_val = _paths_rel_root(Path('.'), self._expected_contents, FileType.__contains__)

        ret_val.sort()

        return ret_val

    def _expected_paths__absolute(self, expected__rel_contents_root: List[Path]) -> List[Path]:
        return [
            self._contents_root / rel_contents_root
            for rel_contents_root in expected__rel_contents_root
        ]


def _paths_rel_root(root: Path,
                    contents: List[FileSystemElement],
                    files_type_is_included: Callable[[FileType], bool],
                    ) -> List[Path]:
    ret_val = []
    for element in contents:
        if files_type_is_included(element.file_type):
            ret_val.append(root / element.name)
        if isinstance(element, Dir):
            ret_val += _paths_rel_root(root / element.name,
                                       element.file_system_element_contents,
                                       files_type_is_included)

    return ret_val


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
