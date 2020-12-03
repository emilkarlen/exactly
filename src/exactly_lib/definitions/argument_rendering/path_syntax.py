from typing import List, Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls import file_properties
from exactly_lib.impls.file_properties import FileType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.elements.argument import ArgumentUsage


def path_or_symbol_reference(multiplicity: a.Multiplicity, path_argument: a.Named) -> a.ArgumentUsage:
    return a.Single(multiplicity, path_argument)


def mandatory_path_with_optional_relativity(path_argument: a.Named,
                                            path_suffix_is_required: bool = True) -> List[ArgumentUsage]:
    multiplicity = a.Multiplicity.MANDATORY if path_suffix_is_required else a.Multiplicity.OPTIONAL
    path_part = a.Single(multiplicity, path_argument)
    return [path_part]


def the_path_of(a_file_description: str) -> str:
    return ' '.join((
        'The',
        syntax_elements.PATH_SYNTAX_ELEMENT.argument.name,
        'of',
        a_file_description,
    ))


def the_path_of_an_existing_file(file_type: Optional[FileType] = None,
                                 final_dot: bool = False) -> str:
    object_name = (
        file_properties.TYPE_INFO[file_type].name.singular
        if file_type is not None
        else
        'file'
    )
    if final_dot:
        object_name += '.'
    return the_path_of(' '.join(('an existing', object_name)))
