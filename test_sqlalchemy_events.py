import weakref

import sqlalchemy
from sqlalchemy import event
from sqlalchemy import orm

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def expire_for_fk_change(target, fk_value, relationship_prop, column_attr):
    sess = orm.object_session(target)

    if sess is not None:
        if relationship_prop.back_populates and \
                relationship_prop.key in target.__dict__:
            obj = getattr(target, relationship_prop.key)
            if obj is not None and sqlalchemy.inspect(obj).persistent:
                sess.expire(obj, [relationship_prop.back_populates])

        if sqlalchemy.inspect(target).persistent:
            sess.expire(target, [relationship_prop.key])

        # optional - set manytoones directly to avoid a SQL round trip
        if relationship_prop.back_populates:
            target.__dict__[column_attr] = fk_value
            new = getattr(target, relationship_prop.key)
            if new is not None:
                if sqlalchemy.inspect(new).persistent:
                    sess.expire(new, [relationship_prop.back_populates])
    else:
        if target not in _emit_on_pending:
            _emit_on_pending[target] = []
        _emit_on_pending[target].append(
            (fk_value, relationship_prop, column_attr))


_emit_on_pending = weakref.WeakKeyDictionary()


@event.listens_for(orm.session.Session, "pending_to_persistent")
def _pending_callables(session, obj):
    if obj is None:
        return
    args = _emit_on_pending.pop(obj, [])
    for a in args:
        if a is not None:
            expire_for_fk_change(obj, *a)


@event.listens_for(orm.session.Session, "persistent_to_deleted")
def _persistent_to_deleted(session, obj):
    mapper = sqlalchemy.inspect(obj).mapper
    for prop in mapper.relationships:
        if prop.direction is orm.interfaces.MANYTOONE:
            for col in prop.local_columns:
                colkey = mapper.get_property_by_column(col).key
                expire_for_fk_change(obj, None, prop, colkey)


@event.listens_for(Base, "attribute_instrument", propagate=True)
def _listen_for_changes(cls, key, inst):
    mapper = sqlalchemy.inspect(cls)
    if key not in mapper.relationships:
        return
    prop = inst.property

    if prop.direction is orm.interfaces.MANYTOONE:
        for col in prop.local_columns:
            colkey = mapper.get_property_by_column(col).key
            _expire_prop_on_col(cls, prop, colkey)
    elif prop.direction is orm.interfaces.ONETOMANY:
        remote_mapper = prop.mapper
        # the collection *has* to have a MANYTOONE backref so we
        # can look up the parent.  so here we make one if it doesn't
        # have it already, as is the case in this example
        if not prop.back_populates:
            name = "_%s_backref" % prop.key
            backref_prop = orm.relationship(
                prop.parent, back_populates=prop.key)

            remote_mapper.add_property(name, backref_prop)
            prop.back_populates = name


def _expire_prop_on_col(cls, prop, colkey):
    @event.listens_for(getattr(cls, colkey), "set")
    def expire(target, value, oldvalue, initiator):
        expire_for_fk_change(target, value, prop, colkey)


if __name__ == '__main__':
    from sqlalchemy.orm import Session, relationship
    from sqlalchemy import create_engine, Column, Integer, ForeignKey

    class User(Base):
        __tablename__ = 'user'
        id = Column(Integer, primary_key=True)

    class Article(Base):
        __tablename__ = 'article'
        id = Column(Integer, primary_key=True)
        content = Column(Integer)

        user_id = Column(Integer, ForeignKey(User.id))
        user = relationship("User", backref="articles")

    e = create_engine("sqlite://", echo=True)

    Base.metadata.create_all(e)

    DBSession = Session(e)

    user1 = User(id=23)
    user2 = User(id=42)
    DBSession.add(user2)
    DBSession.add(user1)

    article = Article()
    article.user_id = user1.id
    DBSession.add(article)

    DBSession.flush()
    assert article.user.id == 23
    assert article.user_id == 23

    article.user_id = 42

    DBSession.flush()
    assert article.user.id == 42
    assert article.user_id == 42

    DBSession.commit()
    assert article.user.id == 42
    assert article.user_id == 42

    assert article in user2.articles
    assert article not in user1.articles

    article.user_id = 23

    assert article not in user2.articles
    assert article in user1.articles

    article2 = Article(user_id=42)
    assert article2 not in user2.articles

    DBSession.add(article2)
    DBSession.flush()

    assert article2 in user2.articles
