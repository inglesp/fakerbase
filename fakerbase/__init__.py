from collections import defaultdict

from django.db.models import Manager, QuerySet
from django.db.models.lookups import Exact
from django.test import TestCase, TransactionTestCase


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

    records = database[join.table_name]

    if self.query.where.children:
        where = self.query.where
        assert where.connector == 'AND'
        assert not where.negated
        assert len(where.children) == 1
        child = where.children[0]
        assert isinstance(child, Exact)
        fieldname = child.lhs.target.name
        value = child.rhs

        records = [r for r in records if r[fieldname] == value]

    fieldnames = [f.attname for f in self.model._meta.fields]
    values_list = [[record[fn] for fn in fieldnames] for record in records]
    return [self.model(**dict(zip(fieldnames, values))) for values in values_list]



class FakerbaseManager(OrigManagerBase):
    __last_id = 0
    __database = defaultdict(list)

    def _insert(self, *args, **kwargs):
        if self.__manages_django_model():
            return super(FakerbaseManager, self)._insert(*args, **kwargs)
        else:
            return self.__insert(*args, **kwargs)

    @classmethod
    def reset_database(cls):
        cls.__database = defaultdict(list)

    def __insert(self, objs, fields, return_id=False, raw=False, using=None):
        assert len(objs) == 1
        assert return_id
        assert not raw

        self.__last_id += 1
        obj = objs[0]
        attrs = {field.attname: getattr(obj, field.attname) for field in fields}
        attrs['id'] = self.__last_id
        table_name = self.model._meta.db_table
        self.__database[table_name].append(attrs)
        return self.__last_id

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


