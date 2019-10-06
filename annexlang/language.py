from .components import ProtocolStep


class HTTPRequest(ProtocolStep):
    yaml_tag = '!http-request'
    method = ""
    url = ""
    parameters = ""
    type = "http_request"
    id_above = True

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.text_above = " ".join((self.method, self.url, )).strip()
        self.text_below = self.parameters
        if hasattr(self, 'reply_to'):
            self.dest = self.reply_to.src
            self.src = self.reply_to.dest
        self._affecting_nodes = [
            self.get_pos(self.src.column, self.line),
            self.get_pos(self.dest.column, self.line)
        ]

    @property
    def affected_parties(self):
        yield self.src
        yield self.dest
    
    def tikz_arrows(self):
        src = self.get_pos(self.src.column, self.line)
        dest = self.get_pos(self.dest.column, self.line)
        return fr"""%% draw {self.type}
        \draw[annex_{self.type}{self.tikz_extra_style}] ({src}) to {self.tikz_above} {self.tikz_below} ({dest});"""

    @property
    def height(self):
        if self.tikz_above and self.tikz_below:
            return "4ex" + ("+2ex" * len(self.lines_below)), "north,yshift=3ex"
        elif self.tikz_above:
            return "4ex", "south,yshift=-1ex"
        elif self.tikz_below:
            return "2ex" + ("+2ex" * len(self.lines_below)), "north,yshift=1ex"
        else:
            return "1ex", "center"

    @property
    def svg_height(self):
        lh = self.protocol.options['line_height']
        if self.tikz_above and self.tikz_below:
            return 1 + lh + (lh * len(self.lines_below))
        elif self.tikz_above:
            return 1 + lh
        elif self.tikz_below:
            return 1 + (lh * len(self.lines_below))
        else:
            return 1

    def svg_draw(self, d):
        id = self.annexid
        print (f"In element {id}")
        group = d.add(d.g(id=id))
        
        lh = self.protocol.options['line_height']
        fs = self.protocol.options['font_size']
        
        center = int((self.svg_get_x_from_column(self.src.column) + self.svg_get_x_from_column(self.dest.column))/2)
        top = self.svg_get_y()

        # draw text above, if needed
        if self.tikz_above:
            paragraph = group.add(d.g(font_size=self.protocol.options['font_size']))
            x = center
            y = top + fs
            print ("above:", self.text_above)
            paragraph.add(d.text(self.text_above, ([x], [y]), text_anchor="middle"))
            
            top += lh

        # draw arrow, takes up half a unit
        start = (self.svg_get_x_from_column(self.src.column), top + 0.5)
        end = (self.svg_get_x_from_column(self.dest.column), top + 0.5)
        group.add(d.line(start=start, end=end, class_="annex_" + self.type, marker_end="url(#arrow)"))
        top += 1

        # draw text below, if needed
        if self.tikz_below:
            paragraph = group.add(d.g(font_size=self.protocol.options['font_size']))
            for line in self.lines_below:
                print ('below: ' + line, top)
                x = center
                y = top + fs
                paragraph.add(d.text(line, ([x], [y]), text_anchor="middle"))
                top += lh


class XHRRequest(HTTPRequest):
    yaml_tag = '!xhr-request'
    type = "xhr_request"


class HTTPResponse(HTTPRequest):
    yaml_tag = '!http-response'
    code = ""
    headers = ""
    type = "http_response"
    
    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.text_above = " ".join((self.code, self.headers, )).strip()
        if not self.text_above and not self.skip_number:
            self.text_above = 'Response'
        self.text_below = self.parameters


class XHRResponse(HTTPResponse):
    yaml_tag = '!xhr-response'
    type = "xhr_response"


class Websocket(HTTPRequest):
    yaml_tag = '!websocket'
    type = "websocket"

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.text_above = "WebSocket"
        self.text_below = self.parameters
    

class HTTPRequestResponse(HTTPRequest):
    yaml_tag = '!http-request-response'
    type = "request_response"
    type_above = 'http_request'
    type_below = 'http_response'

    def tikz_arrows(self):
        src = self.get_pos(self.src.column, self.line)
        dest = self.get_pos(self.dest.column, self.line)
        return fr"""%% draw {self.type}
        \draw[annex_{self.type_above},transform canvas={{yshift=0.25ex}}{self.tikz_extra_style}] ({src}) to {self.tikz_above} ({dest});
        \draw[annex_{self.type_below},transform canvas={{yshift=-0.25ex}}{self.tikz_extra_style}] ({dest}) to {self.tikz_below} ({src});"""


class XHRRequestResponse(HTTPRequestResponse):
    yaml_tag = '!xhr-request-response'
    type = "xhr_request_response"
    type_above = 'xhr_request'
    type_below = 'xhr_response'


class HTTPResponseRequest(HTTPRequest):
    yaml_tag = '!http-response-request'
    type = "response_request"
    type_above = 'http_response'
    type_below = 'http_request'

    def tikz_arrows(self):
        src = self.get_pos(self.src.column, self.line)
        dest = self.get_pos(self.dest.column, self.line)
        return fr"""%% draw {self.type}
        \draw[annex_{self.type_above},transform canvas={{yshift=0.25ex}}{self.tikz_extra_style}] ({dest}) to {self.tikz_above} ({src});
        \draw[annex_{self.type_below},transform canvas={{yshift=-0.25ex}}{self.tikz_extra_style}] ({src}) to {self.tikz_below} ({dest});"""

    
class XHRResponseRequest(HTTPResponseRequest):
    yaml_tag = '!xhr-request-response'
    type = "xhr_request_response"
    type_above = 'xhr_request'
    type_below = 'xhr_response'


class PostMessage(ProtocolStep):
    yaml_tag = '!postmessage'
    body = ""
    comment = ""
    id_above = True
    text_style = "annex_postmessage_text"

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.text_above = self.body
        self.text_below = self.comment
        self._affecting_nodes = [
            self.get_pos(self.src.column, self.line),
            self.get_pos(self.dest.column, self.line)
        ]

    @property
    def affected_parties(self):
        yield self.src
        yield self.dest
    
    def tikz_arrows(self):
        src = self.get_pos(self.src.column, self.line)
        dest = self.get_pos(self.dest.column, self.line)
        return fr"""%% draw postmessage
        \draw[annex_postmessage{self.tikz_extra_style}] ({src}) to {self.tikz_above} {self.tikz_below} ({dest});"""

#    def height(self):
#        if self.tikz_above:
#            return "4ex", "south,yshift=-1ex"
#        else:
#            return "1ex", "center"
    @property
    def height(self):
        if self.tikz_above and self.tikz_below:
            return "4ex" + ("+2ex" * len(self.lines_below)), "north,yshift=3ex"
        elif self.tikz_above:
            return "4ex", "south,yshift=-1ex"
        elif self.tikz_below:
            return "2ex" + ("+2ex" * len(self.lines_below)), "north,yshift=1ex"
        else:
            return "1ex", "center"
        
    @property
    def svg_height(self):
        lh = self.protocol.options['line_height']
        if self.tikz_above and self.tikz_below:
            return 1 + lh + (lh * len(self.lines_below))
        elif self.tikz_above:
            return 1 + lh
        elif self.tikz_below:
            return 1 + (lh * len(self.lines_below))
        else:
            return 1

    def svg_draw(self, d):
        id = self.annexid
        print (f"In element {id}")
        group = d.add(d.g(id=id))
        
        lh = self.protocol.options['line_height']
        fs = self.protocol.options['font_size']
        
        center = int((self.svg_get_x_from_column(self.src.column) + self.svg_get_x_from_column(self.dest.column))/2)
        top = self.svg_get_y()

        # draw text above, if needed
        if self.tikz_above:
            paragraph = group.add(d.g(font_size=self.protocol.options['font_size']))
            x = center
            y = top + fs
            print ("above:", self.text_above)
            paragraph.add(d.text(self.text_above, ([x], [y]), text_anchor="middle"))
            
            top += lh

        # draw arrow, takes up half a unit
        start = (self.svg_get_x_from_column(self.src.column), top + 0.5)
        end = (self.svg_get_x_from_column(self.dest.column), top + 0.5)
        group.add(d.line(start=start, end=end, class_="annex_postmessage"))#, marker_end=marker.get_funciri()))
        top += 1

        # draw text below, if needed
        if self.tikz_below:
            paragraph = group.add(d.g(font_size=self.protocol.options['font_size']))
            for line in self.lines_below:
                print ('below: ' + line, top)
                x = center
                y = top + fs
                paragraph.add(d.text(line, ([x], [y]), text_anchor="middle"))
                top += lh

class Action(ProtocolStep):
    yaml_tag = '!action'

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.node_name = self.create_affecting_node_name()

    def tikz(self):
        pos = self.get_pos(self.party.column, self.line)
        text = self.tex_id + self.contour(self.label)
        out = fr"""\node[annex_action,name={self.node_name}{self.tikz_extra_style}] at ({pos}) {{{text}}};"""
        return out

    @property
    def height(self):
        h = 1 + 2 * len(self.label.split("\\\\"))
        return f"{h}ex", "center"

    @property
    def svg_height(self):
        return 1

    
class ScriptAction(Action):
    yaml_tag = '!script-action'
    data = ""
    label = ""
    id_above = False

    def _init(self, *args, **kwargs):
        self.party = self.src
        super()._init(*args, **kwargs)
    
    def tikz_arrows(self):
        direction = "east" if self.src.column < self.dest.column else "west"
        src = self.get_pos(self.src.column, self.line)
        dest = self.get_pos(self.dest.column, self.line)
        self.text_above = self.data
        rev = "_reversed" if getattr(self, 'reversed', False) else ''
        return fr"""%% draw script action arrow
        \draw[annex_script_action_arrow{rev}{self.tikz_extra_style}] ({self.node_name}.{direction}) to  {self.tikz_above} ({dest});"""

    @property
    def height(self):
        return "4ex", "center"
    
    @property
    def affected_parties(self):
        yield self.party
        yield self.src
        yield self.dest

    @property
    def svg_height(self):
        return 4
        

class EndParty(ProtocolStep):
    yaml_tag = '!end-party'
    skip_number = True
    type = 'end_party'
    endsparty = True

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.node_name = self.create_affecting_node_name()
    
    def tikz(self):
        pos = self.get_pos(self.party.column, self.line)
        text = self.party.name
        out = fr"""\node[name={self.node_name},annex_{self.type}_box,{self.party.style}] at ({pos}) {{{text}}};"""
        return out

    @property
    def height(self):
        return "5ex", "center"

    def svg_draw(self, d):
        fs = self.protocol.options['font_size']
        col = self.svg_get_x_from_column(self.party.column)
        y = self.svg_get_y() + fs
        d.add(d.text(self.party.name, ([col], [y]), text_anchor="middle", font_size=self.protocol.options['font_size'], class_="annex_" + self.type))

    @property
    def svg_height(self):
        return 1


class StartParty(EndParty):
    yaml_tag = '!start-party'
    skip_number = True
    type = 'start_party'
    endsparty = False
    startsparty = True
    lifeline_segments = []

    def tikz_arrows(self):
        out = ""
        for segment in self.lifeline_segments:
            if segment[0] % 2 == 1:
                node_above = self.get_pos(self.party.column, segment[0] // 2)
                node_below = self.get_pos(self.party.column, segment[0] // 2 + 1)
                out += fr"""\node[inner sep=0] ({node_above}-half) at ($({node_above})!0.5!({node_below})$) {{}};"""
                src = fr"""{node_above}-half"""
            else:
                src = self.get_pos(self.party.column, segment[0] // 2)
            if segment[1] % 2 == 1:
                node_above = self.get_pos(self.party.column, segment[1] // 2)
                node_below = self.get_pos(self.party.column, segment[1] // 2 + 1)
                out += fr"""\node[inner sep=0] ({node_above}-half) at ($({node_above})!0.5!({node_below})$) {{}};"""
                dest = fr"""{node_above}-half"""
            else:
                dest = self.get_pos(self.party.column, segment[1] // 2)
            out += fr"""\draw[{segment[2]}] ({src}) -- ({dest});"""
        return out

    def svg_draw(self, d):
        super().svg_draw(d)
        col = self.svg_get_x_from_column(self.party.column)
        
        # draw the lifeline(s)
        out = ""
        for segment in self.lifeline_segments:
            
            starty = self.svg_get_y(1+segment[0] // 2)
            if segment[0] % 2 == 1:
                starty += self.protocol.svg_line_maxheights.get(1+segment[0] // 2, 0) // 2
            start=(col, starty)

            endy = self.svg_get_y(segment[1] // 2)
            if segment[0] % 2 == 1:
                endy += self.protocol.svg_line_maxheights.get(segment[1] // 2, 0) // 2
            end=(col, endy)
                        
            d.add(d.line(start=start, end=end, class_=segment[2]))#, marker_end=marker.get_funciri()))


class DummyParty(ProtocolStep):
    yaml_tag = '!dummy-party'
    skip_number = True
    dummyparty = True

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.node_name = self.create_affecting_node_name()
    
#    def tikz(self):
#        pos = self.get_pos(self.party.column, self.line)
#        text = self.party.name
#        out = fr"""\node[name={self.node_name},annex_{self.type}_box,{self.party.style}] at ({pos}) {{{text}}};"""
#        return out
#
#    @property
#    def height(self):
#        return "5ex", "center"


class OpenWindowStartParty(StartParty):
    yaml_tag = '!open-window-start-party'
    id_above = True
    skip_number = False

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.party = self.dest
    
    def tikz_arrows(self):
        direction = "east" if self.src.column > self.dest.column else "west"
        src = self.get_pos(self.src.column, self.line)
        self.text_above = "open"
        out = fr"""%% draw open window arrow
        \draw[annex_open_window_start_party_arrow{self.tikz_extra_style}] ({src}) to  {self.tikz_above} ({self.node_name}.{direction});"""
        out += super().tikz_arrows()
        return out
    
    @property
    def height(self):
        return "6ex", "center,yshift=1ex"
    
    @property
    def affected_parties(self):
        yield self.src
        yield self.dest


class CloseWindowEndParty(EndParty):
    yaml_tag = '!close-window-end-party'
    id_above = True
    skip_number = False

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.party = self.dest
    
    def tikz_arrows(self):
        direction = "east" if self.src.column > self.dest.column else "west"
        src = self.get_pos(self.src.column, self.line)
        self.text_above = "close"
        out = fr"""%% draw close window arrow
        \draw[annex_close_window_end_party_arrow{self.tikz_extra_style}] ({src}) to  {self.tikz_above} ({self.node_name}.{direction});"""
        out += super().tikz_arrows()
        return out
    
    @property
    def height(self):
        return "6ex", "center,yshift=1ex"
    
    @property
    def affected_parties(self):
        yield self.src
        yield self.dest

