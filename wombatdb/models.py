from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from datetime import datetime
from os.path import splitext

Base = declarative_base()

class Revision(Base):
    __tablename__ = 'revisions'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    log = Column(Text)
    author = Column(Unicode(255))
    date = Column(DateTime)
    files = relationship("File", backref="revision")
    dirs = relationship("Dir", backref="revision")

    def __init__(self, id, name, log=u'No log message',
            author=u'Unkonwn author', date=datetime.utcnow()):
        self.id = id
        self.name = name
        self.log = log
        self.author = author
        self.date = date

    def __repr__(self):
        return "Revision(%d: %r)" %(self.id, self.log)

class Dir(Base):
    __tablename__ = 'dirs'
    path = Column(Unicode(255), primary_key=True)
    name = Column(Unicode(255))
    root = Column(Unicode(255))
    rev_id = Column(Integer, ForeignKey('revisions.id'))
    in_dir = Column(Unicode(255), ForeignKey('dirs.path'))
    files = relationship("File", backref="parent")
    subdirs = relationship("Dir", backref=backref("parent", remote_side="Dir.path"))

    def __init__(self, path, name, root):
        self.path = path
        self.name = name
        self.root = root

    def __repr__(self):
        return "Dir(%r, %d subdirs, %d files)" % (self.path, len(self.subdirs), len(self.files))

class File(Base):
    __tablename__ = 'files'
    path = Column(Unicode(255), primary_key=True)
    name = Column(Unicode(255))
    size = Column(Integer)
    root = Column(Unicode(255))
    ext = Column(Unicode(255))
    type = Column(Unicode(20))
    in_dir = Column(Unicode(255), ForeignKey('dirs.path'))
    rev_id = Column(Integer, ForeignKey('revisions.id'))

    def __init__(self, path, name, size, root):
        self.path = path
        self.name = name
        self.size = size
        self.root = root
        dummy, self.ext = splitext(name)
        self.ext = self.ext.lower()
        self.type = u'other'

    def __repr__(self):
        return "File(%r, type: %s)" % (self.path, self.type)
