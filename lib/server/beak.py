import tornado.web
import markdown
import re, os

class Beak(tornado.web.RequestHandler):
    def initialize(self, config):
        self.conf = config
        self.log = config['LOGGER']

        self.words = config['WORDS'].replace('{dir}', config['BASE_PATH'])
        self.pages = config['PAGES'].replace('{dir}', config['BASE_PATH'])
        self.files = config['FILES'].replace('{dir}', config['BASE_PATH'])
        self.errors = config['ERRORS'].replace('{dir}', config['BASE_PATH'])

    def get(self, *args, **kwargs):
        self.log.info('GET called with path ' + args[0])
        path = args[0].strip('/')
        is_file = re.search(r'\.', path)
        
        get_params = self.request.arguments

        if is_file:
            if re.search(r'/\d{3}(?=.)', path) and re.match(r'errors', path):
                path = re.split(r'/', path)
                try:
                    self.render(self.errors + path[-1])
                except:
                    pass
            else:
                self.render(self.files + path)
        else:
            self.log.info('Page requested')
            try:
                if os.path.isfile(self.pages + path + '.html'):
                    self.log.info('Page found, attempting to render')
                    self.render(self.pages + path + '.html')
                elif os.path.isfile(self.words + path + '.md'):
                    self.log.info('Page not found, attempting to load from markdown')
                    with open(self.words + path + '.md', 'r') as md_file, \
                         open(self.pages + path + '.html', 'w', encoding='utf-8') as html_file:
                        raw_md = md_file.read()
                        html = markdown.markdown(raw_md)
                        html_file.write(html)
                        self.render(self.pages + path + '.html')
            except:
                self.render(self.errors + '404.html')

