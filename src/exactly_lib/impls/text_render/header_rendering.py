from exactly_lib.common.report_rendering import header_blocks
from exactly_lib.util.render import combinators
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.structure import MinorBlock, LineElement, MajorBlock
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.str_.str_constructor import ToStringObject

UNEXPECTED = 'Unexpected'


class SimpleHeaderMinorBlockRenderer(Renderer[MinorBlock]):
    def __init__(self, single_line_to_str: ToStringObject):
        self._single_line_to_str = single_line_to_str

    def render(self) -> MinorBlock:
        header = LineElement(text_struct.StringLineObject(str(self._single_line_to_str)))
        return MinorBlock([header])


class HeaderValueRenderer(Renderer[MajorBlock]):
    def __init__(self,
                 header: ToStringObject,
                 value_description: SequenceRenderer[MinorBlock] = combinators.ConstantSequenceR(()),
                 ):
        self._header = header
        self._object_description = value_description

    @staticmethod
    def of_unexpected_attr_of_obj(
            attribute: ToStringObject,
            object_: ToStringObject,
            object_description: SequenceRenderer[MinorBlock] = combinators.ConstantSequenceR(()),
            attribute_of_object_word: str = 'of') -> Renderer[MajorBlock]:
        return HeaderValueRenderer(
            unexpected_attr_of_obj(attribute,
                                   object_,
                                   attribute_of_object_word),
            object_description,
        )

    def render(self) -> MajorBlock:
        return header_blocks.w_details(self._header, self._object_description).render()


def unexpected_attr_of_obj(attribute: ToStringObject,
                           object_: ToStringObject,
                           attribute_of_object_word: str = 'of',
                           ) -> ToStringObject:
    return str_constructor.Concatenate([
        UNEXPECTED,
        ' ',
        attribute,
        ' ',
        attribute_of_object_word,
        ' ',
        object_
    ],
    )
