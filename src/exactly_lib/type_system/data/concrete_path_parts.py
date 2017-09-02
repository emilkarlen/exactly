from exactly_lib.type_system.data.path_part import PathPart


class PathPartAsFixedPath(PathPart):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def value(self) -> str:
        return self._file_name


class PathPartAsNothing(PathPart):
    def value(self) -> str:
        return ''


class PathPartVisitor:
    def visit(self, path_suffix: PathPart):
        if isinstance(path_suffix, PathPartAsFixedPath):
            return self.visit_fixed_path(path_suffix)
        elif isinstance(path_suffix, PathPartAsNothing):
            return self.visit_nothing(path_suffix)
        raise TypeError('Not a {}: {}'.format(str(PathPart), path_suffix))

    def visit_fixed_path(self, path_suffix: PathPartAsFixedPath):
        raise NotImplementedError()

    def visit_nothing(self, path_suffix: PathPartAsNothing):
        raise NotImplementedError()
