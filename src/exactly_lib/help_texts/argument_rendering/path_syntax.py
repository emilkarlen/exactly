from exactly_lib.util.cli_syntax.elements import argument as a

PATH_SYNTAX_ELEMENT_NAME = 'PATH'

PATH_ARGUMENT = a.Named(PATH_SYNTAX_ELEMENT_NAME)
FILE_ARGUMENT = a.Named('FILE')
DIR_ARGUMENT = a.Named('DIR')

RELATIVITY_ARGUMENT = a.Named('RELATIVITY')
OPTIONAL_RELATIVITY_ARGUMENT_USAGE = a.Single(a.Multiplicity.OPTIONAL,
                                              RELATIVITY_ARGUMENT)
SYMBOL_REFERENCE = a.Named('SYMBOL-REFERENCE')


def path_or_symbol_reference(multiplicity: a.Multiplicity, path_argument: a.Named) -> a.ArgumentUsage:
    return a.Single(multiplicity, path_argument)


def mandatory_path_with_optional_relativity(path_argument: a.Named,
                                            may_use_symbols: bool = False,
                                            path_suffix_is_required: bool = True) -> list:
    multiplicity = a.Multiplicity.MANDATORY if path_suffix_is_required else a.Multiplicity.OPTIONAL
    path_part = a.Single(multiplicity, path_argument)
    return [
        OPTIONAL_RELATIVITY_ARGUMENT_USAGE,
        path_part,
    ]
