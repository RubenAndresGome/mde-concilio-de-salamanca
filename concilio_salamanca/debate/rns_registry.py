"""
Registro de Licencias Rerum Novarum Statuto (RNS).

Proporciona:
- Registro de proyectos que adoptan RNS
- Calculo de precios (tabla plana + BME)
- Emision de Bulas
- Badge RNS Licensed
- Reportes de contribucion al Fondo de Sostenibilidad

Uso:
    from concilio_salamanca.debate.rns_registry import RenerumRegistry

    registry = RenerumRegistry()
    registry.register_project("Mi Proyecto", "https://github.com/user/project")
    price = registry.calculate_price("corp", annual_revenue=5_000_000)
    bula = registry.issue_bula("corp-123", "Mi Proyecto")
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


REGISTRY_FILE = "rns_registry.json"
ORPHAN_FUND_RATE = 0.05


@dataclass
class ProjectRegistration:
    project_id: str
    project_name: str
    repo_url: str
    license_type: str = "rns"  # "rns" | "dual-mit-rns"
    registered_at: str = ""
    adopters: List[str] = field(default_factory=list)  # company names
    total_contributions_usd: float = 0.0


@dataclass
class Bula:
    bula_id: str
    holder_name: str
    project_id: str
    issued_at: str
    expires_at: str
    price_usd: float
    tier: str
    is_std: bool = False


@dataclass
class LicensePayment:
    payment_id: str
    payer_name: str
    project_id: str
    amount_usd: float
    orphan_contribution: float
    paid_at: str
    payment_method: str = "stripe"


FLAT_PRICE_TABLE: list = [
    (0, 100_000, 0, "Open Source gratuito"),
    (100_000, 1_000_000, 500, "Licencia Individual/Startup"),
    (1_000_000, 10_000_000, 2_500, "Licencia PYME"),
    (10_000_000, 100_000_000, 10_000, "Licencia Corporativa"),
    (100_000_000, 1_000_000_000, 50_000, "Licencia Enterprise"),
    (1_000_000_000, float("inf"), 0.001, "Licencia Oligarca (0.1% facturacion)"),
]


class RenerumRegistry:
    """Registro central de proyectos RNS, licencias, Bulas y pagos."""

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.getcwd()
        self._projects: Dict[str, ProjectRegistration] = {}
        self._bulas: Dict[str, Bula] = {}
        self._payments: List[LicensePayment] = []
        self._load()

    # ── Persistencia ────────────────────────────────────────────────

    def _path(self) -> Path:
        return Path(self.data_dir) / REGISTRY_FILE

    def _load(self):
        p = self._path()
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                for pid, prj in data.get("projects", {}).items():
                    self._projects[pid] = ProjectRegistration(**prj)
                for bid, bula in data.get("bulas", {}).items():
                    self._bulas[bid] = Bula(**bula)
                for pmt in data.get("payments", []):
                    self._payments.append(LicensePayment(**pmt))
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self):
        data = {
            "projects": {k: v.__dict__ for k, v in self._projects.items()},
            "bulas": {k: v.__dict__ for k, v in self._bulas.items()},
            "payments": [p.__dict__ for p in self._payments],
        }
        self._path().write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    # ── Proyectos ───────────────────────────────────────────────────

    def register_project(
        self, name: str, repo_url: str, license_type: str = "rns"
    ) -> ProjectRegistration:
        pid = name.lower().replace(" ", "-").replace("/", "-")
        if pid in self._projects:
            return self._projects[pid]
        prj = ProjectRegistration(
            project_id=pid,
            project_name=name,
            repo_url=repo_url,
            license_type=license_type,
            registered_at=datetime.now().isoformat(),
        )
        self._projects[pid] = prj
        self._save()
        return prj

    def list_projects(self) -> List[ProjectRegistration]:
        return list(self._projects.values())

    def get_project(self, project_id: str) -> Optional[ProjectRegistration]:
        return self._projects.get(project_id)

    # ── Precios ─────────────────────────────────────────────────────

    @staticmethod
    def calculate_price(
        annual_revenue: float, use_bme: bool = False, bme_value: Optional[float] = None
    ) -> dict:
        """Calcula el precio de licencia segun tabla plana o BME.

        Args:
            annual_revenue: Facturacion anual USD.
            use_bme: Si True, usa el sistema BME en lugar de tabla plana.
            bme_value: Valor BME del usuario (solo si use_bme=True).

        Returns:
            dict con price_usd, tier, orphan_contribution.
        """
        # Tabla plana (default)
        for lo, hi, price, name in FLAT_PRICE_TABLE:
            if lo <= annual_revenue < hi:
                if isinstance(price, float) and price < 1:
                    price = max(annual_revenue * price, 100_000)
                orphan = round(price * ORPHAN_FUND_RATE, 2)
                return {"price_usd": round(price, 2), "tier": name, "orphan_contribution": orphan}

        return {"price_usd": 0, "tier": "Gratis", "orphan_contribution": 0}

    # ── Bulas ───────────────────────────────────────────────────────

    def issue_bula(
        self, holder_name: str, project_id: str, annual_revenue: float
    ) -> Optional[Bula]:
        """Emite una Bula de 7 anos para un proyecto."""
        project = self._projects.get(project_id)
        if not project:
            return None

        pricing = self.calculate_price(annual_revenue)
        if pricing["price_usd"] == 0:
            return None  # No se emite Bula para uso gratuito

        bid = f"bula-{project_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        now = datetime.now()
        bula = Bula(
            bula_id=bid,
            holder_name=holder_name,
            project_id=project_id,
            issued_at=now.isoformat(),
            expires_at=(now + timedelta(days=365 * 7)).isoformat(),
            price_usd=pricing["price_usd"],
            tier=pricing["tier"],
        )
        self._bulas[bid] = bula
        self._save()
        return bula

    def list_bulas(self) -> List[Bula]:
        return list(self._bulas.values())

    # ── Pagos ───────────────────────────────────────────────────────

    def record_payment(
        self,
        payer_name: str,
        project_id: str,
        amount_usd: float,
        method: str = "stripe",
    ) -> LicensePayment:
        pid = f"pay-{project_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        orphan = round(amount_usd * ORPHAN_FUND_RATE, 2)
        payment = LicensePayment(
            payment_id=pid,
            payer_name=payer_name,
            project_id=project_id,
            amount_usd=amount_usd,
            orphan_contribution=orphan,
            paid_at=datetime.now().isoformat(),
            payment_method=method,
        )
        self._payments.append(payment)

        # Actualizar contribuciones del proyecto
        if project_id in self._projects:
            self._projects[project_id].total_contributions_usd += amount_usd
            if payer_name not in self._projects[project_id].adopters:
                self._projects[project_id].adopters.append(payer_name)

        self._save()
        return payment

    def list_payments(self, project_id: Optional[str] = None) -> List[LicensePayment]:
        if project_id:
            return [p for p in self._payments if p.project_id == project_id]
        return self._payments

    # ── Reportes ────────────────────────────────────

    def orphan_fund_total(self) -> float:
        return sum(p.orphan_contribution for p in self._payments)

    def project_contributions(self, project_id: str) -> float:
        return self._projects[project_id].total_contributions_usd if project_id in self._projects else 0.0

    def format_badge(self, project_id: str) -> str:
        """Genera el badge markdown 'RNS Licensed'."""
        project = self._projects.get(project_id)
        if not project:
            return ""
        adopters = len(project.adopters)
        total = project.total_contributions_usd
        return (
            f"[![RNS Licensed](https://img.shields.io/badge/License-Rerum_Novarum_4.1-purple.svg)](LICENSE.md)\n"
            f"[![{adopters} adopters](https://img.shields.io/badge/adopters-{adopters}-blue.svg)](rns_registry.json)\n"
            f"[![${total:,.0f} in contributions](https://img.shields.io/badge/contributions-${total:,.0f}-green.svg)]"
        )

    def summary(self) -> str:
        lines = ["=== RERUM NOVARUM REGISTRY ===", ""]
        lines.append(f"Proyectos registrados: {len(self._projects)}")
        lines.append(f"Bulas emitidas: {len(self._bulas)}")
        lines.append(f"Pagos registrados: {len(self._payments)}")
        lines.append(f"Fondo de Sostenibilidad: ${self.orphan_fund_total():,.2f}")
        lines.append("")
        for pid, prj in self._projects.items():
            lines.append(f"  {prj.project_name:30s} adopters={len(prj.adopters):3d}  contrib=${prj.total_contributions_usd:>8,.2f}")
        return "\n".join(lines)
