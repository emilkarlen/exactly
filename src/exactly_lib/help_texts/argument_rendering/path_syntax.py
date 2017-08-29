from exactly_lib.help_texts.instruction_arguments import OPTIONAL_RELATIVITY_ARGUMENT_USAGE
from exactly_lib.util.cli_syntax.elements import argument as a


def path_or_symbol_reference(multiplicity: a.Multiplicity, path_argument: a.Named) -> a.ArgumentUsage:
    return a.Single(multiplicity, path_argument)


def mandatory_path_with_optional_relativity(path_argument: a.Named,
                                            path_suffix_is_required: bool = True) -> list:
    multiplicity = a.Multiplicity.MANDATORY if path_suffix_is_required else a.Multiplicity.OPTIONAL
    path_part = a.Single(multiplicity, path_argument)
    return [
        OPTIONAL_RELATIVITY_ARGUMENT_USAGE,
        path_part,
    ]
