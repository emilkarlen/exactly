import pathlib
import unittest

from exactly_lib.util.file_utils import TmpDirFileSpaceThatMustNoBeUsed


class TmpFileSpaceThatAllowsSinglePathGeneration(TmpDirFileSpaceThatMustNoBeUsed):
    def __init__(self,
                 put: unittest.TestCase,
                 storage_dir: pathlib.Path,
                 path_name: str,
                 ):
        self.put = put
        self.storage_dir = storage_dir
        self.path_name = path_name
        self._generated_path = None

    def new_path(self) -> pathlib.Path:
        if self._generated_path is not None:
            self.put.fail('The path has already been generated')
        return self.storage_dir / self.path_name
