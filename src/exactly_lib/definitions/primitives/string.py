import re

HERE_DOCUMENT_MARKER_PREFIX = '<<'
HERE_DOCUMENT_TOKEN_RE = re.compile('(<<)([0-9a-zA-Z_-]+)')
