#!/usr/bin/env python3
"""
build_vault.py - Genera un vault Obsidian dalle NTC18 (JSON OCR).

Uso:
    python scripts/build_vault.py
    python scripts/build_vault.py --vault-dir ~/Desktop/NTC18-vault
    python scripts/build_vault.py --data-dir ntc18_data --vault-dir ntc18-vault

Comportamento:
    - Idempotente: rilancia senza perdere modifiche manuali
    - Incrementale: aggiunge note per nuovi capitoli
    - Smart overwrite: rigenera solo note non modificate a mano (hash tracking)
"""

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

# ─── Defaults ────────────────────────────────────────────────────────

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "ntc18_data"
DEFAULT_VAULT_DIR = Path(__file__).resolve().parent.parent / "ntc18-vault"
HASH_FILE_NAME = ".vault_hashes.json"

# ─── Chapter titles ──────────────────────────────────────────────────

CHAPTER_TITLES = {
    1: "Oggetto",
    2: "Sicurezza e prestazioni attese",
    3: "Azioni sulle costruzioni",
    4: "Costruzioni civili e industriali",
    5: "Ponti",
    6: "Progettazione geotecnica",
    7: "Progettazione per azioni sismiche",
    8: "Costruzioni esistenti",
    9: "Collaudo statico",
    10: "Redazione dei progetti strutturali",
    11: "Materiali e prodotti per uso strutturale",
    12: "Riferimenti tecnici",
}

# ─── Regex ────────────────────────────────────────────────────────────

RE_SECTION_NUM = re.compile(
    r"^(?:#{1,5}\s*)?"          # optional markdown heading
    r"(\d+(?:\.\d+)*\.?)\s+"    # section number
    r"(.+)$",                   # title
)
RE_CHAPTER_HEADER = re.compile(r"CAPITOLO\s+\d+", re.IGNORECASE)
RE_FORMULA_NUM = re.compile(r"\[(\d+(?:\.\d+)*)\]")
RE_TABLE_CAPTION = re.compile(
    r"Tab\.?\s*(\d+(?:\.\d+)*(?:\.[IVXivx]+)?)\s*[-\u2013\u2014]\s*(.*)",
    re.IGNORECASE,
)
RE_FIGURE_CAPTION = re.compile(
    r"Fig\.?\s*(\d+(?:\.\d+)*)\s*[-\u2013\u2014]\s*(.*)",
    re.IGNORECASE,
)


# ─── Hash helpers ─────────────────────────────────────────────────────

def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def load_hashes(vault_dir: Path) -> dict:
    path = vault_dir / HASH_FILE_NAME
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_hashes(vault_dir: Path, hashes: dict):
    path = vault_dir / HASH_FILE_NAME
    path.write_text(json.dumps(hashes, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_write(filepath: Path, content: str, hashes: dict) -> str:
    """Write file only if new or not manually modified. Returns status string."""
    rel = filepath.as_posix()

    if filepath.exists():
        existing = filepath.read_text(encoding="utf-8")
        old_hash = hashes.get(rel)
        current_hash = _hash(existing)

        if old_hash and old_hash != current_hash:
            return "skipped"

        if existing == content:
            return "unchanged"

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    hashes[rel] = _hash(content)
    return "written"


# ─── Filename sanitization ───────────────────────────────────────────

def sanitize(name: str) -> str:
    name = name.replace("/", "-").replace("\\", "-")
    name = re.sub(r'[<>:"|?*]', "", name)
    return name.strip(". ")


# ─── JSON loading ─────────────────────────────────────────────────────

def load_chapter(data_dir: Path, cap: str) -> list[dict]:
    """Load all pages of a chapter in order, return flat element list."""
    files = sorted(
        data_dir.glob(f"{cap}_page_*.json"),
        key=lambda f: int(f.stem.split("_page_")[1]),
    )
    elements = []
    for f in files:
        page = json.loads(f.read_text(encoding="utf-8"))
        for el in page:
            if el["category"] not in ("Page-header", "Page-footer", "Picture"):
                elements.append(el)
    return elements


# ─── Section extraction ───────────────────────────────────────────────

def parse_header(text: str):
    """Return (section_number, title) or None."""
    if RE_CHAPTER_HEADER.search(text) and not re.search(r"\d+\.\d+", text):
        return None
    if text.startswith("**"):
        return None
    m = RE_SECTION_NUM.match(text)
    if m:
        num = m.group(1).rstrip(".")
        title = m.group(2).strip()
        return num, title
    return None


def extract_sections(elements: list[dict], cap_num: int) -> list[dict]:
    """Group elements into sections. Each section is a dict with metadata + content."""
    sections = []
    current = None
    pending_caption = None

    for el in elements:
        cat = el["category"]
        text = el.get("text", "")

        # ── New section header ──
        if cat == "Section-header":
            parsed = parse_header(text)
            if parsed:
                if current:
                    sections.append(current)
                num, title = parsed
                current = {
                    "number": num,
                    "title": title,
                    "chapter": cap_num,
                    "body": [],
                    "formulas": [],
                    "tables": [],
                    "figures": [],
                }
                pending_caption = None
                continue

        if current is None:
            continue

        # ── Caption (appears BEFORE the table/figure) ──
        if cat == "Caption":
            tm = RE_TABLE_CAPTION.match(text)
            fm = RE_FIGURE_CAPTION.match(text)
            if tm:
                pending_caption = {"ref": tm.group(1), "title": tm.group(2), "raw": text}
            elif fm:
                current["figures"].append({"ref": fm.group(1), "title": fm.group(2)})
            current["body"].append(el)
            continue

        # ── Table ──
        if cat == "Table":
            table_entry = {"html": text, "ref": None, "title": None}
            if pending_caption:
                table_entry["ref"] = pending_caption["ref"]
                table_entry["title"] = pending_caption["title"]
                pending_caption = None
            current["tables"].append(table_entry)
            current["body"].append(el)
            continue

        # ── Formula ──
        if cat == "Formula":
            fm = RE_FORMULA_NUM.search(text)
            current["formulas"].append({
                "text": text,
                "number": fm.group(1) if fm else None,
            })
            current["body"].append(el)
            continue

        # ── Footnote ──
        if cat == "Footnote":
            current["body"].append(el)
            continue

        # ── Text / List-item ──
        current["body"].append(el)

    if current:
        sections.append(current)

    return sections


# ─── Markdown generation ──────────────────────────────────────────────

def el_to_md(el: dict) -> str:
    cat = el["category"]
    text = el.get("text", "")
    if cat == "Formula":
        return f"\n{text}\n"
    if cat == "Table":
        return f"\n{text}\n"
    if cat == "Caption":
        return f"\n*{text}*\n"
    if cat == "Footnote":
        return f"\n> [!note] Nota\n> {text}\n"
    return text


def _section_link(number: str, section_map: dict[str, str]) -> str:
    """Build a wikilink to a section using its full note name."""
    title = section_map.get(number)
    if title:
        return f"[[§{number} - {title}|§{number}]]"
    return f"[[§{number}]]"


def make_section_note(s: dict, section_map: dict[str, str],
                      formula_map: dict[str, list[str]] | None = None) -> str:
    lines = ["---"]
    lines.append("tipo: sezione")
    lines.append(f"capitolo: {s['chapter']}")
    lines.append(f"sezione: \"{s['number']}\"")
    lines.append(f"titolo: \"{s['title']}\"")

    f_refs = [f["number"] for f in s["formulas"] if f["number"]]
    t_refs = [t["ref"] for t in s["tables"] if t.get("ref")]
    if f_refs:
        lines.append(f"formule: {json.dumps(f_refs)}")
    if t_refs:
        lines.append(f"tabelle: {json.dumps(t_refs)}")
    lines.append("---")
    lines.append("")

    # Heading
    lines.append(f"# \u00a7{s['number']} \u2014 {s['title']}")
    lines.append("")

    # Navigation: parent + children
    parts = s["number"].split(".")
    if len(parts) > 2:
        parent = ".".join(parts[:-1])
        lines.append(f"Sezione padre: {_section_link(parent, section_map)}")
        lines.append("")

    # Direct children (e.g. for 3.3 -> 3.3.1, 3.3.2, ... but not 3.3.1.1)
    prefix = s["number"] + "."
    children = sorted(
        [(num, title) for num, title in section_map.items()
         if num.startswith(prefix) and num.count(".") == s["number"].count(".") + 1],
        key=lambda x: [int(p) for p in x[0].split(".")],
    )
    if children:
        lines.append("**Sotto-sezioni:**")
        for c_num, c_title in children:
            lines.append(f"- [[§{c_num} - {c_title}]]")
        lines.append("")

        # Formulario only for level x.x (e.g. 3.3, 3.5) — not deeper
        is_parent_level = s["number"].count(".") == 1
        if is_parent_level and formula_map:
            descendant_formulas = sorted(
                [fnum for sec_num, fnums in formula_map.items()
                 if sec_num.startswith(prefix) for fnum in fnums],
                key=lambda x: [int(p) for p in x.split(".")],
            )
            if descendant_formulas:
                lines.append("**Formulario:**")
                for fnum in descendant_formulas:
                    lines.append(f"![[Formula {fnum}]]")
                lines.append("")

    # Body
    for el in s["body"]:
        md = el_to_md(el)
        if md:
            lines.append(md)
    lines.append("")

    # Cross-references (no formulas — they are already in the body text)
    if t_refs or s["figures"]:
        lines.append("---")
        lines.append("## Riferimenti")
        lines.append("")
        if t_refs:
            lines.append("**Tabelle:**")
            for ref in t_refs:
                lines.append(f"- [[Tab {ref}]]")
            lines.append("")
        if s["figures"]:
            lines.append("**Figure:**")
            for fig in s["figures"]:
                lines.append(f"- Fig. {fig['ref']} \u2014 {fig['title']}")
            lines.append("")

    return "\n".join(lines)


def make_table_note(t: dict, section_num: str, section_map: dict[str, str]) -> str:
    ref = t.get("ref", "?")
    title = t.get("title", "")
    lines = ["---"]
    lines.append("tipo: tabella")
    lines.append(f"riferimento: \"Tab {ref}\"")
    lines.append(f"sezione: \"{section_num}\"")
    lines.append(f"titolo: \"{title}\"")
    lines.append("---")
    lines.append("")
    lines.append(f"# Tab {ref} \u2014 {title}")
    lines.append("")
    lines.append(f"Sezione: {_section_link(section_num, section_map)}")
    lines.append("")
    if t.get("html"):
        lines.append(t["html"])
        lines.append("")
    return "\n".join(lines)


def make_formula_note(f: dict, section_num: str, section_map: dict[str, str]) -> str:
    num = f["number"]
    section_title = section_map.get(section_num, "")
    lines = ["---"]
    lines.append("tipo: formula")
    lines.append(f"riferimento: \"{num}\"")
    lines.append(f"sezione: \"{section_num}\"")
    lines.append("---")
    lines.append("")
    lines.append(f"# Formula [{num}] \u2014 {section_title}")
    lines.append("")
    lines.append(f"Sezione: {_section_link(section_num, section_map)}")
    lines.append("")
    lines.append(f"{f['text']}")
    lines.append("")
    return "\n".join(lines)


# ─── pyntc notes from @ntc_ref ───────────────────────────────────────

def extract_ntc_refs(src_dir: Path) -> list[dict]:
    refs = []
    for py_file in sorted(src_dir.rglob("*.py")):
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for dec in node.decorator_list:
                if not isinstance(dec, ast.Call):
                    continue
                func = dec.func
                name = getattr(func, "id", None) or getattr(func, "attr", None)
                if name != "ntc_ref":
                    continue
                kwargs = {}
                for kw in dec.keywords:
                    if isinstance(kw.value, ast.Constant):
                        kwargs[kw.arg] = kw.value.value

                docstring = ast.get_docstring(node) or ""
                first_line = docstring.split("\n")[0].strip()

                refs.append({
                    "function": node.name,
                    "file": py_file.relative_to(src_dir.parent.parent).as_posix(),
                    "module": py_file.stem,
                    "article": kwargs.get("article", ""),
                    "table": kwargs.get("table"),
                    "formula": kwargs.get("formula"),
                    "docstring": first_line,
                })
    return refs


def make_pyntc_note(ref: dict, section_map: dict[str, str]) -> str:
    lines = ["---"]
    lines.append("tipo: pyntc")
    lines.append(f"funzione: \"{ref['function']}\"")
    lines.append(f"modulo: \"{ref['module']}\"")
    lines.append(f"file: \"{ref['file']}\"")
    lines.append(f"articolo: \"{ref['article']}\"")
    if ref["table"]:
        lines.append(f"tabella: \"{ref['table']}\"")
    if ref["formula"]:
        lines.append(f"formula: \"{ref['formula']}\"")
    lines.append("---")
    lines.append("")
    lines.append(f"# `{ref['function']}()`")
    lines.append("")
    lines.append(f"> {ref['docstring']}")
    lines.append("")
    lines.append(f"**File:** `{ref['file']}`")
    lines.append("")
    lines.append("## Riferimenti NTC18")
    lines.append("")
    lines.append(f"- Sezione: {_section_link(ref['article'], section_map)}")
    if ref["table"]:
        tab_ref = ref["table"].replace("Tab.", "Tab ").strip()
        lines.append(f"- Tabella: [[{tab_ref}]]")
    if ref["formula"]:
        lines.append(f"- Formula: [[Formula {ref['formula']}]]")
    lines.append("")
    return "\n".join(lines)


# ─── Map of Content ──────────────────────────────────────────────────

def make_moc(sections_by_cap: dict[int, list[dict]], pyntc_refs: list[dict]) -> str:
    lines = ["---", "tipo: moc", "---", ""]
    lines.append("# Indice NTC18")
    lines.append("")
    lines.append("> D.M. 17 gennaio 2018 \u2014 Aggiornamento delle "
                 "\u00abNorme tecniche per le costruzioni\u00bb")
    lines.append("")

    for cap_num in sorted(sections_by_cap):
        cap_title = CHAPTER_TITLES.get(cap_num, "")
        lines.append(f"## Capitolo {cap_num} \u2014 {cap_title}")
        lines.append("")

        def sort_key(s):
            try:
                return [int(p) for p in s["number"].split(".")]
            except ValueError:
                return [0]

        for s in sorted(sections_by_cap[cap_num], key=sort_key):
            depth = len(s["number"].split(".")) - 2
            indent = "  " * max(depth, 0)
            fname = sanitize(f"\u00a7{s['number']} - {s['title']}")
            lines.append(
                f"{indent}- [[\u00a7{s['number']} - {s['title']}"
                f"|\u00a7{s['number']} {s['title']}]]"
            )
        lines.append("")

    # pyntc coverage table
    if pyntc_refs:
        lines.append("## Copertura pyntc")
        lines.append("")
        lines.append("| Funzione | Articolo | Modulo |")
        lines.append("|----------|----------|--------|")
        for ref in pyntc_refs:
            lines.append(
                f"| [[{ref['function']}]] "
                f"| \u00a7{ref['article']} "
                f"| `{ref['module']}` |"
            )
        lines.append("")

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────

def build_vault(data_dir: Path, vault_dir: Path, src_dir: Path | None = None):
    print(f"Data dir:  {data_dir}")
    print(f"Vault dir: {vault_dir}")
    print()

    vault_dir.mkdir(parents=True, exist_ok=True)
    hashes = load_hashes(vault_dir)
    stats = {"written": 0, "unchanged": 0, "skipped": 0}

    def track(status: str):
        key = status.split()[0] if " " in status else status
        stats[key] = stats.get(key, 0) + 1

    # Discover chapters
    caps = sorted(
        {f.stem.split("_page_")[0] for f in data_dir.glob("cap*_page_*.json")},
        key=lambda c: int(c.replace("cap", "")),
    )
    if not caps:
        print("Nessun file JSON trovato in", data_dir)
        return

    print(f"Capitoli trovati: {', '.join(caps)}\n")

    sections_by_cap: dict[int, list[dict]] = {}
    all_tables = []
    all_formulas = []

    # ── Parse all chapters first (build section_map) ────────────────
    for cap in caps:
        cap_num = int(cap.replace("cap", ""))
        elements = load_chapter(data_dir, cap)
        sections = extract_sections(elements, cap_num)
        sections_by_cap[cap_num] = sections

    # section_map: number -> title (needed for wikilinks)
    # formula_map: number -> [formula numbers] (for parent embedding)
    section_map: dict[str, str] = {}
    formula_map: dict[str, list[str]] = {}
    for cap_sections in sections_by_cap.values():
        for s in cap_sections:
            section_map[s["number"]] = s["title"]
            own_formulas = [f["number"] for f in s["formulas"] if f["number"]]
            if own_formulas:
                formula_map[s["number"]] = own_formulas

    # ── Write notes ──────────────────────────────────────────────────
    for cap_num in sorted(sections_by_cap):
        n_tables = 0
        n_formulas = 0

        for s in sections_by_cap[cap_num]:
            # Write section note
            fname = sanitize(f"\u00a7{s['number']} - {s['title']}.md")
            path = vault_dir / "01 - Capitoli" / fname
            track(safe_write(path, make_section_note(s, section_map, formula_map), hashes))

            # Collect tables
            for t in s["tables"]:
                if t.get("ref"):
                    t["_section"] = s["number"]
                    all_tables.append(t)
                    n_tables += 1

            # Collect formulas
            for f in s["formulas"]:
                if f["number"]:
                    f["_section"] = s["number"]
                    all_formulas.append(f)
                    n_formulas += 1

        print(f"Cap {cap_num}: {len(sections_by_cap[cap_num])} sezioni, "
              f"{n_tables} tabelle, {n_formulas} formule")

    # ── Table notes ───────────────────────────────────────────────────
    seen_tables = set()
    for t in all_tables:
        ref = t["ref"]
        if ref in seen_tables:
            continue
        seen_tables.add(ref)
        fname = sanitize(f"Tab {ref}.md")
        path = vault_dir / "02 - Tabelle" / fname
        track(safe_write(path, make_table_note(t, t["_section"], section_map), hashes))
    print(f"\nTabelle: {len(seen_tables)} note")

    # ── Formula notes ─────────────────────────────────────────────────
    seen_formulas = set()
    for f in all_formulas:
        num = f["number"]
        if num in seen_formulas:
            continue
        seen_formulas.add(num)
        fname = sanitize(f"Formula {num}.md")
        path = vault_dir / "03 - Formule" / fname
        track(safe_write(path, make_formula_note(f, f["_section"], section_map), hashes))
    print(f"Formule: {len(seen_formulas)} note")

    # ── pyntc notes ───────────────────────────────────────────────────
    pyntc_refs = []
    if src_dir and src_dir.exists():
        pyntc_refs = extract_ntc_refs(src_dir)
        for ref in pyntc_refs:
            fname = sanitize(f"{ref['function']}.md")
            path = vault_dir / "04 - pyntc" / fname
            track(safe_write(path, make_pyntc_note(ref, section_map), hashes))
        print(f"pyntc: {len(pyntc_refs)} note")

    # ── MOC ───────────────────────────────────────────────────────────
    moc_path = vault_dir / "00 - Indice" / "Indice NTC18.md"
    track(safe_write(moc_path, make_moc(sections_by_cap, pyntc_refs), hashes))

    # ── Save hashes & summary ─────────────────────────────────────────
    save_hashes(vault_dir, hashes)

    print(f"\n{'=' * 40}")
    print(f"  Scritte:   {stats.get('written', 0)}")
    print(f"  Invariate: {stats.get('unchanged', 0)}")
    print(f"  Saltate:   {stats.get('skipped', 0)} (modificate a mano)")
    print(f"{'=' * 40}")


def main():
    parser = argparse.ArgumentParser(
        description="Build NTC18 Obsidian vault from OCR JSON",
    )
    parser.add_argument(
        "--data-dir", type=Path, default=DEFAULT_DATA_DIR,
        help="Directory with JSON OCR files (default: ntc18_data/)",
    )
    parser.add_argument(
        "--vault-dir", type=Path, default=DEFAULT_VAULT_DIR,
        help="Output Obsidian vault directory (default: ntc18-vault/)",
    )
    parser.add_argument(
        "--src-dir", type=Path, default=None,
        help="pyntc source dir (auto-detected if omitted)",
    )
    args = parser.parse_args()

    src_dir = args.src_dir
    if src_dir is None:
        candidate = Path(__file__).resolve().parent.parent / "src" / "pyntc"
        if candidate.exists():
            src_dir = candidate

    build_vault(args.data_dir, args.vault_dir, src_dir)


if __name__ == "__main__":
    main()
