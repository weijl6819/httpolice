# -*- coding: utf-8; -*-

from httpolice import common, header_view, parse, syntax
from httpolice.common import Unparseable
from httpolice.known import tc


class Message(common.ReportNode):

    self_name = 'msg'

    def __init__(self, version, header_entries,
                 body=None, trailer_entries=None, raw=None):
        super(Message, self).__init__()
        self.version = version
        self.header_entries = header_entries
        self.body = body
        self.trailer_entries = trailer_entries
        self.raw = raw
        self.headers = header_view.HeadersView(self)


def parse_chunked(msg, state):
    data = []
    try:
        chunk = syntax.chunk.parse(state)
        while chunk:
            data.append(chunk)
            chunk = syntax.chunk.parse(state)
        trailers = syntax.trailer_part.parse(state)
        syntax.crlf.parse(state)
    except parse.ParseError, e:
        msg.complain(1005, error=e)
        msg.body = Unparseable
        return False
    else:
        msg.body = ''.join(data)
        msg.trailer_entries = trailers
        return True


def decode_transfer_coding(msg, coding):
    if coding == tc.chunked:
        # The outermost chunked has already been peeled off at this point.
        msg.complain(1002)
        msg.body = Unparseable
    else:
        msg.complain(1003, coding=coding)
        msg.body = Unparseable
