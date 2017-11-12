from exactly_lib.util.textformat.structure import structures as docs

POSIX_SYNTAX = 'Posix syntax'


def paths_uses_posix_syntax() -> list:
    return docs.paras('Paths uses ' + POSIX_SYNTAX + '.')
