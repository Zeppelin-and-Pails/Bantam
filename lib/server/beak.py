"""
Beak

The server for Bantam

@category   Utility
@version    $ID: 1.1.1, 2016-02-02 17:00:00 CST $;
@author     KMR
@licence    GNU GPL v.3
"""

import markdown
import os, re
import json
import stat
import mimetypes

from gevent.pywsgi import WSGIServer

class Beak:
    def __init__(self, config):
        self.conf = config
        self.log = config['logger']

        self.words = config['words'].replace('{dir}', config['base_path'])
        self.pages = config['pages'].replace('{dir}', config['base_path'])
        self.files = config['files'].replace('{dir}', config['base_path'])
        self.errors = config['errors'].replace('{dir}', config['base_path'])
        self.theme = config['theme'].replace('{dir}', config['base_path'])
        self.templates = config['templates'].replace('{dir}', config['base_path'])

    def serve(self):
        self.log.info('Serve called')
        server = WSGIServer((self.conf['HOST'], self.conf['PORT']), self.app)
        server.serve_forever()

    def app(self, env, sr):
        body = None
        self.headers = []
        status = '200 OK'
        if (env['REQUEST_METHOD'] == 'GET'):
            body = self.get(env['PATH_INFO'], params = env['QUERY_STRING'])
        else:
            body = self.render(self.errors + '404.html')
            status = '404 Not Found'

        sr(status, self.headers)
        return body

    def get(self, path, **kwargs):
        self.log.info('GET called with path ' + path)
        path = path.strip('/') or 'index'
        is_file = re.search(r'\.(?!htm)', path)
        if kwargs['params']:
            get_params = kwargs['params']

        if is_file:
            if re.search(r'/\d{3}(?=.)', path) and re.match(r'^errors', path):
                path = re.split(r'/', path)
                path = self.errors + path[-1]
            elif re.match(r'^theme', path):
                path = re.split(r'/', path)
                path = self.theme + path[-1]
            else:
                path = self.files + path

            try:
                self.log.info('Serving file with path ' + path)
                return self.serve_file(path)
            except Exception as e:
                self.log.info('Failed to serve file: ' + e)
                return self.render(self.errors + '404.html')

        else:
            self.log.info('Page requested')
            path = path.strip('.html').strip('.htm')
            self.headers = [('Content-Type', 'text/html')]
            self.log.info('path')
            try:
                cont_path = self.words + path
                if self.conf['use_templates']:
                    cont_path = cont_path + '.json'
                else:
                    cont_path = cont_path + '.md'
                html_path = self.pages + path + '.html'

                changed = False
                if os.path.isfile(html_path) and os.path.isfile(cont_path):
                    stat_c = os.stat(cont_path)
                    stat_h = os.stat(html_path)
                    changed = stat_c[stat.ST_MTIME] < stat_h[stat.ST_MTIME]

                if os.path.isfile(html_path) and not changed:
                    self.log.info('Page found, attempting to render')
                    return self.render(html_path)

                elif os.path.isfile(cont_path):
                    self.log.info('New or updated content found, attempting to load')
                    with open(cont_path, 'r') as content, open(html_path, 'w', encoding='utf-8') as html_file:
                        raw = content.read()
                        if self.conf['use_template']:
                            html = self.load_template(raw, path)
                        else:
                            html = markdown.markdown(raw)

                        if self.conf['use_theme']:
                            html = self.load_theme(html)
                        html_file.write(html)
                        return self.render(html_path)
                else:
                    return self.render(self.errors + '404.html')
            except:
                return self.render(self.errors + '404.html')

    def render(self, path):
        self.headers.append(('Content-Type', 'text/html'))
        if os.path.isfile(path):
            with open(path, 'r') as output:
                return [bytes(output.read(), 'utf-8')]
        else:
            return self.render(self.errors + '404.html')

    def serve_file(self, path, chunk=0):
        if os.path.isfile(path):
            stat_result = os.stat(path)
            size = stat_result[stat.ST_SIZE]
            self.set_file_headers(path, stat_result[stat.ST_MTIME])
            entire_file = False
            if (size < chunk):
                chunk = size
                entire_file = True
            with open(path, 'rb') as output:
                if chunk and not entire_file:
                    yield output.read(chunk)
                else:
                    yield output.read()
        else:
            yield self.render(self.errors + '404.html')

    def set_file_headers(self, path, modified):
        self.headers.append(("Accept-Ranges", "bytes"))
        if modified:
            self.headers.append(("Last-Modified", modified))

        content_type = self.get_content_type(path)
        if content_type:
            self.headers.append(("Content-Type", content_type))

    def get_content_type(self, path):
        mime_type, encoding = mimetypes.guess_type(path)
        if encoding == "gzip":
            return "application/gzip"
        elif encoding is not None:
            return "application/octet-stream"
        elif mime_type is not None:
            return mime_type
        else:
            # if mime_type not detected, use application/octet-stream
            return "application/octet-stream"

    def load_template(self, raw, path):
        path = re.sub('/\w*$', '', path)
        if path and os.path.isfile(self.templates + path + '.m'):
            path = self.templates + path + '.m'
        elif os.path.isfile(self.templates + 'default.m'):
            path = self.templates + 'default.m'
        else:
            return markdown.markdown(raw)

        with open(path + '.m') as template:
            html = template.read()
        content = json.loads(raw)
        for k, v in content.items():
            if k == 'markdown':
                html.replace('{{body}}', markdown.markdown(v))
            else:
                # Crazy multi {} results in {{key}}
                html.replace('{{{{{}}}}}'.format(k), v)

        return html

    def load_theme(self, html):
        if os.path.isfile(self.theme):
            with open(self.theme) as theme:
                html = theme.read().replace('{{body}}', html)
        return html