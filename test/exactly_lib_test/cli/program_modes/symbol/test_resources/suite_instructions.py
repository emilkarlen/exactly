from exactly_lib_test.test_suite.test_resources import preprocessor_for_search_replace
from exactly_lib_test.test_suite.test_resources.test_suite_definition import test_suite_definition_with_instructions

_SET_SEARCH_REPLACE_PREPROC = 'python-preproc'


def set_search_replace_preprocessor(to_replace: str,
                                    replacement: str) -> str:
    return ' '.join([
        _SET_SEARCH_REPLACE_PREPROC,
        to_replace,
        replacement
    ])


SUITE_DEFINITION_WITH_SEARCH_REPLACE_PREPROC = test_suite_definition_with_instructions(
    {
        _SET_SEARCH_REPLACE_PREPROC:
            preprocessor_for_search_replace.setup(_SET_SEARCH_REPLACE_PREPROC)
    },
)
