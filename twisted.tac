from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web import server
from server import app as application

resource = WSGIResource(reactor, reactor.getThreadPool(), application)
site = server.Site(resource)
reactor.listenTCP(5000, site)
reactor.run()

