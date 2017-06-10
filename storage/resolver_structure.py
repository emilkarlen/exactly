import pathlib

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType


class SymbolValueResolver:
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name


class StringFragmentResolver:
    pass


class ConstantStringFragmentResolver(StringFragmentResolver):
    def __init__(self, string: str):
        self.string = string


class SymbolValueStringFragmentResolver(StringFragmentResolver):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name


class StringResolver:
    def __init__(self, fragment_resolvers: list):
        self.fragment_resolvers = fragment_resolvers


class ListComponentResolver:
    pass


class StringListComponentResolver(ListComponentResolver):
    def __init__(self, string_resolver: StringResolver):
        self.string_resolver = string_resolver


class SymbolValueListComponentResolver(ListComponentResolver):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name


class ListResolver:
    def __init__(self, component_resolvers: list):
        self.component_resolvers = component_resolvers


class PathRootResolver:
    pass


class AbsolutePathRootResolver(PathRootResolver):
    def __init__(self, absolute_path: pathlib.Path):
        self.absolute_path = absolute_path


class CdRootResolver(PathRootResolver):
    pass


class SymbolPathRootResolver(PathRootResolver):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name


class ExactlyDirPathRootResolver(PathRootResolver):
    def __init__(self, root_dir: RelOptionType):
        self.root_dir = root_dir


class PathResolver:
    def __init__(self,
                 root_resolver: PathRootResolver,
                 path_suffix_resolvers: list):
        """
        :param path_suffix_resolvers: [StringResolver]
        """
        self.root_resolver = root_resolver
        self.path_suffix_resolvers = path_suffix_resolvers
