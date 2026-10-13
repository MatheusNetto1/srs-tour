from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.core.dependencies import DbSession
from app.reports import service
from app.reports.models import Report
from app.reports.schemas import ReportCreate, ReportResponse, ReportUpdate

router = APIRouter()

NOT_FOUND_DETAIL = "Relatório não encontrado."


@router.get(
    "",
    response_model=list[ReportResponse],
)
def list_reports(
    db: DbSession,
    year: Annotated[int | None, Query(ge=1900, le=2100)] = None,
    category: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
) -> list[Report]:
    # Listagem pública: apenas relatórios publicados.
    # Quando o módulo Auth estiver integrado, a visão administrativa
    # (incluindo rascunhos) deve usar only_published=False.
    return service.list_reports(db, year=year, category=category)


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
def get_report(
    report_id: int,
    db: DbSession,
) -> Report:
    try:
        return service.get_report(db, report_id, only_published=True)
    except service.ReportNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOT_FOUND_DETAIL,
        ) from error


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    data: ReportCreate,
    db: DbSession,
) -> Report:
    return service.create_report(db, data)


@router.put(
    "/{report_id}",
    response_model=ReportResponse,
)
def update_report(
    report_id: int,
    data: ReportUpdate,
    db: DbSession,
) -> Report:
    try:
        return service.update_report(db, report_id, data)
    except service.ReportNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOT_FOUND_DETAIL,
        ) from error


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_report(
    report_id: int,
    db: DbSession,
) -> Response:
    try:
        service.delete_report(db, report_id)
    except service.ReportNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOT_FOUND_DETAIL,
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{report_id}/publish",
    response_model=ReportResponse,
)
def publish_report(
    report_id: int,
    db: DbSession,
) -> Report:
    try:
        return service.publish_report(db, report_id)
    except service.ReportNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOT_FOUND_DETAIL,
        ) from error


@router.patch(
    "/{report_id}/unpublish",
    response_model=ReportResponse,
)
def unpublish_report(
    report_id: int,
    db: DbSession,
) -> Report:
    try:
        return service.unpublish_report(db, report_id)
    except service.ReportNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOT_FOUND_DETAIL,
        ) from error
