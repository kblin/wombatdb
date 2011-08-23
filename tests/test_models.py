from unittest import TestCase
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from nose.tools import *

from wombatdb.models import Base, Revision, Dir, File


class DBTestCase(TestCase):
    def setUp(self):
        self.engine = create_engine(u'sqlite://', convert_unicode=True)
        self.s = scoped_session(sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine))
        Base.query = self.s.query_property()
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self):
        self.s.rollback()
        Base.metadata.drop_all(bind=self.engine)


class RevisionTestCase(DBTestCase):

    def test_default_log_message(self):
        "Test Revision default log message"
        r = Revision(id=1, name='r1', date=datetime.utcnow())
        eq_(r.log, 'No log message')

    def test_repr(self):
        "Test Revision repr is as expected"
        r = Revision(id=1, name='r1', log='test log message')
        eq_(str(r), "Revision(1: 'test log message')")


class DirTestCase(DBTestCase):

    def test_subdir(self):
        "Test Dir managing a subdir"
        parent = Dir(u'.', u'/', u'fake://fake/repo/base')
        child = Dir(u'./test', u'test', u'fake://fake/repo/base')
        child.parent = parent
        self.s.add(child)
        self.s.add(parent)
        self.s.commit()
        ok_(len(parent.subdirs) == 1)
        eq_(parent.subdirs[0], child)

    def test_subdirs(self):
        "Test Dir managing two subdirs"
        parent = Dir(u'.', u'/', u'fake://fake/repo/base')
        self.s.add(parent)
        child1 = Dir(u'./test', u'test', u'fake://fake/repo/base')
        child1.parent = parent
        self.s.add(child1)
        child2 = Dir(u'./another_test', u'another_test', u'fake://fake/repo/base')
        child2.parent = parent
        self.s.add(child2)
        self.s.commit()
        ok_(len(parent.subdirs) == 2)
        eq_(parent.subdirs[0], child1)
        eq_(parent.subdirs[1], child2)

    def test_repr(self):
        "Test Dir repr is as expected"
        parent = Dir(u'.', u'/', u'fake://fake/repo/base')
        self.s.add(parent)
        child1 = Dir(u'./test', u'test', u'fake://fake/repo/base')
        child1.parent = parent
        self.s.add(child1)
        child2 = Dir(u'./another_test', u'another_test', u'fake://fake/repo/base')
        child2.parent = parent
        self.s.add(child2)
        self.s.commit()
        eq_(str(parent), "Dir(u'.', 2 subdirs, 0 files)")


class FileTestCase(DBTestCase):

    def test_dir_order(self):
        "Test File being in a subdir"
        parent = Dir(u'.', u'/', u'fake://fake/repo/base')
        self.s.add(parent)
        f = File(u'./test.txt', u'test.txt', 0, u'fake://fake/repo/base')
        self.s.add(f)
        parent.files.append(f)
        self.s.commit()
        ok_(len(parent.files) == 1)
        eq_(parent, f.parent)

    def test_repr(self):
        "Test File repr is as expected"
        f = File(u'./test.foo', u'test.foo', 0, u'fake://fake/repo/base')
        self.s.add(f)
        self.s.commit()
        eq_(str(f), "File(u'./test.foo', type: other)")
