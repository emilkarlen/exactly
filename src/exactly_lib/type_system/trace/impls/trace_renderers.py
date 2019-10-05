from typing import Sequence

from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail


class DetailsRendererOfErrorMessageResolver(DetailsRenderer):
    def __init__(self, message_resolver: ErrorMessageResolver):
        self._message_resolver = message_resolver

    def render(self) -> Sequence[Detail]:
        return [tree.PreFormattedStringDetail(self._message_resolver.resolve())]
