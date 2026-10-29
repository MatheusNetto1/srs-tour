from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.indicators.models import Indicator, IndicatorStatus
from app.reports.models import Report, ReportStatus
from scripts.seed_content import INDICATORS, REPORTS, seed_indicators, seed_reports


def _count(session: Session, model, **filters) -> int:
    stmt = select(func.count()).select_from(model)

    for column, value in filters.items():
        stmt = stmt.where(getattr(model, column) == value)

    return session.scalar(stmt)


def test_seed_indicators_creates_published_and_draft_rows(
    db_session: Session,
) -> None:
    seed_indicators(db_session)

    expected_published = sum(1 for item in INDICATORS if item["status"] == "published")
    expected_drafts = sum(1 for item in INDICATORS if item["status"] == "draft")

    assert (
        _count(db_session, Indicator, status=IndicatorStatus.PUBLISHED)
        == expected_published
    )
    assert (
        _count(db_session, Indicator, status=IndicatorStatus.DRAFT) == expected_drafts
    )


def test_seed_indicators_is_idempotent(db_session: Session) -> None:
    seed_indicators(db_session)
    seed_indicators(db_session)

    assert _count(db_session, Indicator) == len(INDICATORS)


def test_seed_reports_creates_published_and_draft_rows(db_session: Session) -> None:
    seed_reports(db_session)

    expected_published = sum(1 for item in REPORTS if item["status"] == "published")
    expected_drafts = sum(1 for item in REPORTS if item["status"] == "draft")

    assert (
        _count(db_session, Report, status=ReportStatus.PUBLISHED.value)
        == expected_published
    )
    assert (
        _count(db_session, Report, status=ReportStatus.DRAFT.value) == expected_drafts
    )


def test_seed_reports_is_idempotent(db_session: Session) -> None:
    seed_reports(db_session)
    seed_reports(db_session)

    assert _count(db_session, Report) == len(REPORTS)
