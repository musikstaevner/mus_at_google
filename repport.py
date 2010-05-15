import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from datamodel import ElevInfo

class MainPage(webapp.RequestHandler):
    def get(self):
        elevInfo_query = ElevInfo.all().order('-TilmeldtDate')
        elevInfo = elevInfo_query.fetch(9999)
	
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
	
	tilmeldt_count = '123'
	betalt_count = 12
        template_values = {
            'elevInfo': elevInfo,
            'tilmeldt_count': tilmeldt_count,
            'betalt_count': betalt_count,
            }

        path = os.path.join(os.path.dirname(__file__), 'repport.html')
        self.response.out.write(template.render(path, template_values))



class Guestbook(webapp.RequestHandler):
    def post(self):
        greeting = Greeting()

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', Guestbook)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
