import logging

from sqlalchemy import select
from forum.auth.models import Role
from forum.database.core import DbSession

log = logging.getLogger(__name__)


async def init_roles(session: DbSession):
    res = await session.scalar(select(Role))
    if res is None:
        role = Role(name="User")
        session.add(role)
        log.info("Creating User role")
        role = Role(name="Moderator")
        session.add(role)
        log.info("Creating Moderador role")
        role = Role(name="Admin")
        session.add(role)
        log.info("Creating Admin role")
        await session.commit()
