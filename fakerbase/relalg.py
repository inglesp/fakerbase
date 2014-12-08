class Relation:
    def __init__(self, attrs, tuples):
        n = len(attrs)
        assert all(t for t in tuples if len(t) == n)
        self.attrs = tuple(attrs)
        self.tuples = {tuple(t) for t in tuples}

    def __eq__(self, other):
        return self.attrs == other.attrs and self.tuples == other.tuples

    def rename(self, new_attrs):
        assert len(new_attrs) == len(self.attrs)
        return Relation(new_attrs, self.tuples)

    def project(self, attrs):
        assert set(attrs) <= set(self.attrs)
        ixs = [self.attrs.index(a) for a in attrs]
        new_tuples = [[t[ix] for ix in ixs] for t in self.tuples]
        return Relation(attrs, new_tuples)

    def select(self, predicate):
        dicts = [dict(zip(self.attrs, t)) for t in self.tuples]
        selected_dicts = [d for d in dicts if predicate(d)]
        selected_tuples = {tuple(d[k] for k in self.attrs) for d in selected_dicts}
        return Relation(self.attrs, selected_tuples)


def cross(rel1, rel2):
    assert not set(rel1.attrs) & set(rel2.attrs)
    new_attrs = rel1.attrs + rel2.attrs
    new_tuples = [t1 + t2 for t1 in rel1.tuples for t2 in rel2.tuples]
    return Relation(new_attrs, new_tuples)


def natural_join(rel1, rel2):
    common_attrs = set(rel1.attrs) & set(rel2.attrs)
    assert common_attrs
    rel1a_attrs = [(1, attr) for attr in rel1.attrs]
    rel2a_attrs = [(2, attr) for attr in rel2.attrs]
    rel2a_only_attrs = [attr for attr in rel2a_attrs if attr[1] not in common_attrs]
    joined_attrs = rel1a_attrs + rel2a_only_attrs
    renamed_attrs = [attr[1] for attr in joined_attrs]
    rel1a = rel1.rename(rel1a_attrs)
    rel2a = rel2.rename(rel2a_attrs)
    cross_rel = cross(rel1a, rel2a)
    predicate = and_(*[eq(F((1, attr)), F((2, attr))) for attr in common_attrs])
    join_rel = cross_rel.select(predicate)
    return join_rel.project(joined_attrs).rename(renamed_attrs)


def diff(rel1, rel2):
    assert rel1.attrs == rel2.attrs
    new_tuples = rel1.tuples - rel2.tuples
    return Relation(rel1.attrs, new_tuples)


def union(rel1, rel2):
    assert rel1.attrs == rel2.attrs
    new_tuples = rel1.tuples | rel2.tuples
    return Relation(rel1.attrs, new_tuples)


def intersection(rel1, rel2):
    assert rel1.attrs == rel2.attrs
    new_tuples = rel1.tuples & rel2.tuples
    return Relation(rel1.attrs, new_tuples)


lookups = {
    'exact': lambda lhs, rhs: lhs == rhs,
    'iexact': lambda lhs, rhs: lhs.lower() == rhs.lower(),
    'contains': lambda lhs, rhs: rhs in lhs,
    'icontains': lambda lhs, rhs: rhs.lower() in lhs.lower(),
    'gt': lambda lhs, rhs: lhs > rhs,
    'gte': lambda lhs, rhs: lhs >= rhs,
    'lt': lambda lhs, rhs: lhs < rhs,
    'lte': lambda lhs, rhs: lhs <= rhs,
    'startswith': lambda lhs, rhs: lhs.startswith(rhs),
    'endswith': lambda lhs, rhs: lhs.endswith(rhs),
    'istartswith': lambda lhs, rhs: lhs.lower().startswith(rhs.lower()),
    'iendswith': lambda lhs, rhs: lhs.lower().endswith(rhs.lower()),
    'year': lambda lhs, rhs: lhs.year == rhs,
    'month': lambda lhs, rhs: lhs.month == rhs,
    'day': lambda lhs, rhs: lhs.day == rhs,
}


def build_predicate_fn(lookup):
    def predicate_fn(lhs, rhs):
        def predicate(record):
            if isinstance(lhs, dict):
                lhsv = record[lhs['field']]
            else:
                lhsv = lhs
            if isinstance(rhs, dict):
                rhsv = record[rhs['field']]
            else:
                rhsv = rhs
            return lookup(lhsv, rhsv)
        return predicate
    return predicate_fn


predicate_fns = {key: build_predicate_fn(lookup) for key, lookup in lookups.items()}

for key, fn in predicate_fns.items():
    locals()[key] = fn

eq = predicate_fns['exact']


def and_(*ps):
    return lambda record: all(p(record) for p in ps)


def or_(*ps):
    return lambda record: any(p(record) for p in ps)


def not_(p):
    return lambda record: not p(record)


def F(fieldname):
    return {'field': fieldname}
