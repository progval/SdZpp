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
        elif response['content-type'].startswith('text/css') or \
                response['content-type'].startswith('application/javascript'):
            response.content = response.content.replace(' ', '').replace('\n', '').replace('\t', '')
        return response
