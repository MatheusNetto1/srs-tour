from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.reports import repository
from app.reports.exceptions import ReportNotFoundError
from app.reports.models import Report, ReportStatus
from app.reports.schemas import ReportCreate, ReportUpdate


def list_reports(
    db: Session,
    *,
    year: int | None = None,
    category: str | None = None,
    only_published: bool = True,
    status: ReportStatus | str | None = None,
    q: str | None = None,
) -> list[Report]:
    if only_published:
        resolved_status: str | None = ReportStatus.PUBLISHED.value
    elif status is not None:
        resolved_status = str(status)
    else:
        resolved_status = None

    return repository.list_reports(
        db,
        year=year,
        category=category,
        status=resolved_status,
        q=q,
    )


def get_report(
    db: Session,
    report_id: int,
    *,
    only_published: bool = False,
) -> Report:
    report = repository.get_report_by_id(db, report_id)

    if report is None:
        raise ReportNotFoundError

    if only_published and report.status != ReportStatus.PUBLISHED.value:
        raise ReportNotFoundError

    return report


def create_report(db: Session, data: ReportCreate) -> Report:
    report = Report(
        title=data.title.strip(),
        description=data.description,
        category=data.category.strip(),
        year=data.year,
        status=ReportStatus.DRAFT.value,
    )

    report = repository.add_report(db, report)
    db.commit()

    return report


def update_report(db: Session, report_id: int, data: ReportUpdate) -> Report:
    report = get_report(db, report_id)

    report.title = data.title.strip()
    report.description = data.description
    report.category = data.category.strip()
    report.year = data.year

    report = repository.update_report(db, report)
    db.commit()

    return report


def delete_report(db: Session, report_id: int) -> None:
    report = get_report(db, report_id)

    repository.delete_report(db, report)
    db.commit()


def publish_report(db: Session, report_id: int) -> Report:
    report = get_report(db, report_id)

    if report.status != ReportStatus.PUBLISHED.value:
        report.status = ReportStatus.PUBLISHED.value
        report.published_at = datetime.now(UTC)

    report = repository.update_report(db, report)
    db.commit()

    return report


def unpublish_report(db: Session, report_id: int) -> Report:
    report = get_report(db, report_id)

    report.status = ReportStatus.DRAFT.value
    report.published_at = None

    report = repository.update_report(db, report)
    db.commit()

    return report
