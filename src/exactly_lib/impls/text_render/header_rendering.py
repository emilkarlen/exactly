from exactly_lib.util.render import combinators
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer, SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as text_struct
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects
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


def unexpected_attribute__major_block(attribute: ToStringObject) -> Renderer[MajorBlock]:
    return blocks.MajorBlockOfSingleLineObject(
        line_objects.StringLineObject(unexpected(attribute))
    )


class UnexpectedAttrOfObjMajorBlockRenderer(Renderer[MajorBlock]):
    def __init__(self,
                 attribute: ToStringObject,
                 object_: ToStringObject,
                 object_description: SequenceRenderer[MinorBlock] = combinators.ConstantSequenceR(()),
                 ):
        self._attribute = attribute
        self._object = object_
        self._object_description = object_description

    def render(self) -> MajorBlock:
        minor_blocks = [
            blocks.MinorBlockOfSingleLineObject(
                line_objects.StringLineObject(unexpected_attr_of_obj(self._attribute,
                                                                     self._object))).render()
        ]
        minor_blocks += rend_comb.Indented(self._object_description).render_sequence()

        return MajorBlock(minor_blocks)


def unexpected(attribute: ToStringObject) -> ToStringObject:
    return str_constructor.Concatenate([
        UNEXPECTED,
        ' ',
        attribute,
    ],
    )


def unexpected_attr_of_obj(attribute: ToStringObject,
                           object_: ToStringObject) -> ToStringObject:
    return str_constructor.Concatenate([
        UNEXPECTED,
        ' ',
        attribute,
        ' of ',
        object_
    ],
    )
