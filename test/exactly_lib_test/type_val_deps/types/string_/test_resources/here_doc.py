from exactly_lib.definitions.primitives import string


def here_doc_start_token(marker: str) -> str:
    return string.HERE_DOCUMENT_MARKER_PREFIX + marker
