#!python

import re
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import models

class MainPage(webapp.RequestHandler):
    def get(self):
        already_selected = set([4, 8, 15, 16, 23, 42])
        
        user_id = self.request.get("user_id")
        if not user_id:
            path = os.path.join(os.path.dirname(__file__), 'invalid_userid.html')
            self.response.out.write(template.render(path, {}))
            return

        template_values = {
            'topics' : [["meow"], ["meep"]],
            'title' : "Lorem ipsum",
            'document_id' : 314159,
            'user_id' : user_id,
'snippet' : """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec
tempus lorem. Morbi tristique nisi sit amet nulla dapibus
luctus. Nullam id nunc quis eros ornare rhoncus sit amet quis
nisl. Phasellus in turpis nec dolor pellentesque
elementum. Pellentesque at lorem et sapien dictum vestibulum. Fusce
augue erat, ornare vitae eleifend a, ultrices ut dui. Nunc blandit
velit ac neque ullamcorper eleifend. Sed at est lectus, id adipiscing
felis. Suspendisse justo ipsum, varius id fringilla sed, convallis a
erat. Etiam quis ipsum lacus, non tincidunt leo. Morbi euismod
ullamcorper neque, non venenatis risus lacinia vel. Nam faucibus
imperdiet blandit.

Proin tempus, ipsum nec hendrerit vehicula, eros sapien euismod
ligula, nec vulputate est mi sagittis mi. Pellentesque tincidunt,
velit et ornare cursus, turpis neque mattis arcu, quis tempor lectus
ipsum vitae nunc. Curabitur mattis lorem vel diam imperdiet
imperdiet. Phasellus vehicula auctor cursus. Curabitur ipsum eros,
semper nec euismod sed, vestibulum a mauris. Integer semper mi ut eros
pharetra tristique. Vivamus ante eros, viverra vitae commodo non,
egestas quis odio. Ut non metus id mi condimentum ornare. Cras vel
nulla metus, non adipiscing ipsum. Proin facilisis diam id lorem
volutpat in tincidunt purus tincidunt. Integer scelerisque rhoncus
nisl, ac dignissim nunc vestibulum ut. Quisque sed justo erat.
"""
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
        tag = models.Tag()
        tag.topic = int(self.request.get("topic"))
        tag.word = int(self.request.get("word"))
        tag.user_id = int(self.request.get("user_id"))
        tag.document_id = int(self.request.get("document_id"))
        tag.word_string = self.request.get("word_string").lower()
        tag.put()
        self.redirect('/?user_id=%s' % self.request.get("user_id"))

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/submit', RecordResult)],
                                     debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
