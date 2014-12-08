from django.db.models import Manager, QuerySet
from django.db.models.lookups import Exact
from django.test import TestCase, TransactionTestCase

from .relalg import Relation, union, eq, F


assert len(Manager.__bases__) == 1
OrigManagerBase = Manager.__bases__[0]

orig_queryset_iterator = QuerySet.iterator


def fakerbase_iterator(self):
    database = FakerbaseManager._FakerbaseManager__database

    compiler = self.query.get_compiler(using=self.db)
    compiler.pre_sql_setup()

    assert len(self.query.tables) == 1

    table = self.query.tables[0]
    join = self.query.alias_map[table]

    assert join.table_name == join.rhs_alias
    assert len(join.join_cols) == 1
    assert join.join_type is None

    rel = database[join.table_name]

    if self.query.where.children:
        where = self.query.where
        assert where.connector == 'AND'
        assert not where.negated
        assert len(where.children) == 1
        child = where.children[0]
        assert isinstance(child, Exact)
        fieldname = child.lhs.target.name
        value = child.rhs

        p = eq(F(fieldname), value)
        rel = rel.select(p)

    return [self.model(**dict(zip(rel.attrs, t))) for t in rel.tuples]


class FakerbaseManager(OrigManagerBase):
    __last_id = 0

    @classmethod
    def reset_database(cls):
        cls.__database = {}

    def _insert(self, *args, **kwargs):
        if self.__manages_django_model():
            return super(FakerbaseManager, self)._insert(*args, **kwargs)
        else:
            return self.__insert(*args, **kwargs)

    def __insert(self, objs, fields, return_id=False, raw=False, using=None):
        assert len(objs) == 1
        assert return_id
        assert not raw

        self.__last_id += 1
        obj = objs[0]

        attrs = ['id'] + [field.attname for field in fields]
        t = [self.__last_id] + [getattr(obj, field.attname) for field in fields]

        table_name = self.__table_name()

        if table_name in self.__database:
            rel = self.__database[table_name]
        else:
            rel = Relation(attrs, set())

        self.__database[table_name] = union(rel, Relation(attrs, [t]))
        return self.__last_id

    def __table_name(self):
        return self.model._meta.db_table

    def __manages_django_model(self):
        return self.model.__module__.split('.')[0] == 'django'


class FakerbaseTestCase(TransactionTestCase):
    def run(self, *args, **kwargs):
        Manager.__bases__ = (FakerbaseManager,)
        QuerySet.iterator = fakerbase_iterator

        FakerbaseManager.reset_database()

        rc = super(FakerbaseTestCase, self).run(*args, **kwargs)

        Manager.__bases__ = (OrigManagerBase,)
        QuerySet.iterator = orig_queryset_iterator

        return rc

assert TestCase.__bases__ == (TransactionTestCase,)
TestCase.__bases__ = (FakerbaseTestCase,)
