from fastapi import APIRouter

from service.api.routes import router as links_router


router = APIRouter(prefix="/api/v1")

router.include_router(links_router)
