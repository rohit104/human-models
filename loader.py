import datetime
from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models

class DocumentLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Document',
                                   [('document_id', int),
                                    ('title', lambda x: unicode(x, "utf-8")),
                                    ('body', lambda x: unicode(x, "utf-8"))])

loaders = [DocumentLoader]
                                    
