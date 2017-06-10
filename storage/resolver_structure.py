import pathlib

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, ResolvingDependency, DEPENDENCY_DICT
from exactly_lib.util.symbol_table import SymbolTable


class ResolvingDependencyError(Exception):
    def __init__(self,
                 error_message: str,
                 symbols_path: list,
                 ):
        self.error_message = error_message
        self.symbols_path = symbols_path

    def add_parent_symbol_to_path(self, symbol_name):
        self.symbols_path.append(symbol_name)


class Resolver:
    def assert_is_resolvable(self,
                             dependency: ResolvingDependency,
                             symbols: SymbolTable):
        """
        :raises ResolvingDependencyError: Value cannot be resolved with given dependency
        """
        raise NotImplementedError()


def _check_symbol(dependency: ResolvingDependency,
                  symbols: SymbolTable,
                  symbol_to_check: str):
    resolver_for_symbol = symbols.lookup(symbol_to_check)
    assert isinstance(resolver_for_symbol, Resolver)
    try:
        resolver_for_symbol.assert_is_resolvable(dependency, symbols)
    except ResolvingDependencyError as ex:
        ex.add_parent_symbol_to_path(symbol_to_check)
        raise ex


def _check_resolvers(dependency: ResolvingDependency,
                     symbols: SymbolTable,
                     resolvers: iter):
    for resolver in resolvers:
        assert isinstance(resolver, Resolver)
        resolver.assert_is_resolvable(dependency, symbols)


class StringFragmentResolver(Resolver):
    pass


class ConstantStringFragmentResolver(StringFragmentResolver):
    def __init__(self, string: str):
        self.string = string

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        pass


class SymbolValueStringFragmentResolver(StringFragmentResolver):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        _check_symbol(dependency, symbols, self.symbol_name)


class StringResolver(Resolver):
    def __init__(self, fragment_resolvers: list):
        self.fragment_resolvers = fragment_resolvers

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        _check_resolvers(dependency, symbols, self.fragment_resolvers)


class ListComponentResolver(Resolver):
    pass


class StringListComponentResolver(ListComponentResolver):
    def __init__(self, string_resolver: StringResolver):
        self.string_resolver = string_resolver

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        self.string_resolver.assert_is_resolvable(dependency, symbols)


class SymbolValueListComponentResolver(ListComponentResolver):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        _check_symbol(dependency, symbols, self.symbol_name)


class ListResolver(Resolver):
    def __init__(self, component_resolvers: list):
        self.component_resolvers = component_resolvers

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        _check_resolvers(dependency, symbols, self.component_resolvers)


class PathRootResolver(Resolver):
    pass


class AbsolutePathRootResolver(PathRootResolver):
    def __init__(self, absolute_path: pathlib.Path):
        self.absolute_path = absolute_path

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        pass


class SymbolPathRootResolver(PathRootResolver):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        _check_symbol(dependency, symbols, self.symbol_name)


class TestCaseyDirPathRootResolver(PathRootResolver):
    def __init__(self, root_dir: RelOptionType):
        self.root_dir = root_dir

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        if self.root_dir not in DEPENDENCY_DICT[dependency]:
            msg = '(TODO improve error message!) Unaccepted dependency: Expected {}. Found: {}'.format(
                dependency,
                self.root_dir
            )
            raise ResolvingDependencyError(msg, [])


class PathResolver(Resolver):
    def __init__(self,
                 root_resolver: PathRootResolver,
                 path_suffix_resolvers: list):
        """
        :param path_suffix_resolvers: [StringResolver]
        """
        self.root_resolver = root_resolver
        self.path_suffix_resolvers = path_suffix_resolvers

    def assert_is_resolvable(self, dependency: ResolvingDependency, symbols: SymbolTable):
        self.root_resolver.assert_is_resolvable(dependency, symbols)
        _check_resolvers(dependency, symbols, self.path_suffix_resolvers)
