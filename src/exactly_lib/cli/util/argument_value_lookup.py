import os

from exactly_lib.cli.program_modes.help.error import HelpError
from exactly_lib.cli.util import value_lookup
from exactly_lib.cli.util.value_lookup import Match
from exactly_lib.help.utils.entity_documentation import EntitiesHelp


def entities_key_value_iter(entities_help: EntitiesHelp) -> iter:
    return map(lambda entity_doc: (entity_doc.singular_name(), entity_doc),
               entities_help.all_entities)


def lookup_argument(object_name: str,
                    argument_pattern: str,
                    key_value_iter) -> Match:
    try:
        return value_lookup.lookup(argument_pattern, key_value_iter)
    except value_lookup.NoMatchError:
        raise HelpError('No matching ' + object_name)
    except value_lookup.MultipleMatchesError as ex:
        matches_list = ['  ' + key_value[0] for key_value in ex.matching_key_values]
        header = 'Multiple matches. Which %s do you mean?' % object_name
        lines = [header] + matches_list
        msg = os.linesep.join(lines)
        raise HelpError(msg)
