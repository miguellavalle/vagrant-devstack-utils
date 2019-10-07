from sqlalchemy import and_, or_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from neutron.db.models import securitygroup
from neutron.db import rbac_db_models as models

engine = create_engine(
    'mysql+pymysql://root:devstack@127.0.0.1/neutron?charset=utf8',
    echo=False)
# connection = engine.connect()
# result = connection.execute('select * from ports')
# ports = [p for p in result]
# connection.close()
project_id = '29b2f9ab6dc04e0ab8ab7e48c8baaa8d'
session = sessionmaker()
session.configure(bind=engine)
s = session()
query = s.query(
    securitygroup.SecurityGroup).outerjoin(models.SecurityGroupRBAC)
query = query.filter(
        or_(securitygroup.SecurityGroup.project_id == project_id,
            and_(models.SecurityGroupRBAC.action == models.ACCESS_SHARED,
                 models.SecurityGroupRBAC.target_tenant.in_(
                     ['*', project_id]))))
