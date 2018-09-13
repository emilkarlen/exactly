import os
from typing import Iterable, Tuple, Dict

from exactly_lib.cli.program_modes.help.error import HelpError
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, EntityDocumentation
from exactly_lib.util import value_lookup
from exactly_lib.util.value_lookup import Match, T


def entities_key_value_iter(entities_help: EntityTypeHelp) -> Iterable[Tuple[str, EntityDocumentation]]:
    return map(lambda entity_doc: (entity_doc.singular_name(), entity_doc),
               entities_help.all_entities)


def lookup_argument__dict(object_name: str,
                          argument_pattern: str,
                          elements: Dict[str, T]) -> Match[T]:
    return lookup_argument(object_name,
                           argument_pattern,
                           list(elements.items()))


def lookup_argument(object_name: str,
                    argument_pattern: str,
                    elements: Iterable[Tuple[str, T]]) -> Match[T]:
    try:
        return value_lookup.lookup(argument_pattern, elements)
    except value_lookup.NoMatchError:
        raise HelpError('No matching ' + object_name)
    except value_lookup.MultipleMatchesError as ex:
        matches_list = ['  ' + key_value[0] for key_value in ex.matching_key_values]
        header = 'Multiple matches. Which %s do you mean?' % object_name
        lines = [header] + matches_list
        msg = os.linesep.join(lines)
        raise HelpError(msg)
