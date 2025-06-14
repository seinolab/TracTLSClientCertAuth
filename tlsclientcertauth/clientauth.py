import re
from trac.core import Component, implements
from trac.web.api import IRequestFilter

class TLSClientCertAuth(Component):
    implements(IRequestFilter)

    def pre_process_request(self, req, handler):
        dn = req.environ.get("SSL_CLIENT_S_DN", "")
        match = re.search(r"CN=([^,@]+)", dn)
        if match:
            req.environ['REMOTE_USER'] = match.group(1)
        else:
            req.environ.pop('REMOTE_USER', None)  # 念のため削除
        return handler

    def post_process_request(self, req, template, data, content_type):
        return template, data, content_type
