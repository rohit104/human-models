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
        ids = ids.fetch(100)
        chosen_id = random.choice(ids)
        tokens = models.Token.get(chosen_id).token

        num_words = 0
        new_token = ""
        for mm in re.finditer(r'(\w+|\W+)', tokens):
            if re.match(r'\w+', mm.group(0)):
                new_token += '<a href="javascript:chooseWord(%d);" class="tag" id="word_%d">%s</a>' % (num_words, num_words, mm.group(0))
                num_words += 1
            else:
                new_token += mm.group(0)

        self.response.out.write(new_token)

class MainPage(webapp.RequestHandler):
    def get(self):
        user_id = self.request.get("user_id")
        if not user_id:
            path = os.path.join(os.path.dirname(__file__), 'invalid_userid.html')
            self.response.out.write(template.render(path, {}))
            return

        num_finished = 0

        template_values = {
            'num_finished' : num_finished + 1,
            'user_id' : user_id
        }

        path = os.path.join(os.path.dirname(__file__), 'tokens.html')
        self.response.out.write(template.render(path, template_values))

class RecordResult(webapp.RequestHandler):
    def post(self):
        document_id = int(self.request.get("document_id"))
        topic = int(self.request.get("topic"))
        word_string = self.request.get("word_string").lower()

        tag = models.Tag()
        tag.topic = topic
        tag.word = int(self.request.get("word"))
        tag.user_id = int(self.request.get("user_id"))
        tag.document_id = document_id
        tag.word_string = word_string
        tag.put()
        
        document_stat = models.DocumentStats.gql("WHERE document_id = %d and topic = %d" % 
                                                 (document_id, topic)).get()
        if not document_stat:
            document_stat = models.DocumentStats()
            document_stat.document_id = document_id
            document_stat.topic = topic
            document_stat.count = 1
        else:
            document_stat.count = document_stat.count + 1
        document_stat.put()

        topic_stat = models.TopicStats.gql("WHERE topic = %d and word = '%s'" % (topic, word_string)).get()
        if not topic_stat:
            topic_stat = models.TopicStats()
            topic_stat.topic = topic
            topic_stat.word = word_string
            topic_stat.count = 1
        else:
            topic_stat.count = topic_stat.count + 1
        topic_stat.put()

        self.redirect('/?user_id=%s' % self.request.get("user_id"))

application = webapp.WSGIApplication([('/tokens.html', MainPage),
                                      ('/token_rpc', TokenFetcher),
                                      ('/submit', RecordResult)],
                                     debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
