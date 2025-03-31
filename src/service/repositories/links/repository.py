from datetime import datetime
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from service.models.domain.link import Link


class LinkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, short_code: str, original_url: str, custom_alias: bool = False, expires_at: Optional[datetime] = None
    ) -> Link:
        """Create a new link in the database"""
        query = text("""
            INSERT INTO links (short_code, original_url, custom_alias, expires_at)
            VALUES (:short_code, :original_url, :custom_alias, :expires_at)
            RETURNING id, short_code, original_url, custom_alias, created_at, expires_at
        """)

        result = await self.db.execute(
            query,
            {
                "short_code": short_code,
                "original_url": original_url,
                "custom_alias": custom_alias,
                "expires_at": expires_at,
            },
        )
        await self.db.commit()

        row = result.fetchone()
        return Link(
            id=row[0], short_code=row[1], original_url=row[2], custom_alias=row[3], created_at=row[4], expires_at=row[5]
        )

    async def get_by_short_code(self, short_code: str) -> Optional[Link]:
        """Get a link by its short code"""
        query = text("""
            SELECT id, short_code, original_url, custom_alias, created_at, expires_at
            FROM links
            WHERE short_code = :short_code
        """)

        result = await self.db.execute(query, {"short_code": short_code})
        row = result.fetchone()

        if not row:
            return None

        return Link(
            id=row[0], short_code=row[1], original_url=row[2], custom_alias=row[3], created_at=row[4], expires_at=row[5]
        )

    async def exists_by_short_code(self, short_code: str) -> bool:
        """Check if a link with the given short code exists"""
        query = text("""
            SELECT EXISTS(SELECT 1 FROM links WHERE short_code = :short_code)
        """)

        result = await self.db.execute(query, {"short_code": short_code})
        return result.scalar()

    async def delete(self, link_id: int) -> None:
        """Delete a link by its ID"""
        query = text("""
            DELETE FROM links
            WHERE id = :link_id
        """)

        await self.db.execute(query, {"link_id": link_id})
        await self.db.commit()

    async def update(self, link_id: int, original_url: str, expires_at: Optional[datetime] = None) -> Link:
        """Update a link's original URL and/or expiration date"""
        query = text("""
            UPDATE links
            SET original_url = :original_url,
                expires_at = :expires_at
            WHERE id = :link_id
            RETURNING id, short_code, original_url, custom_alias, created_at, expires_at
        """)

        result = await self.db.execute(
            query, {"link_id": link_id, "original_url": original_url, "expires_at": expires_at}
        )
        await self.db.commit()

        row = result.fetchone()
        return Link(
            id=row[0], short_code=row[1], original_url=row[2], custom_alias=row[3], created_at=row[4], expires_at=row[5]
        )

    async def record_visit(
        self,
        link_id: int,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        referrer: Optional[str] = None,
    ) -> None:
        """Record a visit to a link"""
        query = text("""
            INSERT INTO link_visits (link_id, user_agent, ip_address, referrer)
            VALUES (:link_id, :user_agent, :ip_address, :referrer)
        """)

        await self.db.execute(
            query, {"link_id": link_id, "user_agent": user_agent, "ip_address": ip_address, "referrer": referrer}
        )
        await self.db.commit()

    async def get_visit_count(self, link_id: int) -> int:
        """Get the number of visits for a link"""
        query = text("""
            SELECT COUNT(*) FROM link_visits
            WHERE link_id = :link_id
        """)

        result = await self.db.execute(query, {"link_id": link_id})
        return result.scalar()

    async def get_last_visit(self, link_id: int) -> Optional[datetime]:
        """Get the timestamp of the last visit for a link"""
        query = text("""
            SELECT visited_at FROM link_visits
            WHERE link_id = :link_id
            ORDER BY visited_at DESC
            LIMIT 1
        """)

        result = await self.db.execute(query, {"link_id": link_id})
        row = result.fetchone()

        return row[0] if row else None

    async def find_by_original_url(self, original_url: str) -> List[Link]:
        """Find links by original URL"""
        query = text("""
            SELECT id, short_code, original_url, custom_alias, created_at, expires_at
            FROM links
            WHERE original_url = :original_url
        """)

        result = await self.db.execute(query, {"original_url": original_url})
        rows = result.fetchall()

        return [
            Link(
                id=row[0],
                short_code=row[1],
                original_url=row[2],
                custom_alias=row[3],
                created_at=row[4],
                expires_at=row[5],
            )
            for row in rows
        ]
