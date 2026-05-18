import os
import re
import ast
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from collections import defaultdict

# ============================================
# KONFIGURASI
# ============================================
TARGET_DIR = r"D:\APPS\Project\lumra"
OUTPUT_FILE = "mapping_logic_lumra.md"

# Folder yang DIKECUALIKAN dari scan
EXCLUDE_DIRS = {
    '.venv', 'venv', 'env', 'virtualenv',
    'backup', '.backup',
    '__pycache__', '.git', 'node_modules',
    '.idea', '.vscode', 'migrations',
    'static', 'media', 'locale',
    '.lumra_fixer_backup', '.lumra_fix_all_backup', '.lumra_reorg_backup'
}

# ============================================
# DATA STRUCTURE
# ============================================
@dataclass
class ViewMapping:
    file_path: str
    view_name: str
    view_type: str
    line_number: int
    templates: List[str] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    forms: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    http_methods: List[str] = field(default_factory=list)
    is_api: bool = False
    redirects: List[str] = field(default_factory=list)
    url_patterns: List[str] = field(default_factory=list)
    raw_content: str = ""

# ============================================
# MAIN SCANNER CLASS
# ============================================
class DjangoLogicMapper:
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.results: List[ViewMapping] = []
        self.model_cache: Dict[str, str] = {}       # ModelName -> AppName
        self.form_model_cache: Dict[str, str] = {}   # FormName -> ModelName
        self.url_cache: Dict[str, str] = {}          # ViewName -> URL Pattern
        self.all_model_names: Set[str] = set()       # Lowercase lookup set
        self._parsed_model_files: Set[str] = set()   # Avoid duplicate parsing
        
    def _should_skip_dir(self, dir_path: Path) -> bool:
        """Cek apakah directory harus di-skip"""
        parts = dir_path.parts
        for part in parts:
            if part.lower() in EXCLUDE_DIRS:
                return True
        return False
    
    def _is_model_related_path(self, path: Path) -> bool:
        """Cek apakah path berhubungan dengan models (aggressive)"""
        # Cek nama file
        if 'model' in path.name.lower():
            return True
        # Cek semua folder parent
        for part in path.parts:
            if 'model' in part.lower():
                return True
        return False
    
    def scan_all(self) -> List[ViewMapping]:
        """Main entry point"""
        print("📦 Step 1: Membangun cache models (aggressive scan)...")
        self._build_model_cache()
        
        print("📦 Step 2: Membangun cache forms...")
        self._build_form_cache()
        
        print("📦 Step 3: Membaca URL patterns (flexible import)...")
        self._build_url_cache()
        
        print("📦 Step 4: Memindai views...")
        self._scan_all_views()
        
        print("📦 Step 5: Menghubungkan dengan URL...")
        self._enrich_with_urls()
        
        return self.results
    
    # ========================================
    # AGGRESSIVE MODEL CACHE
    # ========================================
    def _build_model_cache(self):
        """Scan AGRESIF: semua file .py di folder 'model' ATAU file bernama *_models.py"""
        
        model_base_classes = {
            'Model', 'AbstractUser', 'AbstractBaseUser',
            'PermissionsMixin', 'TimeStampedModel', 'SoftDeleteModel',
        }
        
        # Strategy 1: Semua .py di dalam folder yang namanya mengandung 'model'
        for py_file in self.target_dir.rglob("*.py"):
            if self._should_skip_dir(py_file):
                continue
            if self._is_model_related_path(py_file):
                self._parse_models_from_file(py_file, model_base_classes)
        
        # Strategy 2: File models.py eksplisit (backup jika belum ke-catch)
        for models_file in self.target_dir.rglob("models.py"):
            if self._should_skip_dir(models_file):
                continue
            file_key = str(models_file)
            if file_key not in self._parsed_model_files:
                self._parse_models_from_file(models_file, model_base_classes)
        
        # Strategy 3: Scan serializers.py untuk model references
        for ser_file in self.target_dir.rglob("serializers.py"):
            if self._should_skip_dir(ser_file):
                continue
            self._extract_models_from_serializers(ser_file)
        
        # Build lowercase lookup
        self.all_model_names = {m.lower() for m in self.model_cache}
        
        apps = len(set(self.model_cache.values()))
        print(f"  ✅ Ditemukan {len(self.model_cache)} models di {apps} apps")
    
    def _parse_models_from_file(self, file_path: Path, model_base_classes: Set[str]):
        """Parse satu file untuk cari class Model"""
        file_key = str(file_path)
        if file_key in self._parsed_model_files:
            return
        self._parsed_model_files.add(file_key)
        
        app_name = self._guess_app_name(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
        except Exception:
            return
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            
            # Cek 1: Base class adalah Model
            for base in node.bases:
                base_name = self._get_ast_name(base)
                if not isinstance(base_name, str):
                    continue
                if base_name in model_base_classes or base_name.endswith('Model'):
                    self.model_cache[node.name] = app_name
                    break
            
            # Cek 2: Punya Meta class dengan db_table (pasti model)
            if node.name not in self.model_cache:
                for item in node.body:
                    if isinstance(item, ast.ClassDef) and item.name == 'Meta':
                        for meta_item in item.body:
                            if isinstance(meta_item, ast.Assign):
                                for target in meta_item.targets:
                                    if isinstance(target, ast.Name) and target.id == 'db_table':
                                        self.model_cache[node.name] = app_name
                                        break
            
            # Cek 3: Punya objects = models.Manager() (pasti model)
            if node.name not in self.model_cache:
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == 'objects':
                                val_name = self._get_ast_name(item.value)
                                if isinstance(val_name, str) and 'Manager' in val_name:
                                    self.model_cache[node.name] = app_name
                                    break
    
    def _extract_models_from_serializers(self, file_path: Path):
        """Extract model references from serializer files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return
        
        # Pattern: model = ModelName di Meta class
        for match in re.finditer(r"class\s+Meta[^:]*:(?:(?!\nclass).)*model\s*=\s*(\w+)", content, re.DOTALL):
            model_name = match.group(1)
            if model_name.lower() not in {'none', 'self', 'str', 'int', 'bool'}:
                if model_name not in self.model_cache:
                    app_name = self._guess_app_name(file_path)
                    self.model_cache[model_name] = app_name
                    self.all_model_names.add(model_name.lower())
    
    def _guess_app_name(self, file_path: Path) -> str:
        """Tebak Django app name dari path file"""
        rel = file_path.relative_to(self.target_dir)
        parts = rel.parts
        
        if len(parts) < 2:
            return parts[0] if parts else "unknown"
        
        # Cari folder yang punya indikator Django app
        django_indicators = {'views', 'models', 'urls.py', 'admin.py', 'apps.py', 'serializers', 'forms', 'tests'}
        for i in range(1, len(parts)):
            parent = Path(self.target_dir) / Path("/".join(parts[:i]))
            for ind in django_indicators:
                if (parent / ind).exists():
                    return parts[i - 1] if i > 0 else parts[0]
        
        # Fallback: folder pertama setelah root (biasanya nama app)
        return parts[0]
    
    # ========================================
    # FORM CACHE
    # ========================================
    def _build_form_cache(self):
        for forms_file in self.target_dir.rglob("*.py"):
            if self._should_skip_dir(forms_file):
                continue
            
            is_form_related = (
                forms_file.name == 'forms.py' or
                'form' in forms_file.name.lower() or
                'form' in str(forms_file.parent).lower()
            )
            
            if not is_form_related:
                continue
            
            try:
                with open(forms_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and 'Form' in node.name:
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name) and target.id == 'model':
                                        val = self._get_ast_name(item.value)
                                        if isinstance(val, str) and val:
                                            self.form_model_cache[node.name] = val
            except Exception:
                pass
        
        print(f"  ✅ Ditemukan {len(self.form_model_cache)} form-model mappings")
    
    # ========================================
    # FLEXIBLE URL CACHE
    # ========================================
    def _build_url_cache(self):
        """Build URL cache yang handle import views terpecah"""
        for url_file in self.target_dir.rglob("urls.py"):
            if self._should_skip_dir(url_file):
                continue
            
            try:
                with open(url_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Build import mapping dulu
                import_map = self._parse_url_imports(content)
                
                # Pattern 1: path('url/', view_ref)
                for match in re.finditer(
                    r"(?:path|re_path|url)\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*([\w.]+)",
                    content
                ):
                    url_path = match.group(1)
                    view_ref = match.group(2)
                    resolved = self._resolve_url_view(view_ref, import_map)
                    if resolved and resolved not in self.url_cache:
                        self.url_cache[resolved] = url_path
                
                # Pattern 2: path('url/', SomeView.as_view())
                for match in re.finditer(
                    r"(?:path|re_path|url)\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*([\w.]+)\.as_view",
                    content
                ):
                    url_path = match.group(1)
                    view_ref = match.group(2)
                    resolved = self._resolve_url_view(view_ref, import_map)
                    if resolved and resolved not in self.url_cache:
                        self.url_cache[resolved] = url_path
                
                # Pattern 3: urlpatterns = [path(...), ...] yang displit ke variable
                # Handle include() untuk nested urls
                for match in re.finditer(
                    r"(?:path|re_path|url)\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*include\s*\(\s*['\"]([^'\"]+)['\"]",
                    content
                ):
                    pass  # Nested URLs ditangani saat scan file tersebut
                    
            except Exception:
                pass
        
        print(f"  ✅ Ditemukan {len(self.url_cache)} URL patterns")
    
    def _parse_url_imports(self, content: str) -> Dict[str, str]:
        """Parse semua import di urls.py untuk mapping view references"""
        import_map = {}
        
        # Pattern A: from .views.auth_views import login_view, logout_view
        for match in re.finditer(
            r"from\s+([\w.]+)\s+import\s+\(([^)]+)\)",
            content, re.DOTALL
        ):
            module = match.group(1)
            for name in re.findall(r"(\w+)", match.group(2)):
                if name not in ('from', 'import'):
                    import_map[name] = f"{module}.{name}"
        
        # Pattern B: from .views.auth_views import login_view
        for match in re.finditer(
            r"from\s+([\w.]+)\s+import\s+([\w,\s]+?)(?:\s*#|\s*$|\s*\n)",
            content
        ):
            module = match.group(1)
            for name in re.findall(r"(\w+)", match.group(2)):
                if name not in ('from', 'import'):
                    import_map[name] = f"{module}.{name}"
        
        # Pattern C: import auth_views
        for match in re.finditer(r"^import\s+([\w.]+)\s*$", content, re.MULTILINE):
            module = match.group(1)
            parts = module.split('.')
            if len(parts) >= 2:
                # auth_views -> bisa dipanggil sebagai auth_views.login_view
                import_map[parts[-1]] = module
        
        return import_map
    
    def _resolve_url_view(self, view_ref: str, import_map: Dict[str, str]) -> Optional[str]:
        """Resolve view reference ke nama fungsi view sebenarnya"""
        parts = view_ref.split('.')
        
        # Case 1: Simple name "login_view"
        if len(parts) == 1:
            name = parts[0]
            if name in import_map:
                full = import_map[name]
                return full.split('.')[-1]  # Ambil nama fungsi terakhir
            return name
        
        # Case 2: "views.login_view" atau "auth_views.login_view"
        # Nama view sebenarnya adalah bagian terakhir
        last = parts[-1]
        
        # Case 3: "views.auth_views.login_view" (3 levels)
        # View name tetap bagian terakhir
        return last
    
    # ========================================
    # VIEW SCANNING
    # ========================================
    def _scan_all_views(self):
        view_filenames = {'views.py', 'api.py', 'handlers.py', 'viewsets.py'}
        error_count = 0
        
        for py_file in self.target_dir.rglob("*.py"):
            if self._should_skip_dir(py_file):
                continue
            
            filename_lower = py_file.name.lower()
            is_view_file = (
                py_file.name in view_filenames or
                'view' in filename_lower or
                'api' in filename_lower
            )
            
            if is_view_file:
                try:
                    self._parse_view_file(py_file)
                except Exception as e:
                    error_count += 1
                    rel_path = py_file.relative_to(self.target_dir)
                    print(f"  ⚠️ Error parsing {rel_path}: {e}")
        
        if error_count:
            print(f"  ⚠️ {error_count} file gagal di-parse")
    
    def _parse_view_file(self, file_path: Path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        file_rel = str(file_path.relative_to(self.target_dir)).replace("\\", "/")
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                self._parse_fbv(node, file_rel, content)
            elif isinstance(node, ast.ClassDef):
                self._parse_cbv(node, file_rel, content)
    
    def _parse_fbv(self, node: ast.FunctionDef, file_path: str, full_content: str):
        params = [arg.arg for arg in node.args.args]
        if 'request' not in params:
            return
        
        lines = full_content.split('\n')
        func_content = '\n'.join(lines[node.lineno - 1:node.end_lineno])
        
        templates = self._extract_templates_from_content(func_content)
        models = self._extract_models_aggressive(func_content, node)
        forms = self._extract_forms_from_content(func_content)
        redirects = self._extract_redirects_from_content(func_content)
        http_methods = self._detect_http_methods_fbv(node, func_content)
        is_api = self._detect_api_fbv(node, func_content)
        decorators = self._extract_decorators_fbv(node)
        
        self.results.append(ViewMapping(
            file_path=file_path,
            view_name=node.name,
            view_type="FBV",
            line_number=node.lineno,
            templates=templates,
            models=models,
            forms=forms,
            decorators=decorators,
            http_methods=http_methods,
            is_api=is_api,
            redirects=redirects,
            raw_content=func_content
        ))
    
    def _parse_cbv(self, node: ast.ClassDef, file_path: str, full_content: str):
        base_classes = []
        for b in node.bases:
            name = self._get_ast_name(b)
            if name:
                base_classes.append(name)
        
        cbv_indicators = {
            'View', 'TemplateView', 'ListView', 'DetailView',
            'CreateView', 'UpdateView', 'DeleteView', 'FormView',
            'APIView', 'ViewSet', 'ModelViewSet', 'GenericViewSet',
            'ListAPIView', 'RetrieveAPIView', 'CreateAPIView',
            'UpdateAPIView', 'DestroyAPIView', 'ListCreateAPIView',
            'RetrieveUpdateAPIView', 'RetrieveDestroyAPIView',
            'RetrieveUpdateDestroyAPIView', 'ReadOnlyModelViewSet'
        }
        
        is_cbv = any(
            any(ind in base for ind in cbv_indicators)
            for base in base_classes
            if isinstance(base, str)
        )
        
        if not is_cbv:
            return
        
        lines = full_content.split('\n')
        class_content = '\n'.join(lines[node.lineno - 1:node.end_lineno])
        
        templates = self._extract_templates_cbv(node, class_content)
        models = self._extract_models_cbv(node, class_content, base_classes)
        forms = self._extract_forms_cbv(node, class_content)
        redirects = self._extract_redirects_from_content(class_content)
        http_methods = self._detect_http_methods_cbv(node, base_classes)
        is_api = self._detect_api_cbv(base_classes)
        decorators = self._extract_decorators_cbv(node)
        
        self.results.append(ViewMapping(
            file_path=file_path,
            view_name=node.name,
            view_type="CBV",
            line_number=node.lineno,
            templates=templates,
            models=models,
            forms=forms,
            decorators=decorators,
            http_methods=http_methods,
            is_api=is_api,
            redirects=redirects,
            raw_content=class_content
        ))
    
    # ========================================
    # AGGRESSIVE MODEL EXTRACTION (TANPA .objects)
    # ========================================
    def _extract_models_aggressive(self, content: str, func_node: ast.FunctionDef = None) -> List[str]:
        """Deteksi model TANPA mengandalkan .objects saja"""
        models = set()
        
        # ── Pattern 1: Standard .objects.xxx ──
        qs_methods = r"(all|filter|get|create|update|exclude|count|first|last|earliest|latest|aggregate|annotate|bulk_create|bulk_update|delete|exists|order_by|select_related|prefetch_related|values|values_list|distinct|reverse|only|defer|iterator)"
        for m in re.findall(rf"(\w+)\.objects\.{qs_methods}", content):
            models.add(m)
        
        # ── Pattern 2: Custom Manager: Model.custom_manager.filter() ──
        skip_targets = {'user', 'request', 'session', 'response', 'self', 'cls', 'form', 'serializer'}
        for model_name, mgr in re.findall(r"(\w+)\.(\w+)\.(?:filter|get|all|create|update|exclude|annotate|aggregate|select_related|prefetch_related|order_by)", content):
            if model_name.lower() not in skip_targets:
                models.add(model_name)
        
        # ── Pattern 3: get_object_or_404 / get_list_or_404 ──
        for func in ['get_object_or_404', 'get_list_or_404']:
            for m in re.findall(rf"{func}\s*\(\s*(\w+)", content):
                models.add(m)
        
        # ── Pattern 4: Model.DoesNotExist / MultipleObjectsReturned ──
        for m in re.findall(r"(\w+)\.(?:DoesNotExist|MultipleObjectsReturned)", content):
            models.add(m)
        
        # ── Pattern 5: Type annotations (def view(request, obj: ModelName)) ──
        if func_node:
            for arg in func_node.args.args:
                if arg.annotation:
                    ann = self._get_ast_name(arg.annotation)
                    if isinstance(ann, str) and ann.lower() in self.all_model_names:
                        self._add_model_by_name(models, ann)
            
            # Return type: def view(...) -> QuerySet[ModelName]
            if func_node.returns:
                ret = self._get_ast_name(func_node.returns)
                if isinstance(ret, str) and ret:
                    for model_name in self.model_cache:
                        if model_name.lower() in ret.lower():
                            models.add(model_name)
        
        # ── Pattern 6: model = ModelName (serializers, forms, dll) ──
        for m in re.findall(r"\bmodel\s*=\s*(\w+)", content):
            if m.lower() not in {'none', 'self', 'true', 'false', 'str', 'int', 'bool'}:
                self._add_model_by_name(models, m)
        
        # ── Pattern 7: Model._default_manager / _base_manager ──
        for m in re.findall(r"(\w+)\._(?:default|base)_manager", content):
            models.add(m)
        
        # ── Pattern 8: Class Meta: model = ModelName ──
        for m in re.findall(r"class\s+Meta[^:]*:(?:(?!\nclass).)*?model\s*=\s*(\w+)", content, re.DOTALL):
            self._add_model_by_name(models, m)
        
        # ── Pattern 9: Direct instantiation Model(field=val) ──
        # Hanya tangkap jika nama sudah ada di model cache
        known_non_model = {'render', 'redirect', 'HttpResponse', 'JsonResponse', 'Response', 
                          'reverse', 'get_object_or_404', 'get_list_or_404', 'QuerySet',
                          'timezone', 'datetime', 'date', 'time', 'timedelta',
                          'serializers', 'json', 'dict', 'list', 'set', 'tuple',
                          'Decimal', 'FloatField', 'CharField', 'IntegerField'}
        for m in re.findall(r"\b(\w+)\s*\([^)]*\w+\s*=", content):
            if m not in known_non_model and m[0].isupper():
                self._add_model_by_name(models, m)
        
        # ── Pattern 10: Prefetch / Select related dengan string reference ──
        for m in re.findall(r"(?:prefetch_related|select_related)\s*\(\s*['\"](\w+)", content):
            self._add_model_by_name(models, m)
        
        # ── Pattern 11: Dari forms yang punya model ──
        for form_name in self._extract_forms_from_content(content):
            if form_name in self.form_model_cache:
                models.add(self.form_model_cache[form_name])
        
        # ── Pattern 12: queryset assignment ──
        for m in re.findall(r"\bqueryset\s*=\s*(\w+)\.", content):
            self._add_model_by_name(models, m)
        
        return self._enrich_model_names(models)
    
    def _add_model_by_name(self, models: Set[str], name: str):
        """Tambahkan model name ke set jika terdaftar di cache (case-insensitive)"""
        if not name or not isinstance(name, str):
            return
        if name in self.model_cache:
            models.add(name)
        elif name.lower() in self.all_model_names:
            for cached, app in self.model_cache.items():
                if cached.lower() == name.lower():
                    models.add(cached)
                    break
    
    def _extract_models_cbv(self, node: ast.ClassDef, content: str, base_classes: List[str]) -> List[str]:
        models = set()
        
        # 1. model = ModelName
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == 'model':
                        val = self._get_ast_name(item.value)
                        if isinstance(val, str) and val:
                            models.add(val)
        
        # 2. queryset = Model.objects...
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == 'queryset':
                        if isinstance(item.value, ast.Attribute) and isinstance(item.value.value, ast.Name):
                            models.add(item.value.value.id)
        
        # 3. get_queryset() method
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'get_queryset':
                func_src = self._get_func_source(item, content)
                for m in re.findall(r"(\w+)\.objects\.", func_src):
                    models.add(m)
                # Juga aggressive
                for m in self._extract_models_aggressive(func_src, item):
                    models.add(m.split('.')[-1])
        
        # 4. form_class -> model
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == 'form_class':
                        val = self._get_ast_name(item.value)
                        if isinstance(val, str) and val in self.form_model_cache:
                            models.add(self.form_model_cache[val])
        
        # 5. Infer dari nama class (UserListView -> User)
        if not models:
            for model_name in self.model_cache:
                if model_name.lower() in node.name.lower():
                    models.add(model_name)
                    break
        
        # 6. Fallback aggressive
        if not models:
            for m in self._extract_models_aggressive(content):
                models.add(m.split('.')[-1])
        
        return self._enrich_model_names(models)
    
    def _enrich_model_names(self, models: Set[str]) -> List[str]:
        enriched = []
        for model in sorted(models):
            if model in self.model_cache:
                enriched.append(f"{self.model_cache[model]}.{model}")
            elif model.lower() in self.all_model_names:
                for cached, app in self.model_cache.items():
                    if cached.lower() == model.lower():
                        enriched.append(f"{app}.{cached}")
                        break
            else:
                enriched.append(model)
        return enriched
    
    # ========================================
    # TEMPLATE EXTRACTION
    # ========================================
    def _extract_templates_from_content(self, content: str) -> List[str]:
        templates = set()
        for pattern in [
            r"render\s*\([^,]+,\s*['\"]([^'\"]+)['\"]",
            r"TemplateResponse\s*\([^,]+,\s*['\"]([^'\"]+)['\"]",
            r"template_name\s*=\s*['\"]([^'\"]+)['\"]",
            r"['\"]template_name['\"]\s*:\s*['\"]([^'\"]+)['\"]",
            r"render_to_string\s*\(\s*['\"]([^'\"]+)['\"]",
        ]:
            templates.update(re.findall(pattern, content, re.IGNORECASE))
        return list(templates)
    
    def _extract_templates_cbv(self, node: ast.ClassDef, content: str) -> List[str]:
        templates = set()
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == 'template_name':
                        if isinstance(item.value, ast.Constant) and isinstance(item.value.value, str):
                            templates.add(item.value.value)
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'get_template_names':
                templates.update(re.findall(r"['\"]([^'\"]+)['\"]", self._get_func_source(item, content)))
        templates.update(self._extract_templates_from_content(content))
        return list(templates)
    
    # ========================================
    # FORM EXTRACTION
    # ========================================
    def _extract_forms_from_content(self, content: str) -> List[str]:
        forms = set()
        for pattern in [
            r"(\w+Form)\s*\(",
            r"(\w+ModelForm)\s*\(",
            r"form_class\s*=\s*(\w+Form)",
            r"form_class\s*=\s*(\w+ModelForm)",
        ]:
            forms.update(re.findall(pattern, content))
        return list(forms)
    
    def _extract_forms_cbv(self, node: ast.ClassDef, content: str) -> List[str]:
        forms = set()
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == 'form_class':
                        val = self._get_ast_name(item.value)
                        if isinstance(val, str) and val:
                            forms.add(val)
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'get_form_class':
                forms.update(re.findall(r"(\w+Form)", self._get_func_source(item, content)))
        return list(forms)
    
    # ========================================
    # REDIRECT EXTRACTION
    # ========================================
    def _extract_redirects_from_content(self, content: str) -> List[str]:
        redirects = set()
        for pattern in [
            r"redirect\s*\(\s*['\"]([^'\"]+)['\"]",
            r"HttpResponseRedirect\s*\(\s*['\"]([^'\"]+)['\"]",
            r"HttpResponsePermanentRedirect\s*\(\s*['\"]([^'\"]+)['\"]",
            r"reverse\s*\(\s*['\"]([^'\"]+)['\"]",
            r"resolve_url\s*\(\s*['\"]([^'\"]+)['\"]",
        ]:
            redirects.update(re.findall(pattern, content))
        return list(redirects)
    
    # ========================================
    # HTTP METHODS
    # ========================================
    def _detect_http_methods_fbv(self, node: ast.FunctionDef, content: str) -> List[str]:
        methods = set()
        for dec in node.decorator_list:
            dec_name = self._get_ast_name(dec)
            if not isinstance(dec_name, str):
                continue
            if 'require_http_methods' in dec_name:
                dec_src = ast.unparse(dec) if hasattr(ast, 'unparse') else ""
                methods.update(re.findall(r"['\"](\w+)['\"]", dec_src))
                return list(methods) if methods else ['GET']
            if 'require_GET' in dec_name:
                return ['GET']
            if 'require_POST' in dec_name:
                return ['POST']
        
        methods.update(re.findall(r"request\.method\s*==\s*['\"](\w+)['\"]", content))
        for check in re.findall(r"request\.method\s+in\s+\[([^\]]+)\]", content):
            methods.update(re.findall(r"['\"](\w+)['\"]", check))
        
        if 'request.POST' in content or 'request.FILES' in content:
            methods.add('POST')
        if 'request.body' in content:
            methods.add('POST')
        
        return list(methods) if methods else ['GET']
    
    def _detect_http_methods_cbv(self, node: ast.ClassDef, base_classes: List[str]) -> List[str]:
        methods = set()
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name in {'get', 'post', 'put', 'patch', 'delete', 'head', 'options'}:
                methods.add(item.name.upper())
        if methods:
            return list(methods)
        
        mapping = {
            'ListView': ['GET'], 'ListAPIView': ['GET'],
            'DetailView': ['GET'], 'RetrieveAPIView': ['GET'],
            'CreateView': ['GET', 'POST'], 'CreateAPIView': ['POST'],
            'ListCreateAPIView': ['GET', 'POST'],
            'UpdateView': ['GET', 'POST'], 'UpdateAPIView': ['PUT', 'PATCH'],
            'RetrieveUpdateAPIView': ['GET', 'PUT', 'PATCH'],
            'DeleteView': ['GET', 'POST'], 'DestroyAPIView': ['DELETE'],
            'RetrieveDestroyAPIView': ['GET', 'DELETE'],
            'RetrieveUpdateDestroyAPIView': ['GET', 'PUT', 'PATCH', 'DELETE'],
            'ViewSet': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'ModelViewSet': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'ReadOnlyModelViewSet': ['GET'],
        }
        for base in base_classes:
            if isinstance(base, str):
                for pattern, base_methods in mapping.items():
                    if pattern in base:
                        methods.update(base_methods)
        return list(methods) if methods else ['GET']
    
    # ========================================
    # API DETECTION
    # ========================================
    def _detect_api_fbv(self, node: ast.FunctionDef, content: str) -> bool:
        for dec in node.decorator_list:
            dec_name = self._get_ast_name(dec)
            if isinstance(dec_name, str) and 'api_view' in dec_name.lower():
                return True
        return any(ind in content for ind in ['JsonResponse', 'Response(', 'JSONRenderer', 'status.HTTP_'])
    
    def _detect_api_cbv(self, base_classes: List[str]) -> bool:
        api_kw = {'APIView', 'ViewSet', 'ModelViewSet', 'GenericViewSet',
                  'ListAPIView', 'RetrieveAPIView', 'CreateAPIView', 'UpdateAPIView',
                  'DestroyAPIView', 'ListCreateAPIView', 'RetrieveUpdateAPIView',
                  'RetrieveDestroyAPIView', 'RetrieveUpdateDestroyAPIView', 'ReadOnlyModelViewSet'}
        for base in base_classes:
            if isinstance(base, str) and any(k in base for k in api_kw):
                return True
        return False
    
    # ========================================
    # DECORATORS
    # ========================================
    def _extract_decorators_fbv(self, node: ast.FunctionDef) -> List[str]:
        decorators = []
        prefixes = ['django.contrib.auth.decorators.', 'django.views.decorators.',
                     'django.views.decorators.http.', 'django.views.decorators.csrf.',
                     'django.views.decorators.cache.']
        for dec in node.decorator_list:
            name = self._get_ast_name(dec)
            if isinstance(name, str) and name:
                for p in prefixes:
                    name = name.replace(p, '')
                decorators.append(name)
        return decorators
    
    def _extract_decorators_cbv(self, node: ast.ClassDef) -> List[str]:
        decorators = []
        for dec in node.decorator_list:
            name = self._get_ast_name(dec)
            if isinstance(name, str) and name:
                decorators.append(name)
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                for dec in item.decorator_list:
                    name = self._get_ast_name(dec)
                    if isinstance(name, str) and 'method_decorator' in name:
                        m = re.search(r"method_decorator\s*\(\s*(\w+)", name)
                        if m:
                            decorators.append(f"@{m.group(1)}")
        return list(set(decorators))
    
    # ========================================
    # URL ENRICHMENT
    # ========================================
    def _enrich_with_urls(self):
        for mapping in self.results:
            if mapping.view_name in self.url_cache:
                mapping.url_patterns.append(self.url_cache[mapping.view_name])
            for cached_view, url in self.url_cache.items():
                if mapping.view_name in cached_view and cached_view != mapping.view_name:
                    mapping.url_patterns.append(url)
    
    # ========================================
    # SAFE AST HELPER (NO TUPLE ERROR)
    # ========================================
    def _get_ast_name(self, node) -> str:
        """SELALU return string. Tidak pernah tuple."""
        if node is None:
            return ""
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                parent = self._get_ast_name(node.value)
                return f"{parent}.{node.attr}" if parent else node.attr
            elif isinstance(node, ast.Call):
                return self._get_ast_name(node.func)
            elif isinstance(node, ast.Constant):
                return str(node.value) if node.value else ""
            elif isinstance(node, ast.Subscript):
                return self._get_ast_name(node.value)
            elif isinstance(node, ast.Tuple):
                # AMBIL ELEMEN PERTAMA SAJA - tidak pernah return tuple
                return self._get_ast_name(node.elts[0]) if node.elts else ""
            elif isinstance(node, ast.List):
                return self._get_ast_name(node.elts[0]) if node.elts else ""
            elif isinstance(node, ast.BinOp):
                return self._get_ast_name(node.left) + self._get_ast_name(node.right)
            elif isinstance(node, ast.IfExp):
                return self._get_ast_name(node.body)
            elif isinstance(node, ast.Starred):
                return self._get_ast_name(node.value)
            elif isinstance(node, ast.JoinedStr):  # f-string
                return "f-string"
            elif hasattr(ast, 'unparse'):
                try:
                    result = ast.unparse(node)
                    return result if isinstance(result, str) else str(result)
                except Exception:
                    pass
        except Exception:
            pass
        return ""
    
    def _get_func_source(self, node: ast.FunctionDef, full_content: str) -> str:
        lines = full_content.split('\n')
        start = node.lineno - 1
        end = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
        return '\n'.join(lines[start:end])


# ============================================
# MARKDOWN GENERATOR (DENGAN PATH FILE)
# ============================================
def save_to_md(data: List[ViewMapping], output_file: str, fmc: Dict[str, str]):
    with open(output_file, "w", encoding="utf-8") as f:
        # HEADER
        f.write("# 📊 Mapping Logic Lumra\n\n")
        f.write("> Dokumen otomatis: koneksi **Views** ↔ **Templates** ↔ **Database**\n\n")
        
        # STATS
        fbv = sum(1 for d in data if d.view_type == "FBV")
        cbv = sum(1 for d in data if d.view_type == "CBV")
        api = sum(1 for d in data if d.is_api)
        
        all_models, all_templates, all_forms = set(), set(), set()
        for d in data:
            all_models.update(d.models)
            all_templates.update(d.templates)
            all_forms.update(d.forms)
        
        f.write("## 📈 Statistik\n\n")
        f.write("| Metrik | Jumlah |\n|:---|:---|\n")
        f.write(f"| **Total Views** | {len(data)} |\n")
        f.write(f"| FBV / CBV | {fbv} / {cbv} |\n")
        f.write(f"| Web / API | {len(data) - api} / {api} |\n")
        f.write(f"| **Models** | {len(all_models)} |\n")
        f.write(f"| **Templates** | {len(all_templates)} |\n")
        f.write(f"| **Forms** | {len(all_forms)} |\n\n")
        
        # ── MAIN TABLE DENGAN PATH FILE ──
        f.write("## 📋 Tabel Mapping Utama\n\n")
        f.write("| # | Path File | View | Type | URL | Template | Model/DB | Form | Methods | API? |\n")
        f.write("|:--:|:----------|:-----|:----:|:----|:---------|:---------|:-----|:-------|:----:|\n")
        
        for idx, item in enumerate(data, 1):
            url = ", ".join(f"`{u}`" for u in item.url_patterns) if item.url_patterns else "-"
            tpl = ", ".join(f"`{t}`" for t in item.templates) if item.templates else "-"
            mdl = ", ".join(f"**{m}**" for m in item.models) if item.models else "-"
            frm = ", ".join(item.forms) if item.forms else "-"
            met = " ".join(f"`{m}`" for m in item.http_methods)
            badge = "🌐" if item.is_api else ""
            f.write(f"| {idx} | `{item.file_path}` | `{item.view_name}` | {item.view_type} | {url} | {tpl} | {mdl} | {frm} | {met} | {badge} |\n")
        
        # ── DETAIL PER FILE ──
        f.write("\n---\n\n## 📁 Detail Per File\n\n")
        by_file = defaultdict(list)
        for item in data:
            by_file[item.file_path].append(item)
        
        for fpath, items in sorted(by_file.items()):
            f.write(f"### 📄 `{fpath}`\n\n")
            for item in items:
                badge = "🌐 API" if item.is_api else "🕸️ Web"
                f.write(f"#### `{item.view_name}` — L{item.line_number} — {badge}\n\n")
                f.write("| Property | Value |\n|:---------|:------|\n")
                f.write(f"| **Type** | {item.view_type} |\n")
                if item.url_patterns:
                    f.write(f"| **URL** | {', '.join(f'`{u}`' for u in item.url_patterns)} |\n")
                if item.http_methods:
                    f.write(f"| **Methods** | {', '.join(f'`{m}`' for m in item.http_methods)} |\n")
                if item.decorators:
                    f.write(f"| **Decorators** | {', '.join(f'`{d}`' for d in item.decorators)} |\n")
                if item.templates:
                    f.write(f"| **Templates** | {', '.join(f'`{t}`' for t in item.templates)} |\n")
                if item.models:
                    f.write(f"| **Models** | {', '.join(f'**{m}**' for m in item.models)} |\n")
                if item.forms:
                    f.write(f"| **Forms** | {', '.join(f'`{fo}`' for fo in item.forms)} |\n")
                if item.redirects:
                    f.write(f"| **Redirects** | {', '.join(f'`{r}`' for r in item.redirects)} |\n")
                f.write("\n")
        
        # ── MODEL SUMMARY ──
        if all_models:
            f.write("---\n\n## 🗄️ Penggunaan Models\n\n")
            mv = defaultdict(list)
            for item in data:
                for m in item.models:
                    mv[m].append(f"`{item.view_name}`")
            f.write("| Model | Views |\n|:------|:------|\n")
            for m, views in sorted(mv.items()):
                f.write(f"| **{m}** | {', '.join(views)} |\n")
            f.write("\n")
        
        # ── TEMPLATE SUMMARY ──
        if all_templates:
            f.write("---\n\n## 📝 Penggunaan Templates\n\n")
            tv = defaultdict(list)
            for item in data:
                for t in item.templates:
                    tv[t].append(f"`{item.view_name}`")
            f.write("| Template | Views |\n|:---------|:------|\n")
            for t, views in sorted(tv.items()):
                f.write(f"| `{t}` | {', '.join(views)} |\n")
            f.write("\n")
        
        # ── FORM SUMMARY ──
        if all_forms:
            f.write("---\n\n## 📝 Penggunaan Forms\n\n")
            fv = defaultdict(list)
            for item in data:
                for fo in item.forms:
                    fv[fo].append(f"`{item.view_name}`")
            f.write("| Form | Views | Model |\n|:-----|:------|:------|\n")
            for fo, views in sorted(fv.items()):
                mdl = f"**{fmc[fo]}**" if fo in fmc else "-"
                f.write(f"| `{fo}` | {', '.join(views)} | {mdl} |\n")
            f.write("\n")
        
        # ── API ENDPOINTS ──
        api_items = [d for d in data if d.is_api]
        if api_items:
            f.write("---\n\n## 🌐 API Endpoints\n\n")
            f.write("| # | Endpoint | Path File | View | Methods | Models |\n")
            f.write("|:--:|:---------|:----------|:-----|:--------|:-------|\n")
            for idx, item in enumerate(api_items, 1):
                url = item.url_patterns[0] if item.url_patterns else "?"
                mdl = ", ".join(item.models) if item.models else "-"
                met = ", ".join(f"`{m}`" for m in item.http_methods)
                f.write(f"| {idx} | `{url}` | `{item.file_path}` | `{item.view_name}` | {met} | {mdl} |\n")
            f.write("\n")
        
        # ── ORPHAN CHECK ──
        f.write("---\n\n## ⚠️ Potensi Masalah\n\n")
        no_url = [d for d in data if not d.url_patterns]
        if no_url:
            f.write("### Views Tanpa URL Pattern\n\n")
            for item in no_url:
                f.write(f"- `{item.view_name}` — `{item.file_path}`\n")
            f.write("\n")
        else:
            f.write("### Views Tanpa URL Pattern\n\n✅ Semua views punya URL!\n\n")
        
        no_tpl = [d for d in data if not d.templates and not d.is_api and not d.redirects]
        if no_tpl:
            f.write("### Web Views Tanpa Template\n\n")
            for item in no_tpl:
                f.write(f"- `{item.view_name}` — `{item.file_path}`\n")
            f.write("\n")


# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 DJANGO LOGIC MAPPER v2")
    print("   Aggressive Model Scan | Flexible URL | Split Views")
    print("=" * 60)
    print()
    
    if not os.path.exists(TARGET_DIR):
        print(f"❌ Directory tidak ditemukan: {TARGET_DIR}")
        exit(1)
    
    mapper = DjangoLogicMapper(TARGET_DIR)
    results = mapper.scan_all()
    
    print("\n" + "=" * 60)
    save_to_md(results, OUTPUT_FILE, mapper.form_model_cache)
    
    fbv = sum(1 for d in results if d.view_type == "FBV")
    cbv = sum(1 for d in results if d.view_type == "CBV")
    api = sum(1 for d in results if d.is_api)
    
    print(f"✅ Selesai! → {OUTPUT_FILE}")
    print(f"📊 {len(results)} views ({fbv} FBV, {cbv} CBV, {api} API)")
    print("=" * 60)