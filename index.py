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

class MainPage(webapp.RequestHandler):
    def get(self):
        user_id = self.request.get("user_id")
        if not user_id:
            path = os.path.join(os.path.dirname(__file__), 'invalid_userid.html')
            self.response.out.write(template.render(path, {}))
            return

        ## Figure out how many the user has done.
        user_finished = db.GqlQuery("select * from Tag where user_id = %d" % int(user_id))
        user_finished.fetch(100)
        num_finished = len([x.user_id for x in user_finished])

        if num_finished >= 20:
#             ver = models.Verification()
#             ver.user_id = 888
#             ver.verification_code = 8675309
#             ver.put()

            key = db.GqlQuery("select * from Verification where user_id = %d" % int(user_id))
            if key.get() is None:
                key = int(user_id) * 31 - 17
            else:
                key = key.get().verification_code
            path = os.path.join(os.path.dirname(__file__), 'finished.html')
            self.response.out.write(template.render(path, {'key' : key }))
            return
            

        vocab = set([x.rstrip('\n') for x in file("vocabulary")])

#        random.seed(8675309)

        ## NUKER !!!! ##
#        for ii in range(10000):
#            ids = db.GqlQuery("select __key__ from Tag")
#            db.delete(ids.fetch(200))
#            time.sleep(0.5)

        ids = db.GqlQuery("select __key__ from Document")
        ids = ids.fetch(100)
        chosen_id = random.choice(ids)
        document = models.Document.get(chosen_id)

        num_topics = 15
        top_topic_words = {}
        for tt in range(num_topics):
            logging.info("Querying for topic %d" % tt)
            topic_words = db.GqlQuery("select * from TopicStats where topic = %d order by count desc" % tt)
            top_topic_words[tt] = [x.word for x in topic_words.fetch(5)]
        
        empty_topics = set([x for x in top_topic_words.keys() if len(top_topic_words[x]) == 0])

        top_topics = db.GqlQuery("select * from DocumentStats where document_id = %d order by count desc" % document.document_id)

        top_topics = top_topics.fetch(num_topics)
        top_topics = [x.topic for x in top_topics]

        ## Find topics which don't have any assignments for this document
        other_topics = set(range(num_topics)) - set(top_topics)

        ## Remove empty topics
        other_topics = other_topics - set(empty_topics)

        ## Append the other topics to top topics
        top_topics = top_topics + list(other_topics)

        ## Add an empty topic if one exists
        if len(empty_topics) > 0:
            top_topics.append(empty_topics.pop())

        top_topic_words = [{'topic' : tt, 'words' : top_topic_words[tt]} for tt in top_topics]

        ## Get the already selected!
        already_selected = db.GqlQuery("select * from Tag where document_id = %d" % document.document_id)
        already_selected.fetch(1000)
        already_selected = [x.word for x in already_selected]
            
        template_values = {
            'num_finished' : num_finished + 1,
            'topics' : top_topic_words,
            'title' : document.title,
            'document_id' : document.document_id,
            'user_id' : user_id,
            'snippet' : document.body.replace("\\n", "\n"),
        }
        num_words = 0
        new_snippet = ""
        has_unchosen = False
        for mm in re.finditer(r'(\w+|\W+)', template_values['snippet']):
            if re.match(r'\w+', mm.group(0)):
                chosen_string = ""
                if num_words in already_selected or not mm.group(0).lower() in vocab:
                    chosen_string = " chosen"
                else:
                    has_unchosen = True
                new_snippet += '<a href="javascript:chooseWord(%d);" class="tag%s" id="word_%d">%s</a>' % (num_words, chosen_string, num_words, mm.group(0))
                num_words += 1
            else:
                new_snippet += mm.group(0)

        template_values['snippet'] = new_snippet

        if not has_unchosen:
            logging.info("No unchosen elements on page %d" % document.document_id)
            self.redirect('/?user_id=%s' % user_id)
        else:
            path = os.path.join(os.path.dirname(__file__), 'index.html')
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

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/submit', RecordResult)],
                                     debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
