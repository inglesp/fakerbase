from django.db.models import Manager, QuerySet, lookups
from django.db.models.sql.where import WhereNode
from django.test import TestCase, TransactionTestCase

from .relalg import Relation, union, inner_join, predicate_fns, F, and_, or_, not_


assert len(Manager.__bases__) == 1
OrigManagerBase = Manager.__bases__[0]

orig_queryset_iterator = QuerySet.iterator


def build_predicate(node):
    if isinstance(node, lookups.BuiltinLookup):
        predicate_fn = predicate_fns[node.lookup_name]
        lhs = node.lhs
        assert lhs.target == lhs.source, 'Expect query lhs target to equal source'
        attr = (lhs.alias, lhs.target.name)
        value = node.rhs

        predicate = predicate_fn(F(attr), value)

    elif isinstance(node, WhereNode):
        child_predicates = [build_predicate(child) for child in node.children]

        if node.connector == 'AND':
            predicate = and_(*child_predicates)
        else:
            predicate = or_(*child_predicates)

        if node.negated:
            predicate = not_(predicate)

    return predicate


def fakerbase_iterator(self):
    database = FakerbaseManager._FakerbaseManager__database

    compiler = self.query.get_compiler(using=self.db)
    compiler.pre_sql_setup()

    first = True

    for alias in self.query.tables:
        join = self.query.alias_map[alias]

        assert join.table_name == join.rhs_alias, 'Cannot handle queries with aliases'
        assert len(join.join_cols) == 1, 'Cannot handle queries with multiple join columns'

        lhs_alias, rhs_alias = join.lhs_alias, join.rhs_alias
        lhs_col, rhs_col = join.join_cols[0]

        if first:
            assert join.join_type is None, 'Expect join_type to be None'
            rel = database[rhs_alias]
            first = False
        else:
            assert join.join_type == 'INNER JOIN', 'Can only handle INNER JOINs'
            attr_pair = ((lhs_alias, lhs_col), (rhs_alias, rhs_col))
            rel = inner_join(rel, database[rhs_alias], attr_pair)

    if self.query.where.children:
        predicate = build_predicate(self.query.where)
        rel = rel.select(predicate)

    table_name = self.model._meta.db_table

    attrs = [attr for attr in rel.attrs if attr[0] == table_name]
    rel = rel.project(attrs)

    attrs = [attr[1] for attr in rel.attrs]
    rel = rel.rename(attrs)

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
        assert not (return_id and len(objs) != 1), 'Cannot return id if inserting more than one object'
        assert not raw

        table_name = self.__table_name()

        for obj in objs:
            self.__last_id += 1

            attrs = [field.attname for field in fields]

            if 'id' in attrs:
                t = [getattr(obj, field.attname) for field in fields]
            else:
                attrs = ['id'] + attrs
                t = [self.__last_id] + [getattr(obj, field.attname) for field in fields]

            namespaced_attrs = [(table_name, attr) for attr in attrs]

            if table_name in self.__database:
                rel = self.__database[table_name]
            else:
                rel = Relation(namespaced_attrs, set())

            self.__database[table_name] = union(rel, Relation(namespaced_attrs, [t]))

        if return_id:
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
