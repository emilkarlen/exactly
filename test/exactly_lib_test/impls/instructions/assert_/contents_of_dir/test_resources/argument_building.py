from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.definitions.test_case import reserved_words
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.tcfs.test_resources.path_arguments import PathArgument
from exactly_lib_test.test_resources import argument_renderer as arg_rends
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.matcher_argument import MatcherArgument

RECURSION_OPTION_ARG = arg_rends.OptionArgument(file_or_dir_contents.RECURSIVE_OPTION.name)
RECURSION_OPTION_STR = str(RECURSION_OPTION_ARG)


def _arguments(path: PathArgument,
               matcher: ArgumentElementsRenderer,
               ) -> ArgumentElementsRenderer:
    return arg_rends.SequenceOfArguments([
        path,
        arg_rends.Singleton(reserved_words.COLON),
        matcher,
    ])


def of_file_matcher(path: PathArgument,
                    file_matcher: FileMatcherArg) -> ArgumentElementsRenderer:
    return _arguments(path, file_matcher)


def non_recursive(path: PathArgument,
                  files_matcher: ArgumentElementsRenderer) -> ArgumentElementsRenderer:
    return _arguments(path, files_matcher)


def recursive(path: PathArgument,
              files_matcher: MatcherArgument,
              recursion_options: ArgumentElementsRenderer
              = RECURSION_OPTION_ARG,
              ) -> ArgumentElementsRenderer:
    return _arguments(
        path,
        arg_rends.SequenceOfArguments([recursion_options, files_matcher]),
    )
