from exactly_lib.util.command_line_syntax.elements import argument
from exactly_lib.util.command_line_syntax.elements.cl_syntax import CommandLine
from exactly_lib.util.textformat.structure import structures as docs


class ProgramDocumentationRenderer:
    def __init__(self):
        self.cmd_line_syntax_renderer = CommandLineSyntaxRenderer()

    def apply(self, command_line: CommandLine) -> docs.SectionContents:
        return docs.SectionContents([docs.para(self.cmd_line_syntax_renderer.apply(command_line))], [])


class CommandLineSyntaxRenderer:
    def __init__(self):
        self.arg_usage_renderer = ArgumentUsageOnCommandLineRenderer()

    def apply(self, command_line: CommandLine) -> docs.Text:
        components = [command_line.program_name] + list(map(self.arg_usage_renderer, command_line.argument_usages))
        return docs.text(' '.join(components))


class ArgumentUsageOnCommandLineRenderer(object):
    def __init__(self):
        self.argument_renderer = ArgumentOnCommandLineRenderer()

    def __call__(self, usage: argument.ArgumentUsage) -> str:
        arg_str = self.argument_renderer.visit(usage.argument)
        return arg_str if usage.usage_type is argument.ArgumentUsageType.MANDATORY else '[' + arg_str + ']'


class ArgumentOnCommandLineRenderer(argument.ArgumentVisitor):
    LONG_OPTION_PREFIX = '--'
    SHORT_OPTION_PREFIX = '-'

    def visit_as_is(self, x: argument.Constant):
        return x.name

    def visit_positional(self, x: argument.Positional):
        return x.name

    def visit_plain_option(self, x: argument.PlainOption):
        ret_val = ''
        if x.long_name:
            ret_val = self.LONG_OPTION_PREFIX + x.long_name
        else:
            ret_val = self.SHORT_OPTION_PREFIX + x.short_name
        if x.argument:
            return ret_val + ' ' + x.argument
        else:
            return ret_val

    def visit_syntax_element(self, x: argument.SyntaxElement):
        return x.name
