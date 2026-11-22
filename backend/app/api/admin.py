from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin

from app.schemas.admin import AdminDashboardResponse

from app.services.admin_service import (
    get_admin_dashboard_stats,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
)
def admin_dashboard(
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):

    stats = get_admin_dashboard_stats(db)

    return stats