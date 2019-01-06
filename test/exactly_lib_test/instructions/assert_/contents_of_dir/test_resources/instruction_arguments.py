from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    AssertionVariantArgumentsConstructor, EmptyAssertionVariant, FilesMatcherArgumentsConstructor, no_selection, \
    SubSetSelectionArgumentConstructor
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForPfh, pfh_expectation_type_config
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration


class PathArgumentsConstructor:
    """
    Constructs
    - [RELATIVITY]
    - PATH
    """

    def __init__(self,
                 path: str):
        self._path = path

    def apply(self, rel_opt_config: RelativityOptionConfiguration) -> str:
        return '{relativity} {path}'.format(
            relativity=rel_opt_config.option_argument,
            path=self._path)


class CompleteArgumentsConstructor(InstructionArgumentsVariantConstructor):
    """
    Constructs a string for "complete" instruction arguments - common arguments
    followed by arguments for an assertion variant.
    """

    def __init__(self,
                 path: PathArgumentsConstructor,
                 files_matcher: FilesMatcherArgumentsConstructor,
                 ):
        self._path = path
        self._files_matcher = files_matcher

    def apply(self,
              etc: ExpectationTypeConfigForPfh,
              rel_opt_config: RelativityOptionConfiguration) -> str:
        return '{path} {files_matcher}'.format(
            path=self._path.apply(rel_opt_config),
            files_matcher=self._files_matcher.apply(etc))


def complete_arguments_constructor(path: str,
                                   assertion_variant: AssertionVariantArgumentsConstructor,
                                   file_matcher: str = '') -> CompleteArgumentsConstructor:
    return CompleteArgumentsConstructor(
        PathArgumentsConstructor(path),
        FilesMatcherArgumentsConstructor(
            SubSetSelectionArgumentConstructor(file_matcher),
            assertion_variant,
        )
    )


def arguments_constructor_for_variant(path: str,
                                      variant: AssertionVariantArgumentsConstructor) -> CompleteArgumentsConstructor:
    return CompleteArgumentsConstructor(
        PathArgumentsConstructor(path),
        FilesMatcherArgumentsConstructor(
            no_selection(),
            variant
        ))


def instruction_arguments_for_emptiness_check(rel_opt: RelativityOptionConfiguration,
                                              file_name: str) -> str:
    complete_args = arguments_constructor_for_variant(file_name,
                                                      EmptyAssertionVariant())
    return complete_args.apply(pfh_expectation_type_config(ExpectationType.POSITIVE),
                               rel_opt)


def path_and_matcher(file_name: str,
                     matcher: FilesMatcherArgumentsConstructor) -> CompleteArgumentsConstructor:
    return CompleteArgumentsConstructor(
        PathArgumentsConstructor(file_name),
        matcher
    )
