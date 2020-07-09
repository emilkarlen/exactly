import pathlib

from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace


class TmpDirFileSpaceAsDirCreatedOnDemand(TmpDirFileSpace):
    """
    A tmp file space that is a dir that (probably) do not exist,
    but is created when tmp files are demanded.
    """

    def __init__(self, root_dir_to_create_on_demand: pathlib.Path):
        """
        :param root_dir_to_create_on_demand: Either must not exist, or must be an existing empty dir
        If it does not exit, it must be possible to create it as a dir
        (i.e no path components may be a file, and must be writable).
        """
        self._root_dir_to_create_on_demand = root_dir_to_create_on_demand
        self._next_file_number = 1
        self._existing_root_dir_path = None

    def new_path(self) -> pathlib.Path:
        file_num = self._next_file_number
        self._next_file_number += 1
        base_name = '%02d' % file_num
        return self._root_dir() / base_name

    def new_path_as_existing_dir(self) -> pathlib.Path:
        ret_val = self.new_path()
        ret_val.mkdir()
        return ret_val

    def sub_dir_space(self) -> TmpDirFileSpace:
        return TmpDirFileSpaceAsDirCreatedOnDemand(
            self.new_path()
        )

    def _root_dir(self) -> pathlib.Path:
        if self._existing_root_dir_path is None:
            self._existing_root_dir_path = self._root_dir_to_create_on_demand
            self._existing_root_dir_path.mkdir(parents=True,
                                               exist_ok=True)
        return self._existing_root_dir_path


class TmpDirFileSpaceThatMustNoBeUsed(TmpDirFileSpace):
    def new_path(self) -> pathlib.Path:
        raise ValueError('must not be used')

    def new_path_as_existing_dir(self) -> pathlib.Path:
        raise ValueError('must not be used')

    def sub_dir_space(self) -> TmpDirFileSpace:
        raise ValueError('must not be used')
