from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv


class PathPartDdvAsFixedPath(PathPartDdv):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def value(self) -> str:
        return self._file_name


class PathPartDdvAsNothing(PathPartDdv):
    def value(self) -> str:
        return ''


class PathPartDdvVisitor:
    def visit(self, path_suffix: PathPartDdv):
        if isinstance(path_suffix, PathPartDdvAsFixedPath):
            return self.visit_fixed_path(path_suffix)
        elif isinstance(path_suffix, PathPartDdvAsNothing):
            return self.visit_nothing(path_suffix)
        raise TypeError('Not a {}: {}'.format(str(PathPartDdv), path_suffix))

    def visit_fixed_path(self, path_suffix: PathPartDdvAsFixedPath):
        raise NotImplementedError()

    def visit_nothing(self, path_suffix: PathPartDdvAsNothing):
        raise NotImplementedError()
