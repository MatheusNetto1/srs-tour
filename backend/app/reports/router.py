from typing import Annotated

from fastapi import APIRouter, Query, Response
from fastapi import status as http_status

from app.core.dependencies import DbSession
from app.reports import service
from app.reports.models import Report, ReportStatus
from app.reports.schemas import ReportCreate, ReportResponse, ReportUpdate

YearQuery = Annotated[int | None, Query(ge=1900, le=2100)]
CategoryQuery = Annotated[str | None, Query(min_length=1, max_length=100)]
SearchQuery = Annotated[str | None, Query(min_length=1, max_length=100)]

router = APIRouter()
admin_router = APIRouter()


@router.get(
    "",
    response_model=list[ReportResponse],
)
def list_reports(
    db: DbSession,
    year: YearQuery = None,
    category: CategoryQuery = None,
    q: SearchQuery = None,
) -> list[Report]:
    return service.list_reports(
        db,
        year=year,
        category=category,
        only_published=True,
        q=q,
    )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
def get_report(
    report_id: int,
    db: DbSession,
) -> Report:
    return service.get_report(db, report_id, only_published=True)


@admin_router.get(
    "",
    response_model=list[ReportResponse],
)
def admin_list_reports(
    db: DbSession,
    year: YearQuery = None,
    category: CategoryQuery = None,
    status: Annotated[ReportStatus | None, Query()] = None,
    q: SearchQuery = None,
) -> list[Report]:
    return service.list_reports(
        db,
        year=year,
        category=category,
        only_published=False,
        status=status,
        q=q,
    )


@admin_router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
def admin_get_report(
    report_id: int,
    db: DbSession,
) -> Report:
    return service.get_report(db, report_id, only_published=False)


@admin_router.post(
    "",
    response_model=ReportResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_report(
    data: ReportCreate,
    db: DbSession,
) -> Report:
    return service.create_report(db, data)


@admin_router.put(
    "/{report_id}",
    response_model=ReportResponse,
)
def update_report(
    report_id: int,
    data: ReportUpdate,
    db: DbSession,
) -> Report:
    return service.update_report(db, report_id, data)


@admin_router.delete(
    "/{report_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
def delete_report(
    report_id: int,
    db: DbSession,
) -> Response:
    service.delete_report(db, report_id)

    return Response(status_code=http_status.HTTP_204_NO_CONTENT)


@admin_router.patch(
    "/{report_id}/publish",
    response_model=ReportResponse,
)
def publish_report(
    report_id: int,
    db: DbSession,
) -> Report:
    return service.publish_report(db, report_id)


@admin_router.patch(
    "/{report_id}/unpublish",
    response_model=ReportResponse,
)
def unpublish_report(
    report_id: int,
    db: DbSession,
) -> Report:
    return service.unpublish_report(db, report_id)
