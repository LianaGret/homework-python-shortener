from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import RedirectResponse

from service.api.dependencies import get_link_service
from service.models.schemas.link import LinkCreate, LinkResponse, LinkSearchResponse, LinkStats, LinkUpdate
from service.services.link_service import LinkService


router = APIRouter(prefix="/links", tags=["Links"])


@router.post("/shorten", response_model=LinkResponse, status_code=201)
async def create_short_link(link_data: LinkCreate, link_service: LinkService = Depends(get_link_service)):
    """Create a new shortened link"""
    return await link_service.create_link(link_data)


@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str, response: Response, link_service: LinkService = Depends(get_link_service)
):
    """Redirect to the original URL"""
    original_url = await link_service.get_original_url(short_code)
    return RedirectResponse(url=original_url)


@router.delete("/{short_code}", status_code=204)
async def delete_link(short_code: str, link_service: LinkService = Depends(get_link_service)):
    """Delete a shortened link"""
    await link_service.delete_link(short_code)
    return Response(status_code=204)


@router.put("/{short_code}", response_model=LinkResponse)
async def update_link(short_code: str, link_data: LinkUpdate, link_service: LinkService = Depends(get_link_service)):
    """Update a shortened link"""
    return await link_service.update_link(short_code, link_data)


@router.get("/{short_code}/stats", response_model=LinkStats)
async def get_link_stats(short_code: str, link_service: LinkService = Depends(get_link_service)):
    """Get statistics for a shortened link"""
    return await link_service.get_link_stats(short_code)


@router.get("/search", response_model=LinkSearchResponse)
async def search_by_original_url(
    original_url: str = Query(..., description="Original URL to search for"),
    link_service: LinkService = Depends(get_link_service),
):
    """Search for a shortened link by original URL"""
    return await link_service.search_by_original_url(original_url)
