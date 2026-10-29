"""Seeders de indicadores e relatórios de exemplo (ver `scripts/seed.py`).

Os valores abaixo são uma cópia dos mocks do frontend (`frontend/src/mocks/
indicators.ts` e `reports.ts`); o backend não importa o frontend.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.indicators.models import IndicatorStatus
from app.indicators.repository import IndicatorRepository
from app.indicators.schemas import IndicatorCreate
from app.indicators.service import IndicatorService
from app.indicators.slug import slugify
from app.reports.models import Report
from app.reports.schemas import ReportCreate
from app.reports.service import create_report, publish_report

INDICATORS = [
    {
        "name": "Meios de hospedagem",
        "sector": "Hospedagem",
        "period": 2024,
        "value": 27,
        "unit": "estabelecimentos",
        "status": "published",
    },
    {
        "name": "Meios de hospedagem",
        "sector": "Hospedagem",
        "period": 2025,
        "value": 30,
        "unit": "estabelecimentos",
        "status": "published",
    },
    {
        "name": "Meios de hospedagem",
        "sector": "Hospedagem",
        "period": 2026,
        "value": 32,
        "unit": "estabelecimentos",
        "status": "published",
    },
    {
        "name": "Leitos disponíveis",
        "sector": "Hospedagem",
        "period": 2024,
        "value": 681,
        "unit": "leitos",
        "status": "published",
    },
    {
        "name": "Leitos disponíveis",
        "sector": "Hospedagem",
        "period": 2025,
        "value": 714,
        "unit": "leitos",
        "status": "published",
    },
    {
        "name": "Leitos disponíveis",
        "sector": "Hospedagem",
        "period": 2026,
        "value": 742,
        "unit": "leitos",
        "status": "published",
    },
    {
        "name": "Estabelecimentos de alimentação",
        "sector": "Alimentação",
        "period": 2024,
        "value": 49,
        "unit": "estabelecimentos",
        "status": "published",
    },
    {
        "name": "Estabelecimentos de alimentação",
        "sector": "Alimentação",
        "period": 2025,
        "value": 54,
        "unit": "estabelecimentos",
        "status": "published",
    },
    {
        "name": "Estabelecimentos de alimentação",
        "sector": "Alimentação",
        "period": 2026,
        "value": 58,
        "unit": "estabelecimentos",
        "status": "published",
    },
    {
        "name": "Empresas de serviços turísticos",
        "sector": "Serviços",
        "period": 2024,
        "value": 41,
        "unit": "empresas",
        "status": "published",
    },
    {
        "name": "Empresas de serviços turísticos",
        "sector": "Serviços",
        "period": 2025,
        "value": 45,
        "unit": "empresas",
        "status": "published",
    },
    {
        "name": "Empresas de serviços turísticos",
        "sector": "Serviços",
        "period": 2026,
        "value": 49,
        "unit": "empresas",
        "status": "published",
    },
    {
        "name": "Empregos no turismo",
        "sector": "Geral",
        "period": 2024,
        "value": 1138,
        "unit": "empregos",
        "status": "published",
    },
    {
        "name": "Empregos no turismo",
        "sector": "Geral",
        "period": 2025,
        "value": 1207,
        "unit": "empregos",
        "status": "published",
    },
    {
        "name": "Empregos no turismo",
        "sector": "Geral",
        "period": 2026,
        "value": 1284,
        "unit": "empregos",
        "status": "published",
    },
    {
        "name": "Fluxo estimado de visitantes",
        "sector": "Geral",
        "period": 2026,
        "value": 0,
        "unit": "visitantes",
        "status": "draft",
    },
]

REPORTS = [
    {
        "title": "Relatório Anual do Turismo 2026",
        "description": (
            "Síntese demonstrativa dos principais indicadores e informações "
            "sobre a atividade turística de Santa Rita do Sapucaí."
        ),
        "category": "Relatório anual",
        "year": 2026,
        "status": "published",
    },
    {
        "title": "Pesquisa de Perfil do Turista 2026",
        "description": (
            "Pesquisa demonstrativa sobre características, motivações e "
            "comportamento dos visitantes do município."
        ),
        "category": "Pesquisa",
        "year": 2026,
        "status": "published",
    },
    {
        "title": "Boletim do Turismo — 1º semestre de 2026",
        "description": (
            "Boletim demonstrativo com informações consolidadas sobre o "
            "setor turístico no primeiro semestre."
        ),
        "category": "Boletim",
        "year": 2026,
        "status": "published",
    },
    {
        "title": "Relatório Anual do Turismo 2025",
        "description": (
            "Síntese demonstrativa dos principais dados relacionados à "
            "atividade turística do município em 2025."
        ),
        "category": "Relatório anual",
        "year": 2025,
        "status": "published",
    },
    {
        "title": "Pesquisa de Perfil do Turista 2025",
        "description": (
            "Pesquisa demonstrativa sobre o perfil e as características dos "
            "visitantes de Santa Rita do Sapucaí."
        ),
        "category": "Pesquisa",
        "year": 2025,
        "status": "published",
    },
    {
        "title": "Estudo da Oferta Turística 2024",
        "description": (
            "Estudo demonstrativo sobre estabelecimentos, serviços e "
            "estrutura disponível para a atividade turística."
        ),
        "category": "Estudo",
        "year": 2024,
        "status": "published",
    },
    {
        "title": "Boletim do Turismo — 2º semestre de 2026",
        "description": (
            "Boletim em elaboração com informações referentes ao segundo semestre."
        ),
        "category": "Boletim",
        "year": 2026,
        "status": "draft",
    },
]


def seed_indicators(session: Session) -> None:
    repo = IndicatorRepository(session)
    service = IndicatorService(repo)

    for item in INDICATORS:
        slug = slugify(item["name"])

        if repo.get_by_slug_and_period(slug, item["period"]) is not None:
            continue

        indicator = service.create_indicator(
            IndicatorCreate(
                name=item["name"],
                sector=item["sector"],
                period=item["period"],
                value=item["value"],
                unit=item["unit"],
            )
        )

        if item["status"] == "published":
            service.change_status(indicator.id, IndicatorStatus.PUBLISHED)


def seed_reports(session: Session) -> None:
    for item in REPORTS:
        existing = session.scalar(
            select(Report).where(
                Report.title == item["title"],
                Report.year == item["year"],
            )
        )

        if existing is not None:
            continue

        report = create_report(
            session,
            ReportCreate(
                title=item["title"],
                description=item["description"],
                category=item["category"],
                year=item["year"],
            ),
        )

        if item["status"] == "published":
            publish_report(session, report.id)
