import http.server
import json
import socketserver
import time


class TokenHandler(http.server.SimpleHTTPRequestHandler):
    def fake_token_info(self, token):
        '''
        If the token is a number, it will pretend
        the token is valid and belongs to an user with such personal number.

        If the token is GODGODGOD, it will pretend the token is valid
        and belongs to a client that can read everything.

        If the token is anything different, it will pretend it is not valid.
        '''
        scope = ['cvut:utvs:general:read']
        try:
            itoken = int(token)
            scope += ['cvut:utvs:enrollments:by-role']
        except ValueError:
            if token == 'GODGODGOD':
                scope += ['cvut:utvs:enrollments:all']
            else:
                return {'error': 'invalid',
                        'error_description': 'Token is not valid'}

        data = {
            'exp': int(time.time()) + 9999,
            'scope': scope,
        }
        try:
            data['user_name'] = itoken
        except NameError:
            pass
        return data

    def fake_user_info(self, username):
        '''
        Return an user info with personal number same as username if number
        '''
        data = {'username': username}
        try:
            pnum = int(username)
            data['personalNumber'] = pnum
        except ValueError:
            pass
        return data

    def do_GET(self):
        '''
        Respond to a GET request
        '''
        self.send_response(200)
        self.send_header('Content-Type', 'application/json;charset=UTF-8')
        self.end_headers()
        if self.path.startswith('/token'):
            token = self.path.split('=')[-1]
            data = self.fake_token_info(token)
        else:
            username = self.path.split('/')[-1]
            data = self.fake_user_info(username)
        self.wfile.write(json.dumps(data).encode())


def serve_forever(port=8080):
    tokenserver = socketserver.TCPServer(('', port), TokenHandler)
    tokenserver.serve_forever()
