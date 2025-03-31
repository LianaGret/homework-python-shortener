from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from service.api.app import LinkService
from service.db.postgres import get_db
from service.repositories.links import LinkRepository


def get_link_repository(db: AsyncSession = Depends(get_db)) -> LinkRepository:
    return LinkRepository(db)


def get_link_service(repository: LinkRepository = Depends(get_link_repository)) -> LinkService:
    return LinkService(repository)
