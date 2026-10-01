from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.reports.models import Report


def list_reports(
    db: Session,
    *,
    year: int | None = None,
    category: str | None = None,
    status: str | None = None,
) -> list[Report]:
    statement = select(Report).order_by(Report.year.desc(), Report.title)

    if year is not None:
        statement = statement.where(Report.year == year)

    if category is not None:
        statement = statement.where(
            func.lower(Report.category) == category.lower(),
        )

    if status is not None:
        statement = statement.where(Report.status == status)

    return list(db.scalars(statement).all())


def get_report_by_id(db: Session, report_id: int) -> Report | None:
    return db.get(Report, report_id)


def add_report(db: Session, report: Report) -> Report:
    db.add(report)
    db.flush()
    db.refresh(report)

    return report


def update_report(db: Session, report: Report) -> Report:
    db.flush()
    db.refresh(report)

    return report


def delete_report(db: Session, report: Report) -> None:
    db.delete(report)
    db.flush()
