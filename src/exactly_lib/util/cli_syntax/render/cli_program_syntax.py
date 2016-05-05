from exactly_lib.help.utils.render import RenderingEnvironment, cross_reference_list, SectionContentsRenderer
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements.cli_program_syntax import CliProgramSyntaxDocumentation, \
    DescribedArgument, Synopsis
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs


class ProgramDocumentationSectionContentsRenderer(SectionContentsRenderer):
    def __init__(self, program: CliProgramSyntaxDocumentation):
        self.program = program

    def apply(self, environment: RenderingEnvironment) -> docs.SectionContents:
        return ProgramDocumentationRenderer(environment).apply(self.program)


class ProgramDocumentationRenderer:
    def __init__(self, environment: RenderingEnvironment):
        self.environment = environment
        self.cmd_line_syntax_renderer = CommandLineSyntaxRenderer()
        self.arg_in_description_renderer = ArgumentInArgumentDescriptionRenderer()

    def apply(self, program: CliProgramSyntaxDocumentation) -> docs.SectionContents:
        sections = []
        sections.append(self._synopsis_section(program))
        sections.append(self._description_section(program))
        sections.extend(self._options_sections(program.argument_descriptions()))
        return docs.SectionContents([docs.para(program.description().single_line_description)],
                                    sections)

    def _synopsis_section(self, program: CliProgramSyntaxDocumentation) -> docs.Section:
        return docs.section(docs.text('SYNOPSIS'),
                            [self._list(map(self._synopsis_list_item, program.synopsises()))])

    def _description_section(self, program: CliProgramSyntaxDocumentation) -> docs.Section:
        description = program.description()
        return docs.Section(docs.text('DESCRIPTION'),
                            description.rest)

    def _options_sections(self, argument_descriptions: list) -> list:
        if not argument_descriptions:
            return []
        l = self._list(map(self._arg_description_list_item, argument_descriptions))

        return [docs.section(docs.text('OPTIONS'),
                             [l])]

    def _arg_description_list_item(self, argument: DescribedArgument) -> lists.HeaderContentListItem:
        header = docs.text(self.arg_in_description_renderer.visit(argument.argument))
        return lists.HeaderContentListItem(header, self._arg_description_list_item_contents(argument))

    def _arg_description_list_item_contents(self, argument: DescribedArgument) -> list:
        ret_val = []
        ret_val.extend(argument.description)
        if argument.see_also:
            ret_val.append(docs.para('See also'))
            ret_val.append(cross_reference_list(argument.see_also, self.environment))
        return ret_val

    def _synopsis_list_item(self, synopsis: Synopsis) -> lists.HeaderContentListItem:
        header = self.cmd_line_syntax_renderer.apply(synopsis.command_line)
        content_paragraph_items = []
        if synopsis.maybe_single_line_description:
            content_paragraph_items.append(docs.para(synopsis.maybe_single_line_description))
        return lists.HeaderContentListItem(header, content_paragraph_items)

    def _list(self, items):
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_indent_spaces=0,
                                                    custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS))


class CommandLineSyntaxRenderer:
    def __init__(self):
        self.arg_usage_renderer = ArgumentUsageOnCommandLineRenderer()

    def apply(self, command_line: arg.CommandLine) -> docs.Text:
        components = []
        if command_line.prefix:
            components.append(command_line.prefix)
        arguments_str = ' '.join((map(self.arg_usage_renderer, command_line.argument_usages)))
        components.append(arguments_str)
        if command_line.suffix:
            components.append(command_line.suffix)
        return docs.text(' '.join(components))


class ArgumentUsageOnCommandLineRenderer(arg.ArgumentUsageVisitor):
    CHOICE_SEPARATOR = '|'

    def __init__(self):
        self._arg_renderer = ArgumentOnCommandLineRenderer()

    def visit_single(self, x: arg.Single) -> str:
        arg_str = self._arg_renderer.visit(x.argument)
        if x.multiplicity is arg.Multiplicity.OPTIONAL:
            return self._optional(arg_str)
        elif x.multiplicity is arg.Multiplicity.MANDATORY:
            return arg_str
        elif x.multiplicity is arg.Multiplicity.ZERO_OR_MORE:
            return self._and_more(self._optional(arg_str))
        elif x.multiplicity is arg.Multiplicity.ONE_OR_MORE:
            return self._and_more(arg_str)
        else:
            raise ValueError('Invalid %s: %s' % (str(arg.Multiplicity), str(x.multiplicity)))

    def visit_choice(self, x: arg.Choice) -> str:
        arg_str = self.CHOICE_SEPARATOR.join(map(self._arg_renderer, x.arguments))
        if x.multiplicity is arg.Multiplicity.OPTIONAL:
            return self._optional(arg_str)
        elif x.multiplicity is arg.Multiplicity.MANDATORY:
            return self._mandatory_group(arg_str)
        elif x.multiplicity is arg.Multiplicity.ZERO_OR_MORE:
            return self._and_more(self._optional(arg_str))
        elif x.multiplicity is arg.Multiplicity.ONE_OR_MORE:
            return self._and_more(self._mandatory_group(arg_str))
        else:
            raise ValueError('Invalid %s: %s' % (str(arg.Multiplicity), str(x.multiplicity)))

    def _multiplicity(self, arg_str: str, multiplicity: arg.Multiplicity) -> str:
        return arg_str if multiplicity is arg.Multiplicity.MANDATORY else '[' + arg_str + ']'

    @staticmethod
    def _optional(arg_str) -> str:
        return '[' + arg_str + ']'

    @staticmethod
    def _mandatory_group(arg_str) -> str:
        return '(' + arg_str + ')'

    @staticmethod
    def _and_more(arg_str) -> str:
        return arg_str + '...'


class ArgumentOnCommandLineRenderer(arg.ArgumentVisitor):
    def visit_constant(self, x: arg.Constant) -> str:
        return x.name

    def visit_named(self, x: arg.Named) -> str:
        return x.name

    def visit_option(self, x: arg.Option) -> str:
        if x.short_name:
            option_str = x.short_name
        else:
            option_str = x.long_name
        if x.argument:
            return option_str + ' ' + x.argument
        else:
            return option_str


class ArgumentInArgumentDescriptionRenderer(arg.ArgumentVisitor):
    def visit_constant(self, x: arg.Constant) -> str:
        return x.name

    def visit_named(self, x: arg.Named) -> str:
        return x.name

    def visit_option(self, x: arg.Option) -> str:
        ret_val = []
        if x.short_name:
            ret_val.append(x.short_name)
        if x.long_name:
            if ret_val:
                ret_val.append(', ')
            ret_val.append(x.long_name)
        if x.argument:
            ret_val.append(' ')
            ret_val.append(x.argument)
        return ''.join(ret_val)
