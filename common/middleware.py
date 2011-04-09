class MinifyMiddleware:
    def process_response(self, request, response):
        # Yes, this function is not very pretty ;)
        if response['content-type'].startswith('text/html'):
            new_content = ''
            in_pre = False
            for char in response.content:
                if new_content.endswith('<pre'):
                    in_pre = True
                elif new_content.endswith('</pre>'):
                    in_pre = False
                if char in '\n\t' and not in_pre:
                    continue
                if char not in ' ' or new_content[-1] not in ' ' or in_pre:
                    new_content += char
            response.content = new_content
        elif response['content-type'].startswith('text/css'):
            response.content = response.content.replace('\n', '').replace('  ', ' ').replace(' } ', '}').replace(' { ', '{').replace(';}', '}').replace(': ', ':').replace('; ', ';')
            new_content = ''
            in_comment = False
            last_char = ''
            for char in response.content:
                if not in_comment and char == '*' and new_content.endswith('/'):
                    in_comment = True
                    new_content = new_content[0:-1]
                elif in_comment and char == '/' and last_char == '*':
                    in_comment = False
                    new_content = new_content[0:-1]
                elif not in_comment:
                    new_content += char
                else:
                    last_char = char
            response.content = new_content
            response['Expires'] = 'max-age=1500'
            response['Cache-Control'] = 'max-age'
        elif response['content-type'].startswith('application/javascript'):
            new_content = ''
            for char in response.content:
                if char in '\n\t':
                    continue
                if char != ' ' or new_content[-1] != ' ':
                    new_content += char
            new_content = new_content.replace(' {', '{')
            response.content = new_content
            response['Expires'] = 'max-age=1500'
            response['Cache-Control'] = 'max-age'
        response['Content-Length'] = len(response.content)
        return response
