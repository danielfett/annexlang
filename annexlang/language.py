from .components import ProtocolStep


class HTTPRequest(ProtocolStep):
    yaml_tag = '!http-request'
    method = ""
    url = ""
    parameters = ""
    type = "request"
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
        return fr"""%% draw http {self.type}
        \draw[annex_http_{self.type}] ({src}) to {self.tikz_above} {self.tikz_below} ({dest});"""

    @property
    def height(self):
        if self.tikz_above and self.tikz_below:
            return "6ex", "center"
        elif self.tikz_above:
            return "4ex", "south,yshift=-1ex"
        elif self.tikz_below:
            return "4ex", "north,yshift=1ex"
        else:
            return "1ex", "center"
    

class HTTPResponse(HTTPRequest):
    yaml_tag = '!http-response'
    code = ""
    headers = ""
    type = "response"
    id_above = True
    
    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.text_above = " ".join((self.code, self.headers, )).strip()
        if not self.text_above:
            self.text_above = 'Response'
        self.text_below = self.parameters
        

class Action(ProtocolStep):
    yaml_tag = '!action'

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        self.node_name = self.create_affecting_node_name()

    def tikz(self):
        pos = self.get_pos(self.party.column, self.line)
        text = self.tex_id + self.contour(self.label)
        out = fr"""\node[annex_action,name={self.node_name}] at ({pos}) {{{text}}};"""
        return out

    @property
    def height(self):
        return "3ex", "center"

    
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
        return fr"""%% draw open window arrow
        \draw[annex_script_action_arrow{rev}] ({self.node_name}.{direction}) to  {self.tikz_above} ({dest});"""

    @property
    def height(self):
        return "4ex", "center"
    
    @property
    def affected_parties(self):
        yield self.party
        yield self.src
        yield self.dest
        

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


class StartParty(EndParty):
    yaml_tag = '!start-party'
    skip_number = True
    type = 'start_party'
    endsparty = False
    startsparty = True
     
    def tikz_arrows(self):
        src = self.get_pos(self.party.column, self.line)
        dest = self.get_pos(self.party.column, self.end.line)
        out = r"""\draw[annex_lifeline] (%(src)s) -- (%(dest)s);""" % {
            'src': src,
            'dest': dest,
        }
        return out


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
        \draw[annex_open_window_start_party_arrow] ({src}) to  {self.tikz_above} ({self.node_name}.{direction});"""
        out += super().tikz_arrows()
        return out
    
    @property
    def height(self):
        return "6ex", "center,yshift=1ex"
    
    @property
    def affected_parties(self):
        yield self.src
        yield self.dest
