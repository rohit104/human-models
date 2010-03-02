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


class VerificationLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Verification',
                                   [('user_id', int),
                                    ('verification_code', int)])

loaders = [DocumentLoader, VerificationLoader]

class TagExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'Tag',
                                     [('word', str, None),
                                      ('topic', str, None),
                                      ('document_id', str, None),
                                      ('user_id', str, None),
                                      ('word_string', str, None),
                                      ('date', str, None)])

exporters = [TagExporter]
