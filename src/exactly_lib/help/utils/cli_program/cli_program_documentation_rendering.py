from exactly_lib.help.utils.cli_program.cli_program_documentation import CliProgramSyntaxDocumentation
from exactly_lib.help.utils.doc_utils import synopsis_section, description_section
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.rendering.see_also_section import see_also_items_paragraph, SEE_ALSO_TITLE
from exactly_lib.util.cli_syntax.elements.cli_program_syntax import DescribedArgument, \
    Synopsis
from exactly_lib.util.cli_syntax.render.cli_program_syntax import CommandLineSyntaxRenderer, \
    ArgumentInArgumentDescriptionRenderer
from exactly_lib.util.textformat.structure import structures as docs, lists


class ProgramDocumentationSectionContentsRenderer(SectionContentsRenderer):
    def __init__(self, program: CliProgramSyntaxDocumentation):
        self.program = program

    def apply(self, environment: RenderingEnvironment) -> docs.SectionContents:
        return _ProgramDocumentationRenderer(environment).apply(self.program)


class _ProgramDocumentationRenderer:
    def __init__(self, environment: RenderingEnvironment):
        self.environment = environment
        self.cmd_line_syntax_renderer = CommandLineSyntaxRenderer()
        self.arg_in_description_renderer = ArgumentInArgumentDescriptionRenderer()

    def apply(self, program: CliProgramSyntaxDocumentation) -> docs.SectionContents:
        sections = []
        sections.append(self._synopsis_section(program))
        sections.extend(self._description_sections(program))
        sections.extend(self._options_sections(program.argument_descriptions()))
        return docs.SectionContents([docs.para(program.description().single_line_description)],
                                    sections)

    def _synopsis_section(self, program: CliProgramSyntaxDocumentation) -> docs.Section:
        return synopsis_section(
            docs.SectionContents([self._list(map(self._synopsis_list_item, program.synopsises()))]))

    @staticmethod
    def _description_sections(program: CliProgramSyntaxDocumentation) -> list:
        description = program.description()
        if description.rest.is_empty:
            return []
        return [description_section(description.rest)]

    def _options_sections(self, argument_descriptions: list) -> list:
        if not argument_descriptions:
            return []
        l = self._list(map(self._arg_description_list_item, argument_descriptions))

        return [docs.section('OPTIONS', [l])]

    def _arg_description_list_item(self, argument: DescribedArgument) -> lists.HeaderContentListItem:
        header = docs.text(self.arg_in_description_renderer.visit(argument.argument))
        return docs.list_item(header, self._arg_description_list_item_contents(argument))

    def _arg_description_list_item_contents(self, argument: DescribedArgument) -> list:
        ret_val = []
        ret_val.extend(argument.description)
        if argument.see_also_items:
            ret_val.append(docs.para(SEE_ALSO_TITLE))
            ret_val.append(see_also_items_paragraph(argument.see_also_items, self.environment))
        return ret_val

    def _synopsis_list_item(self, synopsis: Synopsis) -> lists.HeaderContentListItem:
        header = self.cmd_line_syntax_renderer.apply(synopsis.command_line)
        content_paragraph_items = []
        if synopsis.maybe_single_line_description:
            content_paragraph_items.append(docs.para(synopsis.maybe_single_line_description))
        content_paragraph_items += synopsis.paragraphs
        return docs.list_item(header, content_paragraph_items)

    def _list(self, items):
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_indent_spaces=0,
                                                    custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS))
