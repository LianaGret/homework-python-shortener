from datetime import datetime
from typing import Optional

from fastapi import Request
from pydantic import HttpUrl

from service.common.shortcode_generator import generate_short_code
from service.core.exceptions import DuplicateAliasException, LinkNotFoundException
from service.models.schemas.link import LinkCreate, LinkResponse, LinkSearchResponse, LinkStats, LinkUpdate
from service.repositories.links import LinkRepository


class LinkService:
    def __init__(self, repository: LinkRepository):
        self.repository = repository

    async def create_link(self, link_data: LinkCreate) -> LinkResponse:
        """Create a new shortened link"""
        if not link_data.custom_alias:
            short_code = generate_short_code()
        else:
            short_code = link_data.custom_alias
            if await self.repository.exists_by_short_code(short_code):
                raise DuplicateAliasException(f"Custom alias '{short_code}' already exists")

        link = await self.repository.create(
            short_code=short_code,
            original_url=link_data.original_url.encoded_string(),
            custom_alias=bool(link_data.custom_alias),
            expires_at=link_data.expires_at,
        )

        return LinkResponse(
            short_code=link.short_code,
            original_url=HttpUrl(link.original_url),
            created_at=link.created_at,
            expires_at=link.expires_at,
            custom_alias=link.custom_alias,
        )

    async def get_original_url(self, short_code: str, request: Optional[Request] = None) -> str:
        """Get the original URL and record a visit"""
        link = await self.repository.get_by_short_code(short_code)
        if not link:
            raise LinkNotFoundException(f"Link with short code '{short_code}' not found")

        if link.expires_at:
            now = datetime.now(link.expires_at.tzinfo)
            if link.expires_at < now:
                await self.repository.delete(link.id)
                raise LinkNotFoundException(f"Link with short code '{short_code}' has expired")

        if request:
            user_agent = request.headers.get("user-agent", "")
            referrer = request.headers.get("referer", "")
            client_host = request.client.host if request.client else None

            await self.repository.record_visit(
                link_id=link.id, user_agent=user_agent, ip_address=client_host, referrer=referrer
            )

        return link.original_url

    async def delete_link(self, short_code: str) -> None:
        """Delete a shortened link"""
        link = await self.repository.get_by_short_code(short_code)
        if not link:
            raise LinkNotFoundException(f"Link with short code '{short_code}' not found")

        await self.repository.delete(link.id)

    async def update_link(self, short_code: str, link_data: LinkUpdate) -> LinkResponse:
        """Update a shortened link"""
        link = await self.repository.get_by_short_code(short_code)

        if link_data.expires_at:
            now = datetime.now(link_data.expires_at.tzinfo)
            if link_data.expires_at <= now:
                raise ValueError("Expiration date must be in the future")

        if not link:
            raise LinkNotFoundException(f"Link with short code '{short_code}' not found")

        updated_link = await self.repository.update(
            link_id=link.id, original_url=link_data.original_url.encoded_string(), expires_at=link_data.expires_at
        )

        return LinkResponse(
            short_code=updated_link.short_code,
            original_url=HttpUrl(updated_link.original_url),
            created_at=updated_link.created_at,
            expires_at=updated_link.expires_at,
            custom_alias=updated_link.custom_alias,
        )

    async def get_link_stats(self, short_code: str) -> LinkStats:
        """Get statistics for a shortened link"""
        link = await self.repository.get_by_short_code(short_code)
        if not link:
            raise LinkNotFoundException(f"Link with short code '{short_code}' not found")

        visit_count = await self.repository.get_visit_count(link.id)
        last_visit = await self.repository.get_last_visit(link.id)

        return LinkStats(
            short_code=link.short_code,
            original_url=HttpUrl(link.original_url),
            created_at=link.created_at,
            visit_count=visit_count,
            last_visited_at=last_visit,
        )

    async def search_by_original_url(self, original_url: str) -> LinkSearchResponse:
        """Search for links by original URL"""
        links = await self.repository.find_by_original_url(original_url)

        return LinkSearchResponse(
            original_url=HttpUrl(original_url),
            links=[
                LinkResponse(
                    short_code=link.short_code,
                    original_url=HttpUrl(link.original_url),
                    created_at=link.created_at,
                    expires_at=link.expires_at,
                    custom_alias=link.custom_alias,
                )
                for link in links
            ],
        )
