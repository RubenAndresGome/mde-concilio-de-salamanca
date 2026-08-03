"""
MDE History Writer — Generacion automatica de archivos PDCA en .mde_history/

Arquitectura 5S:
  1_seiri_sort/     → Material archivado (obsoleto)
  2_seiton_order/   → Archivos PDCA_NNN_Titulo.md (planes y sesiones)
  3_seiso_shine/    → Diffs y archivos afectados (codigo modificado)
  4_seiketsu_standardize/ → Instrucciones y convenciones
  5_shitsuke_sustain/ → Colas de tareas y metricas

Flujo interactivo:
  1. Skill completa una tarea
  2. Pregunta: "Guardar en .mde_history? [S/N/A]"
  3. Si S: genera PDCA_NNN_Titulo.md + actualiza _index.json
  4. Si N: solo registra metrica minima en _index.json
  5. Si A (Always): guarda esta y todas las futuras sin preguntar

Nomenclatura:
  PDCA_{NumeroDeHistorial}_{TituloPascalCase}.md
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


MDE_HISTORY_DIR = ".mde_history"
INDEX_FILE = "_index.json"
SEITON_DIR = "2_seiton_order"
SEISO_CHANGED = "3_seiso_shine/changed_files"
SHITSUKE_METRICS = "5_shitsuke_sustain/metrics"
DEFAULT_PROJECT = "concilio-salamanca"


class HistoryWriter:
    """Motor de escritura de documentacion MDE.

    Gestiona la generacion de archivos PDCA, actualizacion del _index.json
    y el prompt interactivo al finalizar tareas.
    """

    def __init__(self, project_root: Optional[str] = None):
        self.root = Path(project_root or os.getcwd())
        self.history_dir = self.root / MDE_HISTORY_DIR
        self.index_path = self.history_dir / INDEX_FILE
        self.seiton_dir = self.history_dir / SEITON_DIR
        self.seiso_dir = self.history_dir / SEISO_CHANGED
        self.shitsuke_dir = self.history_dir / SHITSUKE_METRICS
        self._ensuely_dirs()
        self._auto_save = self._load_always_flag()

    # ── Infraestructura ──────────────────────────────────────────────

    def _ensuely_dirs(self):
        for d in [
            self.history_dir,
            self.seiton_dir,
            self.seiso_dir,
            self.shitsuke_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> Dict[str, Any]:
        if self.index_path.exists():
            try:
                return json.loads(self.index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, KeyError):
                pass
        return {
            "project": DEFAULT_PROJECT,
            "version": "1.0.0",
            "directory_map": {
                "1_seiri_sort": "Material archivado u obsoleto",
                "2_seiton_order": "Planes y tareas (archivos PDCA)",
                "3_seiso_shine": "Codigo modificado (diffs, changed_files)",
                "4_seiketsu_standardize": "Instrucciones y convenciones",
                "5_shitsuke_sustain": "Colas de tareas y metricas",
                "veredictos": "Output de auditorias del Concilio",
            },
            "sessions": [],
            "cross_references": {},
            "pdca_counter": 0,
            "always_save": False,
            "metrics": {},
        }

    def _save_index(self, data: Dict[str, Any]):
        self.index_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    def _load_always_flag(self) -> bool:
        idx = self._load_index()
        return idx.get("always_save", False)

    # ── Contador PDCA ────────────────────────────────────────────────

    def get_next_pdca_number(self) -> int:
        idx = self._load_index()
        counter = idx.get("pdca_counter", 0) + 1
        idx["pdca_counter"] = counter
        self._save_index(idx)
        return counter

    # ── Plantilla PDCA Markdown ──────────────────────────────────────

    @staticmethod
    def _render_pdca_md(session: Dict[str, Any], pdca_num: int) -> str:
        """Genera el contenido markdown de un archivo PDCA."""
        pdca_id = f"PDCA_{pdca_num:03d}"
        title = session.get("title", session.get("summary", "Sin titulo"))[:80]

        lines = [
            f"# {pdca_id} — {title}",
            "",
            "| Campo | Valor |",
            "|---:|---|",
            f"| **ID Sesion** | `{session.get('id', '?')}` |",
            f"| **Fecha** | {session.get('timestamp', datetime.now().isoformat())} |",
            f"| **Accion** | {session.get('action', 'refactor')} |",
            f"| **Estado** | {session.get('status', 'completed')} |",
        ]
        if session.get("agents"):
            lines.append(f"| **Agentes activos** | {session['agents']} |")
        if session.get("tests"):
            lines.append(f"| **Tests** | {session['tests']} |")
        if session.get("tokens_used"):
            lines.append(f"| **Tokens usados** | ~{session['tokens_used']:,} |")
        if session.get("tools_installed"):
            lines.append(f"| **Herramientas** | {', '.join(session['tools_installed'])} |")

        lines += [
            "",
            "---",
            "",
            "## Plan (Objetivo)",
            "",
            session.get("plan", session.get("summary", "(no documentado)")),
            "",
            "---",
            "",
            "## Do (Implementacion)",
            "",
            session.get("do", session.get("summary", "(no documentado)")),
            "",
        ]

        if session.get("files_affected"):
            lines += [
                "### Archivos Afectados",
                "",
                "| Archivo | Accion |",
                "|---|---|",
            ]
            for f in session.get("files_affected", [])[:20]:
                lines.append(f"| `{f}` | modificado |")
            lines.append("")

        lines += [
            "---",
            "",
            "## Check (Validacion)",
            "",
            session.get("check", f"{session.get('tests', '?')} tests pasan. Outcome: {session.get('outcome', '?')}."),
            "",
        ]

        if session.get("syllogism"):
            lines += [
                "---",
                "",
                "## Syllogismus MDE",
                "",
                session["syllogism"],
                "",
            ]

        if session.get("act"):
            lines += [
                "---",
                "",
                "## Act (Refinamiento)",
                "",
                session["act"],
                "",
            ]

        lines += [
            "---",
            "",
            f"*Archivo generado automaticamente por MDE HistoryWriter el {datetime.now().strftime('%Y-%m-%d %H:%M')}.*",
            f"*PDCA counter: {pdca_num:03d}*",
        ]

        return "\n".join(lines)

    # ── Guardar Sesion ──────────────────────────────────────────────

    def save_session(
        self,
        session: Dict[str, Any],
        generate_pdca: bool = True,
        interactive: bool = False,
    ) -> Optional[str]:
        """Guarda una sesion en .mde_history/

        Args:
            session: Datos de la sesion (id, summary, files_affected, ...)
            generate_pdca: Si True, genera archivo PDCA en 2_seiton_order/
            interactive: Si True, pregunta al usuario si desea guardar

        Returns:
            Path del archivo PDCA generado, o None si no se genero.
        """
        if interactive and not self._auto_save:
            response = HistoryWriter.prompt_user(
                session.get("title", session.get("summary", "esta sesion")),
                session.get("tests"),
                len(session.get("files_affected", [])),
            )
            if response == "A":
                idx = self._load_index()
                idx["always_save"] = True
                self._save_index(idx)
                self._auto_save = True
            elif response == "N":
                self._record_minimal(session)
                return None

        # Generar PDCA markdown
        idx = self._load_index()
        pdca_num = self.get_next_pdca_number()
        title = session.get("title", session.get("summary", "Sesion"))
        title_slug = title.replace(" ", "_").replace("—", "-").replace(",", "").replace(":", "").replace("/", "_")[:80]

        md_path = None
        if generate_pdca:
            md_content = self._render_pdca_md(session, pdca_num)
            filename = f"PDCA_{pdca_num:03d}_{title_slug}.md"
            md_path = self.seiton_dir / filename
            md_path.write_text(md_content, encoding="utf-8")

        # Actualizar _index.json
        idx = self._load_index()
        idx["sessions"].append(session)
        idx["cross_references"][f"PDCA_{pdca_num:03d}"] = filename if generate_pdca else f"PDCA_{pdca_num:03d}"
        if session.get("tests"):
            idx["metrics"]["last_test_count"] = session["tests"]
        if session.get("agents"):
            idx["metrics"]["last_agent_count"] = session["agents"]
        self._save_index(idx)

        if md_path:
            print(f"  Documentacion generada: {md_path}")

        return str(md_path) if md_path else None

    def _record_minimal(self, session: Dict[str, Any]):
        idx = self._load_index()
        idx.setdefault("minimal_sessions", []).append({
            "timestamp": session.get("timestamp", datetime.now().isoformat()),
            "summary": session.get("summary", "?")[:200],
            "outcome": session.get("outcome", "?"),
        })
        idx["metrics"]["total_sessions_total"] = (
            len(idx["sessions"]) + len(idx.get("minimal_sessions", []))
        )
        self._save_index(idx)

    @staticmethod
    def prompt_user(title: str, tests: Optional[int] = None, files_count: int = 0) -> str:
        """Muestra prompt interactivo y retorna S, N, o A."""
        print()
        print("╔══════════════════════════════════════════════╗")
        tag = ""
        if tests:
            tag += f" {tests} tests"
        if files_count:
            tag += f", {files_count} archivos modificados"
        print(f"║  Tarea completada:{tag.ljust(44)}║")
        print(f"║  {title[:44].ljust(44)} ║")
        print("╠══════════════════════════════════════════════╣")
        print("║  Guardar en .mde_history?                     ║")
        print("║  [S] Si — generar PDCA y actualizar indice    ║")
        print("║  [N] No — continuar sin documentar            ║")
        print("║  [A] Siempre — esta y todas las futuras       ║")
        print("╚══════════════════════════════════════════════╝")
        try:
            choice = input("  > ").strip().upper()
            if choice in ("S", "A", "SÍ", "SI"):
                return "A" if choice == "A" else "S"
            return "N"
        except (EOFError, KeyboardInterrupt):
            return "N"

    # ── Batch: regenerar sesiones retroactivas ───────────────────────

    def retro_generate_all(self) -> int:
        """Genera archivos PDCA desde todas las sesiones existentes en _index.json."""
        idx = self._load_index()
        sessions = idx.get("sessions", [])
        if not sessions:
            return 0

        count = 0
        for session in sessions:
            success = self.retro_generate_one(session)
            if success:
                count += 1
        return count

    def retro_generate_one(self, session: Dict[str, Any]) -> bool:
        title = session.get("title", session.get("summary", "Sesion sin titulo"))
        title_slug = title.replace(" ", "_").replace("—", "-").replace(",", "").replace(":", "").replace("/", "_")[:80]

        pdca_num = self.get_next_pdca_number()
        md_content = self._render_pdca_md(session, pdca_num)
        filename = f"PDCA_{pdca_num:03d}_{title_slug}.md"
        md_path = self.seiton_dir / filename
        md_path.write_text(md_content, encoding="utf-8")

        idx = self._load_index()
        idx.setdefault("cross_references", {})
        idx["cross_references"][f"PDCA_{pdca_num:03d}"] = filename
        self._save_index(idx)
        return True

    # ── Utilidades ───────────────────────────────────────────────────

    def stats(self) -> str:
        idx = self._load_index()
        sessions = idx.get("sessions", [])
        minimal = idx.get("minimal_sessions", [])
        cross_refs = idx.get("cross_references", {})
        pdca_files = sorted(self.seiton_dir.glob("PDCA_*.md"))

        lines = [
            "=== .mde_history Stats ===",
            f"Proyecto:       {idx.get('project', '?')}",
            f"Version:        {idx.get('version', '?')}",
            f"Sesiones doc:   {len(sessions)} (con PDCA markdown)",
            f"Sesiones min:   {len(minimal)} (sin documentar)",
            f"PDCA generados: {len(pdca_files)} archivos",
            f"Cross-refs:     {len(cross_refs)} enlaces",
        ]
        for pdca in pdca_files[-5:]:
            lines.append(f"  -> {pdca.name} ({pdca.stat().st_size:,} bytes)")
        return "\n".join(lines)

    def verify_integrity(self) -> Dict[str, bool]:
        """Verifica integridad de .mde_history/"""
        checks = {
            "directorios_5s": all(
                (self.history_dir / d).is_dir()
                for d in ["1_seiri_sort", "2_seiton_order", "3_seiso_shine",
                          "4_seiketsu_standardize", "5_shitsuke_sustain",
                          "veredictos"]
            ),
            "index_json": self.index_path.exists(),
            "schema_json": (self.history_dir / "_schema.json").exists(),
            "cross_refs_ok": True,
            "pdca_validos": True,
        }
        # Validar cross-references
        idx = self._load_index()
        for ref, path in idx.get("cross_references", {}).items():
            fpath = self.seiton_dir / path
            if isinstance(path, str) and not fpath.exists():
                checks["cross_refs_ok"] = False
                break
        # Validar archivos PDCA
        for pdca_file in self.seiton_dir.glob("PDCA_*.md"):
            content = pdca_file.read_text(encoding="utf-8", errors="ignore")
            if "Plan (Objetivo)" not in content or "Do (Implementacion)" not in content:
                checks["pdca_validos"] = False
                break
        return checks
