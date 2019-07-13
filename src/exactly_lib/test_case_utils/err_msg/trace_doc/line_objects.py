from exactly_lib.common.report_rendering import trace_doc
from exactly_lib.common.report_rendering.trace_doc import TraceDoc


def of_pre_formatted_text(text: str,
                          is_line_ended: bool = False) -> TraceDoc:
    return trace_doc.PreFormattedDoc(text, is_line_ended)
