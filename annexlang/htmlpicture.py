from scss import Compiler
from jinja2 import Environment, FileSystemLoader
import os

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

class HTMLPicture:

    options = {
        'html_enumerate': '<a href="#{prefix}-{identifier}" class="number">{number}</a>',
        'template': os.path.join(SCRIPT_PATH, 'html', 'template.html'),
        'stylesheet': os.path.join(SCRIPT_PATH, 'html', 'style.scss'),
        'prefix': 'annex',
    }
    
    def __init__(self, annexfile, unique_id):
        self.options.update(annexfile['options'])
        self.protocol = annexfile['protocol']
        self.protocol.init(self.options, unique_id)

    def get_css(self):
        scssfile = self.protocol.options['stylesheet']
        with open(scssfile, 'r') as f:
            scss = f.read().replace('UNIQUE_ID', self.protocol.unique_id)
        return Compiler(output_style='compressed').compile_string(scss)

        
    def dump(self, f):
        css = self.get_css()
        templatefile = self.protocol.options['template']
        file_loader = FileSystemLoader(os.path.dirname(templatefile))
        env = Environment(loader=file_loader)
        template = env.get_template(os.path.basename(templatefile))
        output = template.render(unique_id=self.protocol.unique_id, protocol=self.protocol, style=css)
        f.write(output)
