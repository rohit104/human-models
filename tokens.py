#!python

import re
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import models
import random
import logging
import time

class TokenFetcher(webapp.RequestHandler):
    def get(self):
        user_id = self.request.get("user_id")
        if not user_id:
            path = os.path.join(os.path.dirname(__file__), 'invalid_userid.html')
            self.response.out.write(template.render(path, {}))
            return

        ids = db.GqlQuery("select __key__ from Token")
        ids = ids.fetch(1000)
        chosen_id = random.choice(ids)
        tokens = models.Token.get(chosen_id).token

        ids = db.GqlQuery("select __key__ from Subtokenization where user_id = %d and index = 0" % int(user_id))
        ids = ids.fetch(20)
        num_finished = len(ids)

        if num_finished >= 20:
            key = db.GqlQuery("select * from Verification where user_id = %d" % int(user_id))
            if key.get() is None:
                key = int(user_id) * 31 - 17
            else:
                key = key.get().verification_code
            self.response.out.write("/token_finish?user_id=%s&key=%d" % (user_id, key))
            return

        num_words = 0
        new_token = ""
        for mm in re.finditer(r'(\w+|\W+)', tokens):
            if re.match(r'\w+', mm.group(0)):
                new_token += '<a href="javascript:paintWord(%d);" class="tag" id="word_%d">%s</a>' % (num_words, num_words, mm.group(0))
                num_words += 1
            else:
                new_token += mm.group(0)
        new_token += '<input type="hidden" id="num_words" value="%d">' % num_words
        new_token += '<input type="hidden" id="tokens" value="%s">' % tokens
        new_token += '<input type="hidden" id="num_finished" value="%d">' % (num_finished + 1)

        self.response.out.write(new_token)

class Finisher(webapp.RequestHandler):
    def get(self):
        user_id = self.request.get("user_id")
        if not user_id:
            path = os.path.join(os.path.dirname(__file__), 'invalid_userid.html')
            self.response.out.write(template.render(path, {}))
            return

        key = self.request.get("key")
        path = os.path.join(os.path.dirname(__file__), 'finished.html')
        self.response.out.write(template.render(path, {'user_id' : user_id, 'key' : key }))

class MainPage(webapp.RequestHandler):
    def get(self):
        user_id = self.request.get("user_id")
        if not user_id:
            path = os.path.join(os.path.dirname(__file__), 'invalid_userid.html')
            self.response.out.write(template.render(path, {}))
            return

        template_values = {
            'user_id' : user_id
        }

        path = os.path.join(os.path.dirname(__file__), 'tokens.html')
        self.response.out.write(template.render(path, template_values))

class RecordResult(webapp.RequestHandler):
    def get(self):
        user_id = int(self.request.get("user_id"))
        tags = self.request.get("tags")
        tokens = self.request.get("tokens")
        
        logging.info("Another submission: %d %s %s", user_id, tokens, tags)

        for ii in range(len(tags)):
            subtoken = models.Subtokenization()
            subtoken.token = tokens
            subtoken.index = ii
            subtoken.tag = int(tags[ii])
            subtoken.user_id = user_id
            subtoken.put()

        self.response.out.write("")


application = webapp.WSGIApplication([('/tokens.html', MainPage),
                                      ('/token_rpc', TokenFetcher),
                                      ('/token_submit', RecordResult),
                                      ('/token_finish', Finisher),
                                      ('/submit', RecordResult)],
                                     debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
