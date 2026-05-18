import ast
import json
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand


ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = ROOT_DIR / "lumra_config"
TEMPLATE_DIR = APP_DIR / "templates"
URL_DIR = APP_DIR / "urls"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "wireframe_output"


def slugify(value: str) -> str:
    cleaned = []
    previous_was_sep = False
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
            previous_was_sep = False
        elif not previous_was_sep:
            cleaned.append("_")
            previous_was_sep = True
    slug = "".join(cleaned).strip("_")
    return slug or "page"


def dotted_module(path: Path) -> str:
    relative = path.relative_to(ROOT_DIR).with_suffix("")
    return ".".join(relative.parts)


def read_structure_stats(structure_file: Path) -> dict:
    if not structure_file.exists():
        return {}
    try:
        payload = json.loads(structure_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    stats = payload.get("stats") or {}
    return {
        "component_total": stats.get("total_components"),
        "interactive_total": stats.get("interactive"),
        "issue_total": stats.get("issues"),
        "scroll_nesting_total": stats.get("scroll_nestings"),
    }


class RenderCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.renders = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "render":
            template_name = None
            context_keys = []
            context_expression = ""
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
                template_name = node.args[1].value
            if len(node.args) >= 3:
                context_keys = extract_context_keys(node.args[2])
                context_expression = ast.unparse(node.args[2]) if hasattr(ast, "unparse") else ""
            self.renders.append(
                {
                    "template_name": template_name,
                    "context_keys": context_keys,
                    "context_expression": context_expression,
                    "line": node.lineno,
                }
            )
        self.generic_visit(node)


def extract_context_keys(node) -> list[str]:
    if isinstance(node, ast.Dict):
        keys = []
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.append(key.value)
        return sorted(set(keys))
    return []


def decorator_names(function_node: ast.FunctionDef) -> list[str]:
    names = []
    for decorator in function_node.decorator_list:
        if isinstance(decorator, ast.Name):
            names.append(decorator.id)
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                names.append(decorator.func.id)
            elif isinstance(decorator.func, ast.Attribute):
                names.append(decorator.func.attr)
        elif isinstance(decorator, ast.Attribute):
            names.append(decorator.attr)
    return names


def function_signals(function_node: ast.FunctionDef) -> dict:
    signals = {
        "uses_get": False,
        "uses_post": False,
        "queries_models": False,
        "uses_json": False,
        "has_branching": False,
    }
    for child in ast.walk(function_node):
        if isinstance(child, ast.Attribute) and isinstance(child.value, (ast.Attribute, ast.Name)):
            if child.attr == "objects":
                signals["queries_models"] = True
        elif isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
            if child.value.id == "request" and child.attr == "GET":
                signals["uses_get"] = True
            if child.value.id == "request" and child.attr == "POST":
                signals["uses_post"] = True
            if child.value.id == "json" and child.attr == "dumps":
                signals["uses_json"] = True
        elif isinstance(child, (ast.If, ast.Match, ast.Try)):
            signals["has_branching"] = True
    return signals


def scan_view_file(view_file: Path) -> list[dict]:
    source = view_file.read_text(encoding="utf-8")
    source_lines = source.splitlines()
    tree = ast.parse(source, filename=str(view_file))
    module_name = dotted_module(view_file)
    matches = []

    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        visitor = RenderCallVisitor()
        visitor.visit(node)
        if not visitor.renders:
            continue

        signals = function_signals(node)
        for render_call in visitor.renders:
            if not render_call["template_name"]:
                continue
            matches.append(
                {
                    "template_name": render_call["template_name"],
                    "view_name": node.name,
                    "view_module": module_name,
                    "view_file": str(view_file.relative_to(ROOT_DIR)).replace("\\", "/"),
                    "line": render_call["line"],
                    "decorators": decorator_names(node),
                    "context_keys": render_call["context_keys"],
                    "context_expression": render_call["context_expression"],
                    "signals": signals,
                    "source_excerpt": extract_source_excerpt(source_lines, node),
                }
            )
    return matches


def extract_source_excerpt(source_lines: list[str], function_node: ast.FunctionDef) -> str:
    start = max(function_node.lineno - 1, 0)
    end = getattr(function_node, "end_lineno", function_node.lineno)
    snippet = source_lines[start:end]
    return "\n".join(snippet).strip()


def collect_view_templates() -> dict[str, list[dict]]:
    template_map = defaultdict(list)
    view_files = set(APP_DIR.glob("views/*.py"))
    view_files.update(APP_DIR.rglob("views.py"))
    view_files.add(APP_DIR / "views.py")

    for view_file in sorted(path for path in view_files if path.exists()):
        for item in scan_view_file(view_file):
            template_map[item["template_name"]].append(item)

    for template_name, entries in list(template_map.items()):
        deduped = []
        seen = set()
        for entry in entries:
            marker = (entry["view_module"], entry["view_name"], entry["line"], entry["template_name"])
            if marker in seen:
                continue
            seen.add(marker)
            deduped.append(entry)
        template_map[template_name] = deduped
    return template_map


def import_alias_map(tree: ast.AST) -> dict[str, str]:
    aliases = {}
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        for alias in node.names:
            aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return aliases


def literal_keyword(call_node: ast.Call, keyword_name: str) -> str:
    for keyword in call_node.keywords:
        if keyword.arg == keyword_name and isinstance(keyword.value, ast.Constant):
            return keyword.value.value
    return ""


def resolve_view_ref(node, aliases: dict[str, str]) -> tuple[str, str]:
    if isinstance(node, ast.Name):
        dotted = aliases.get(node.id, node.id)
        return node.id, dotted
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        dotted = f"{aliases.get(node.value.id, node.value.id)}.{node.attr}"
        return node.attr, dotted
    return "", ""


def collect_url_routes() -> dict[str, list[dict]]:
    routes = defaultdict(list)
    for url_file in sorted(URL_DIR.glob("*.py")):
        source = url_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(url_file))
        aliases = import_alias_map(tree)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name) or node.func.id != "path":
                continue
            if len(node.args) < 2:
                continue
            if not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                continue

            route = node.args[0].value
            view_name, view_dotted = resolve_view_ref(node.args[1], aliases)
            if not view_name:
                continue

            routes[view_dotted].append(
                {
                    "route": route,
                    "url_name": literal_keyword(node, "name"),
                    "url_file": str(url_file.relative_to(ROOT_DIR)).replace("\\", "/"),
                    "view_name": view_name,
                }
            )
    return routes


def classify_template(template_rel: str, view_entries: list[dict], structure_stats: dict) -> dict:
    name = Path(template_rel).name.lower()
    signals = {
        "has_form": "form" in name,
        "has_detail": "detail" in name,
        "has_list": "list" in name,
        "has_report": "report" in name,
        "has_print": "print" in name,
    }

    score = 0
    if any(entry["signals"]["uses_post"] for entry in view_entries):
        score += 3
    if any(entry["signals"]["queries_models"] for entry in view_entries):
        score += 2
    if any(entry["signals"]["has_branching"] for entry in view_entries):
        score += 1
    if signals["has_form"] or signals["has_detail"]:
        score += 2
    if signals["has_report"] or signals["has_print"]:
        score += 2
    if structure_stats.get("component_total", 0) and structure_stats["component_total"] > 40:
        score += 1

    if score <= 1:
        batch = "batch_1_static"
        reason = "Static page or light context, aman untuk mulai round-trip."
    elif score <= 3:
        batch = "batch_2_listing"
        reason = "Listing atau dashboard ringan dengan context sederhana."
    elif score <= 5:
        batch = "batch_3_forms"
        reason = "Form atau halaman detail dengan context/logika menengah."
    else:
        batch = "batch_4_complex"
        reason = "Report/print/logic-heavy page, cocok setelah fondasi stabil."

    return {
        "score": score,
        "batch": batch,
        "reason": reason,
        "signals": signals,
    }


def template_entry(template_file: Path, view_map: dict, route_map: dict, output_dir: Path) -> dict:
    relative_template = str(template_file.relative_to(TEMPLATE_DIR)).replace("\\", "/")
    structure_file = output_dir / f"structure_{slugify(template_file.stem)}.json"
    structure_stats = read_structure_stats(structure_file)
    views = view_map.get(relative_template, [])

    resolved_routes = []
    for view in views:
        resolved_routes.extend(route_map.get(view["view_module"] + "." + view["view_name"], []))

    classification = classify_template(relative_template, views, structure_stats)
    return {
        "template_name": relative_template,
        "template_file": str(template_file.relative_to(ROOT_DIR)).replace("\\", "/"),
        "module_area": template_file.parent.name,
        "reverse_artifacts": {
            "structure_json": str(structure_file.relative_to(ROOT_DIR)).replace("\\", "/") if structure_file.exists() else "",
            "wireframe_html": f"wireframe_output/wireframe_{slugify(template_file.stem)}.html",
            "wireframe_png": f"wireframe_output/wireframe_{slugify(template_file.stem)}.png",
        },
        "views": views,
        "routes": resolved_routes,
        "structure_stats": structure_stats,
        "forward_batch": classification["batch"],
        "batch_reason": classification["reason"],
        "complexity_score": classification["score"],
        "signals": classification["signals"],
    }


def load_structure_payload(structure_file: Path) -> dict:
    if not structure_file.exists():
        return {}
    try:
        return json.loads(structure_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def collect_template_highlights(entry: dict, output_dir: Path) -> dict:
    structure_rel = entry["reverse_artifacts"]["structure_json"]
    structure_file = ROOT_DIR / structure_rel if structure_rel else None
    structure_payload = load_structure_payload(structure_file) if structure_file else {}

    components = structure_payload.get("components") or []
    issues = structure_payload.get("issues") or []
    top_components = []
    for component in components[:8]:
        top_components.append(
            {
                "type": component.get("type"),
                "label": component.get("label"),
                "text_preview": component.get("text_preview"),
            }
        )

    compact_issues = []
    for issue in issues[:8]:
        compact_issues.append(
            {
                "severity": issue.get("severity"),
                "type": issue.get("type"),
                "message": issue.get("message"),
            }
        )

    return {
        "top_components": top_components,
        "issues": compact_issues,
    }


def build_module_handoff(module_name: str, entries: list[dict], output_dir: Path) -> dict:
    view_index = {}
    template_items = []

    for entry in entries:
        highlights = collect_template_highlights(entry, output_dir)
        template_items.append(
            {
                "template_name": entry["template_name"],
                "template_file": entry["template_file"],
                "routes": entry["routes"],
                "forward_batch": entry["forward_batch"],
                "batch_reason": entry["batch_reason"],
                "complexity_score": entry["complexity_score"],
                "structure_stats": entry["structure_stats"],
                "highlights": highlights,
            }
        )
        for view in entry["views"]:
            key = (view["view_file"], view["view_name"], view["line"])
            view_index[key] = {
                "view_name": view["view_name"],
                "view_module": view["view_module"],
                "view_file": view["view_file"],
                "line": view["line"],
                "decorators": view["decorators"],
                "context_keys": view["context_keys"],
                "context_expression": view["context_expression"],
                "signals": view["signals"],
                "source_excerpt": view["source_excerpt"],
            }

    return {
        "module_name": module_name,
        "template_total": len(template_items),
        "templates": sorted(template_items, key=lambda item: (item["forward_batch"], item["template_name"])),
        "views": sorted(view_index.values(), key=lambda item: (item["view_file"], item["line"])),
    }


def render_handoff_markdown(handoff: dict) -> str:
    lines = [
        f"# Claude Handoff: {handoff['module_name']}",
        "",
        "Tujuan:",
        "Revisi modul ini dari hasil reverse-engineering agar UI lebih rapi, konsisten, dan logika view/template lebih kuat tanpa memutus struktur Django yang ada.",
        "",
        "Aturan kerja untuk Claude:",
        "- Kerjakan hanya dalam lingkup modul ini.",
        "- Pertahankan pola Django template yang sudah ada kecuali ada alasan kuat untuk menyederhanakan.",
        "- Saat mengusulkan perubahan, sinkronkan HTML, view context, dan route dependency yang terkait.",
        "- Prioritaskan aksesibilitas, keterbacaan layout, konsistensi komponen, dan kebenaran context di view.",
        "- Jika sebuah template tampak statis tapi route atau context belum jelas, tandai sebagai asumsi, jangan mengarang API baru.",
        "",
        f"Jumlah template: {handoff['template_total']}",
        f"Jumlah view terkait: {len(handoff['views'])}",
        "",
        "## Template Scope",
        "",
    ]

    for template in handoff["templates"]:
        lines.append(f"### {template['template_name']}")
        lines.append(f"- File: `{template['template_file']}`")
        lines.append(f"- Batch: `{template['forward_batch']}`")
        lines.append(f"- Alasan batch: {template['batch_reason']}")
        lines.append(f"- Complexity: {template['complexity_score']}")
        stats = template.get("structure_stats") or {}
        if stats:
            lines.append(
                f"- Reverse stats: components={stats.get('component_total', 0)}, interactive={stats.get('interactive_total', 0)}, issues={stats.get('issue_total', 0)}, scroll_nesting={stats.get('scroll_nesting_total', 0)}"
            )
        if template["routes"]:
            route_text = ", ".join(
                f"`{route.get('route', '')}` ({route.get('url_name', '-')})" for route in template["routes"]
            )
            lines.append(f"- Routes: {route_text}")
        highlights = template.get("highlights") or {}
        if highlights.get("top_components"):
            lines.append("- Komponen utama:")
            for component in highlights["top_components"]:
                label = component.get("label") or component.get("type") or "component"
                preview = component.get("text_preview") or ""
                lines.append(f"  - {label}: {preview}")
        if highlights.get("issues"):
            lines.append("- Temuan reverse:")
            for issue in highlights["issues"]:
                lines.append(f"  - [{issue.get('severity', 'info')}] {issue.get('type')}: {issue.get('message')}")
        lines.append("")

    lines += [
        "## View Scope",
        "",
    ]

    for view in handoff["views"]:
        lines.append(f"### {view['view_name']}")
        lines.append(f"- File: `{view['view_file']}`:{view['line']}")
        if view["decorators"]:
            lines.append(f"- Decorators: {', '.join(f'`{item}`' for item in view['decorators'])}")
        if view["context_keys"]:
            lines.append(f"- Context keys eksplisit: {', '.join(f'`{item}`' for item in view['context_keys'])}")
        lines.append(
            f"- Signals: GET={view['signals']['uses_get']}, POST={view['signals']['uses_post']}, query_model={view['signals']['queries_models']}, json={view['signals']['uses_json']}, branching={view['signals']['has_branching']}"
        )
        lines.append("")
        lines.append("```python")
        lines.append(view["source_excerpt"])
        lines.append("```")
        lines.append("")

    lines += [
        "## Tugas Claude",
        "",
        "1. Review hubungan antar template dan view di modul ini.",
        "2. Usulkan struktur UI yang lebih konsisten berdasarkan komponen hasil reverse.",
        "3. Tandai context yang kurang, conditional yang membingungkan, atau logika view yang rawan salah render.",
        "4. Jika perlu, kembalikan hasil dalam bentuk patch plan per file: template dulu, lalu view yang harus menyesuaikan.",
        "",
    ]
    return "\n".join(lines)


def write_claude_handoffs(entries: list[dict], output_dir: Path) -> list[dict]:
    handoff_dir = output_dir / "claude_handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    grouped = defaultdict(list)
    for entry in entries:
        grouped[entry["module_area"]].append(entry)

    results = []
    for module_name, module_entries in sorted(grouped.items()):
        handoff = build_module_handoff(module_name, module_entries, output_dir)
        slug = slugify(module_name)
        json_path = handoff_dir / f"{slug}.json"
        md_path = handoff_dir / f"{slug}.md"
        json_path.write_text(json.dumps(handoff, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(render_handoff_markdown(handoff), encoding="utf-8")
        results.append(
            {
                "module_name": module_name,
                "json_file": str(json_path.relative_to(ROOT_DIR)).replace("\\", "/"),
                "markdown_file": str(md_path.relative_to(ROOT_DIR)).replace("\\", "/"),
                "template_total": handoff["template_total"],
                "view_total": len(handoff["views"]),
            }
        )
    return results


class Command(BaseCommand):
    help = "Build forward-generation batches from lumra_config views, URLs, templates, and reverse outputs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default=str(DEFAULT_OUTPUT_DIR),
            help="Directory for manifest output. Default: ./wireframe_output",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"]).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        view_map = collect_view_templates()
        route_map = collect_url_routes()

        template_files = [
            path
            for path in sorted((TEMPLATE_DIR / "lumra_pages").glob("**/*.html"))
            if not path.name.endswith(".bak")
        ]

        entries = [template_entry(path, view_map, route_map, output_dir) for path in template_files]
        entries.sort(key=lambda item: (item["forward_batch"], item["module_area"], item["template_name"]))

        batches = defaultdict(list)
        for entry in entries:
            batches[entry["forward_batch"]].append(
                {
                    "template_name": entry["template_name"],
                    "view_names": [item["view_name"] for item in entry["views"]],
                    "routes": [item["route"] for item in entry["routes"]],
                    "complexity_score": entry["complexity_score"],
                    "batch_reason": entry["batch_reason"],
                }
            )

        manifest = {
            "summary": {
                "template_total": len(entries),
                "mapped_template_total": sum(1 for entry in entries if entry["views"]),
                "unmapped_template_total": sum(1 for entry in entries if not entry["views"]),
                "batch_totals": {batch: len(items) for batch, items in sorted(batches.items())},
            },
            "entries": entries,
        }

        batch_plan = {
            "recommended_order": [
                {
                    "batch": batch,
                    "total_templates": len(items),
                    "templates": items,
                }
                for batch, items in sorted(batches.items())
            ]
        }

        handoff_files = write_claude_handoffs(entries, output_dir)

        manifest_path = output_dir / "forward_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        batches_path = output_dir / "forward_batches.json"
        batches_path.write_text(json.dumps(batch_plan, indent=2, ensure_ascii=False), encoding="utf-8")

        handoff_index_path = output_dir / "claude_handoff_index.json"
        handoff_index_path.write_text(json.dumps(handoff_files, indent=2, ensure_ascii=False), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS("Forward manifest generated."))
        self.stdout.write(f"- Manifest: {manifest_path}")
        self.stdout.write(f"- Batches : {batches_path}")
        self.stdout.write(f"- Claude handoff index: {handoff_index_path}")
        self.stdout.write(
            f"- Templates mapped: {manifest['summary']['mapped_template_total']}/{manifest['summary']['template_total']}"
        )
