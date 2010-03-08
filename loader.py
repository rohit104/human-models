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

class TokenLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Token',
                                   [('token', lambda x: unicode(x, "utf-8")),
                                    ('count', int)])

loaders = [DocumentLoader, VerificationLoader, TokenLoader]

class TagExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'Tag',
                                     [('word', str, None),
                                      ('topic', str, None),
                                      ('document_id', str, None),
                                      ('user_id', str, None),
                                      ('word_string', str, None),
                                      ('date', str, None)])


class SubtokenizationExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'Subtokenization',
                                     [('token', str, None),
                                      ('index', str, None),
                                      ('tag', str, None),
                                      ('user_id', str, None),
                                      ('date', str, None)])

exporters = [TagExporter, SubtokenizationExporter]
