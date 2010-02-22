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

class MainPage(webapp.RequestHandler):
    def get(self):
        user_id = self.request.get("user_id")
        if not user_id:
            path = os.path.join(os.path.dirname(__file__), 'invalid_userid.html')
            self.response.out.write(template.render(path, {}))
            return

        random.seed(8675309)

        ids = db.GqlQuery("select __key__ from Document")
        ids = ids.fetch(100)
        chosen_id = random.choice(ids)
        document = models.Document.get(chosen_id)

        top_topics = db.GqlQuery("select * from DocumentStats where document_id = %d order by count desc" % document.document_id)

        num_topics = 10
        top_topics = top_topics.fetch(num_topics)
        ## select at most 5
        real_top_topics = [x.topic for x in top_topics[:5]]

        ## find empties
        unused_topics = set(range(num_topics)) - set([x.topic for x in top_topics])
        ## pad with empties if we don't have enough
        if len(real_top_topics) < 5:
            padding = list(unused_topics)[:(5 - len(real_top_topics))]
            real_top_topics += padding
        ## FIXME: clean up this logic!!
        ## if there are any available topics, make sure they see at
        ## least one empty
        elif len(unused_topics) > 0:
            real_top_topics[4] = list(unused_topics)[0]
            
        top_topic_words = []
        for tt in real_top_topics:
            logging.info("Querying for topic %d" % tt)
            topic_words = db.GqlQuery("select * from TopicStats where topic = %d order by count desc" % tt)
            top_topic_words.append({'topic' : tt, 'words' : [x.word for x in topic_words.fetch(5)]})

        ## Get the already selected!
        already_selected = db.GqlQuery("select * from Tag where document_id = %d" % document.document_id)
        already_selected.fetch(1000)

        ## Do something if they've all been already selected!
        already_selected = [x.word for x in already_selected]
            
        template_values = {
            'topics' : top_topic_words,
            'title' : document.title,
            'document_id' : document.document_id,
            'user_id' : user_id,
            'snippet' : document.body.replace("\\n", "\n"),
        }
        num_words = 0
        new_snippet = ""
        for mm in re.finditer(r'(\w+|\W+)', template_values['snippet']):
            if re.match(r'\w+', mm.group(0)):
                chosen_string = ""
                if num_words in already_selected:
                    chosen_string = " chosen"
                new_snippet += '<a href="javascript:chooseWord(%d);" class="tag%s" id="word_%d">%s</a>' % (num_words, chosen_string, num_words, mm.group(0))
                num_words += 1
            else:
                new_snippet += mm.group(0)

        template_values['snippet'] = new_snippet

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
