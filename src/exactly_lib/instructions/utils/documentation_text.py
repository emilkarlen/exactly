from exactly_lib.util.cli_syntax.elements.argument import Named
from exactly_lib.util.textformat.structure import structures as docs


def paths_uses_posix_syntax() -> list:
    return docs.paras("""Paths uses posix syntax.""")


def default_relativity(path_arg_name: str,
                       default_relativity_location: str) -> list:
    return docs.paras(_DEFAULT_RELATIVITY
                      .format(path=path_arg_name,
                              default_relativity_location=default_relativity_location))

RELATIVITY_ARGUMENT = Named('RELATIVITY')

_DEFAULT_RELATIVITY = """\
By default {path} is relative the {default_relativity_location}.
"""

HERE_DOC_SUFFIX = '<<MARKER <lines> MARKER'
