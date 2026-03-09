"""Indice navigabile NTC18 — collega OCR, funzioni pyntc e riferimenti normativi.

Uso:
    >>> from pyntc.core.index import ntc18
    >>> section = ntc18["4.1.2.3.5.1"]
    >>> section.title
    'Elementi senza armature trasversali resistenti a taglio'
    >>> section.formulas
    ['[4.1.22]', '[4.1.23]']
    >>> section.pyntc_functions
    [FunctionRef(module='pyntc.checks.concrete', name='shear_resistance_no_stirrups', ...)]
    >>> ntc18.search("taglio")
    [Section("4.1.2.3.5"), Section("4.1.2.3.5.1"), ...]
"""

from __future__ import annotations

import importlib
import inspect
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FunctionRef:
    """Riferimento a una funzione pyntc."""

    module: str
    name: str
    article: str
    table: str | None = None
    formula: str | None = None
    signature: str = ""

    @property
    def qualname(self) -> str:
        return f"{self.module}.{self.name}"


@dataclass
class Section:
    """Sezione della norma NTC18."""

    number: str
    title: str = ""
    text_blocks: list[str] = field(default_factory=list)
    formulas: list[str] = field(default_factory=list)
    tables: list[str] = field(default_factory=list)
    captions: list[str] = field(default_factory=list)
    pyntc_functions: list[FunctionRef] = field(default_factory=list)
    children: list[str] = field(default_factory=list)
    parent: str | None = None

    @property
    def has_code(self) -> bool:
        """True se ci sono funzioni pyntc per questa sezione."""
        return len(self.pyntc_functions) > 0

    @property
    def depth(self) -> int:
        """Livello di nesting (es. '4.1.2.3' -> 4)."""
        return len(self.number.split("."))

    def summary(self) -> str:
        """Riassunto one-line della sezione."""
        parts = [f"§{self.number}"]
        if self.title:
            parts.append(self.title)
        if self.formulas:
            parts.append(f"{len(self.formulas)} formule")
        if self.tables:
            parts.append(f"{len(self.tables)} tabelle")
        if self.pyntc_functions:
            funcs = ", ".join(f.name for f in self.pyntc_functions)
            parts.append(f"pyntc: {funcs}")
        return " — ".join(parts)


class NTC18Index:
    """Indice navigabile della NTC 2018.

    Collega tre sorgenti:
    1. JSON OCR (ntc18_data/, opzionale) — testo, formule, tabelle della norma
    2. @ntc_ref decorators — link funzione → articolo
    3. Struttura gerarchica — parent/children tra sezioni
    """

    def __init__(self):
        self._sections: dict[str, Section] = {}
        self._functions: list[FunctionRef] = []
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            self._load_ocr_data()
            self._load_pyntc_refs()
            self._build_hierarchy()
            self._loaded = True

    def __getitem__(self, section_number: str) -> Section:
        """Accesso diretto: ntc18["4.1.2.3.5.1"]."""
        self._ensure_loaded()
        key = section_number.rstrip(".")
        if key not in self._sections:
            raise KeyError(f"Sezione §{key} non trovata nell'indice NTC18")
        return self._sections[key]

    def get(self, section_number: str, default=None) -> Section | None:
        """Accesso con default."""
        try:
            return self[section_number]
        except KeyError:
            return default

    def __contains__(self, section_number: str) -> bool:
        self._ensure_loaded()
        return section_number.rstrip(".") in self._sections

    def __len__(self) -> int:
        self._ensure_loaded()
        return len(self._sections)

    def __iter__(self):
        self._ensure_loaded()
        yield from sorted(
            self._sections.values(),
            key=lambda s: [int(p) for p in s.number.split(".")],
        )

    @property
    def sections(self) -> dict[str, Section]:
        self._ensure_loaded()
        return self._sections

    @property
    def functions(self) -> list[FunctionRef]:
        """Tutte le funzioni pyntc indicizzate."""
        self._ensure_loaded()
        return self._functions

    def search(self, query: str, include_text: bool = False) -> list[Section]:
        """Cerca sezioni per testo nel titolo (e opzionalmente nel body)."""
        self._ensure_loaded()
        query_lower = query.lower()
        results = []
        for section in self._sections.values():
            if query_lower in section.title.lower():
                results.append(section)
            elif include_text and any(query_lower in t.lower() for t in section.text_blocks):
                results.append(section)
        return sorted(results, key=lambda s: [int(p) for p in s.number.split(".")])

    def chapters(self) -> list[Section]:
        """Ritorna le sezioni di primo livello (capitoli)."""
        self._ensure_loaded()
        return [s for s in self._sections.values() if s.depth == 1]

    def functions_for_article(self, article: str) -> list[FunctionRef]:
        """Funzioni pyntc per un dato articolo (match esatto o prefisso)."""
        self._ensure_loaded()
        return [f for f in self._functions if f.article == article or f.article.startswith(article + ".")]

    def coverage(self) -> dict:
        """Statistiche di copertura pyntc sulla norma."""
        self._ensure_loaded()
        total = len(self._sections)
        with_code = sum(1 for s in self._sections.values() if s.has_code)
        with_formulas = sum(1 for s in self._sections.values() if s.formulas)
        with_tables = sum(1 for s in self._sections.values() if s.tables)
        return {
            "total_sections": total,
            "sections_with_code": with_code,
            "sections_with_formulas": with_formulas,
            "sections_with_tables": with_tables,
            "total_functions": len(self._functions),
            "coverage_pct": round(with_code / total * 100, 1) if total else 0,
        }

    # --- Caricamento dati ---

    def _load_ocr_data(self):
        """Carica e struttura i JSON OCR da ntc18_data/."""
        data_dir = Path(__file__).parent.parent.parent.parent / "ntc18_data"
        if not data_dir.exists():
            return

        current_section = None

        for json_file in sorted(data_dir.glob("cap*_page_*.json")):
            data = json.loads(json_file.read_text(encoding="utf-8"))

            for item in data:
                category = item.get("category", "")
                text = item.get("text", "")

                if category == "Section-header":
                    section_num = self._extract_section_number(text)
                    if section_num:
                        title = self._extract_title(text, section_num)
                        if section_num not in self._sections:
                            self._sections[section_num] = Section(
                                number=section_num, title=title
                            )
                        elif title and not self._sections[section_num].title:
                            self._sections[section_num].title = title
                        current_section = section_num

                elif category == "Text" and current_section and text.strip():
                    self._sections[current_section].text_blocks.append(text.strip())

                elif category == "Formula" and current_section:
                    self._sections[current_section].formulas.append(text.strip())

                elif category == "Table" and current_section:
                    self._sections[current_section].tables.append(text.strip())

                elif category == "Caption" and current_section:
                    self._sections[current_section].captions.append(text.strip())

    def _load_pyntc_refs(self):
        """Scansiona tutti i moduli pyntc per i decoratori @ntc_ref."""
        modules = [
            "pyntc.actions.loads",
            "pyntc.actions.wind",
            "pyntc.actions.snow",
            "pyntc.actions.seismic",
            "pyntc.actions.temperature",
            "pyntc.actions.fire",
            "pyntc.actions.combinations",
            "pyntc.checks.concrete",
            "pyntc.checks.steel",
            "pyntc.checks.timber",
            "pyntc.checks.masonry",
            "pyntc.checks.composite",
            "pyntc.checks.geotechnical",
            "pyntc.checks.bridges",
            "pyntc.checks.seismic_design",
            "pyntc.checks.existing_buildings",
        ]

        for mod_name in modules:
            try:
                mod = importlib.import_module(mod_name)
            except ImportError:
                continue

            for name, func in inspect.getmembers(mod, inspect.isfunction):
                if name.startswith("_"):
                    continue

                ref = getattr(func, "_ntc_ref", None)
                if not ref:
                    continue

                sig = str(inspect.signature(func))
                func_ref = FunctionRef(
                    module=mod_name,
                    name=name,
                    article=ref.article,
                    table=ref.table,
                    formula=ref.formula,
                    signature=sig,
                )
                self._functions.append(func_ref)

                # Collega alla sezione corrispondente
                article = ref.article
                if article in self._sections:
                    self._sections[article].pyntc_functions.append(func_ref)
                else:
                    # Crea sezione stub se non trovata nell'OCR
                    self._sections[article] = Section(number=article)
                    self._sections[article].pyntc_functions.append(func_ref)

    def _build_hierarchy(self):
        """Costruisce relazioni parent/children tra sezioni."""
        for number in list(self._sections.keys()):
            parts = number.split(".")
            if len(parts) > 1:
                parent_num = ".".join(parts[:-1])
                self._sections[number].parent = parent_num
                if parent_num in self._sections:
                    if number not in self._sections[parent_num].children:
                        self._sections[parent_num].children.append(number)

        # Ordina children
        for section in self._sections.values():
            section.children.sort(
                key=lambda x: [int(p) for p in x.split(".")]
            )

    @staticmethod
    def _extract_section_number(header_text: str) -> str | None:
        """Estrae il numero di sezione da un header OCR."""
        # Rimuovi markdown heading markers
        clean = re.sub(r"^#+\s*", "", header_text.strip())
        # Match section numbers like "4.1.2.3.5.1"
        m = re.match(r"([\d]+(?:\.[\d]+)*)", clean)
        if m:
            return m.group(1).rstrip(".")
        # Match "CAPITOLO X."
        m = re.match(r"CAPITOLO\s+(\d+)", clean, re.IGNORECASE)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def _extract_title(header_text: str, section_number: str) -> str:
        """Estrae il titolo dal testo dell'header, rimuovendo il numero."""
        clean = re.sub(r"^#+\s*", "", header_text.strip())
        # Rimuovi il numero di sezione e separatori
        clean = re.sub(
            r"^" + re.escape(section_number) + r"\.?\s*[-—.]?\s*",
            "",
            clean,
        )
        # Rimuovi "CAPITOLO X."
        clean = re.sub(r"^CAPITOLO\s+\d+\.?\s*", "", clean, flags=re.IGNORECASE)
        return clean.strip()


# Singleton — importa e usa direttamente
ntc18 = NTC18Index()
