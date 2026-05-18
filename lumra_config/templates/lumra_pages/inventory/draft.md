<!-- ════════════════════════════════════════════════════════
     FILE 1 OF 3 — recipe_list.html
════════════════════════════════════════════════════════ -->
{% extends "base/base_hybrid.html" %}
{% load i18n %}{% load static %}
{% block title %}Daftar Recipe — Lumra{% endblock %}

{% block extra_css %}
<style>
:root{--card-radius:12px;--card-shadow:0 1px 3px rgba(0,0,0,.06),0 4px 16px rgba(0,0,0,.04);--card-border:rgba(0,0,0,.06);}
.pp-page{padding:1.25rem;display:flex;flex-direction:column;gap:1rem;}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:.875rem;}
.kpi-card{background:oklch(var(--b1));border:.5px solid var(--card-border);border-radius:var(--card-radius);box-shadow:var(--card-shadow);padding:1rem 1.25rem;display:flex;flex-direction:column;gap:.4rem;transition:box-shadow 180ms,transform 180ms;}
.kpi-card:hover{box-shadow:0 4px 20px rgba(0,0,0,.08);transform:translateY(-1px);}
.kpi-icon{width:36px;height:36px;border-radius:9px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.kpi-value{font-size:1.5rem;font-weight:800;letter-spacing:-.02em;line-height:1;color:oklch(var(--bc));}
.kpi-label{font-size:.7rem;font-weight:600;color:oklch(var(--bc)/.5);text-transform:uppercase;letter-spacing:.06em;}
.section-card{background:oklch(var(--b1));border:.5px solid var(--card-border);border-radius:var(--card-radius);box-shadow:var(--card-shadow);overflow:hidden;}
.section-card-header{padding:1rem 1.25rem;border-bottom:.5px solid oklch(var(--bc)/.06);display:flex;align-items:center;justify-content:space-between;gap:.5rem;flex-wrap:wrap;}
.section-card-title{font-size:.85rem;font-weight:700;color:oklch(var(--bc));text-transform:uppercase;letter-spacing:.07em;}
.pp-toolbar{background:oklch(var(--b1));border:.5px solid var(--card-border);border-radius:var(--card-radius);box-shadow:var(--card-shadow);padding:.875rem 1.25rem;display:flex;align-items:center;justify-content:space-between;gap:.75rem;flex-wrap:wrap;}
.dash-table{width:100%;border-collapse:collapse;font-size:.82rem;}
.dash-table th{padding:.625rem 1rem;text-align:left;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:oklch(var(--bc)/.4);border-bottom:.5px solid oklch(var(--bc)/.07);cursor:pointer;user-select:none;}
.dash-table th:hover{background:oklch(var(--b2));}
.dash-table td{padding:.75rem 1rem;border-bottom:.5px solid oklch(var(--bc)/.05);color:oklch(var(--bc)/.8);vertical-align:middle;}
.dash-table tr:last-child td{border-bottom:none;}.dash-table tr:hover td{background:oklch(var(--b2));}
.dash-table th.r,.dash-table td.r{text-align:right;}
.sort-icon{display:inline-flex;align-items:center;margin-left:.25rem;opacity:.4;font-size:.7rem;}
.sort-icon.active{opacity:1;color:var(--jade,#00a86b);}
.form-input{background:oklch(var(--b2));border:.5px solid oklch(var(--bc)/.12);border-radius:8px;padding:.6rem .875rem;font-size:.85rem;color:oklch(var(--bc));width:100%;outline:none;transition:border-color 150ms,box-shadow 150ms;}
.form-input:focus{border-color:var(--jade,#00a86b);box-shadow:0 0 0 3px rgba(0,168,107,.12);}
.modal-overlay{position:fixed;inset:0;z-index:50;background:rgba(0,0,0,.4);backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;padding:1rem;}
.modal-box{background:oklch(var(--b1));border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.18);width:100%;max-width:420px;border:.5px solid var(--card-border);}
.modal-header{padding:1.125rem 1.25rem;border-bottom:.5px solid oklch(var(--bc)/.06);display:flex;align-items:center;justify-content:space-between;}
.modal-title{font-size:.95rem;font-weight:700;color:oklch(var(--bc));}
.modal-body{padding:1.25rem;display:flex;flex-direction:column;gap:.75rem;}
.modal-footer{padding:1rem 1.25rem;border-top:.5px solid oklch(var(--bc)/.06);display:flex;gap:.625rem;}
.page-btn{width:32px;height:32px;border-radius:8px;border:.5px solid oklch(var(--bc)/.1);background:oklch(var(--b1));display:flex;align-items:center;justify-content:center;font-size:.78rem;font-weight:600;color:oklch(var(--bc)/.6);cursor:pointer;transition:background 140ms,color 140ms;}
.page-btn:hover:not(:disabled){background:oklch(var(--b2));color:oklch(var(--bc))}.page-btn.active{background:var(--jade,#00a86b);color:#fff;border-color:transparent}.page-btn:disabled{opacity:.35;cursor:not-allowed}
.action-link{font-size:.75rem;font-weight:700;color:oklch(var(--bc)/.5);text-decoration:none;transition:color 140ms;}
.action-link:hover{color:oklch(var(--bc));}
.action-link.danger:hover{color:#ef4444;}
.spin-anim{animation:spin 1s linear infinite;}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:640px){.pp-page{padding:.875rem;gap:.875rem}.kpi-value{font-size:1.25rem}}
</style>
{% endblock %}

{% block content %}
{{ recipes_json|json_script:"recipes-data" }}

<div class="pp-page" x-data="recipesListApp()" x-init="init()" x-cloak>

    <!-- Header -->
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.75rem;">
        <div>
            <h1 style="font-size:1.3rem;font-weight:800;color:oklch(var(--bc));margin:0 0 2px;">Daftar Recipe</h1>
            <p style="font-size:.8rem;color:oklch(var(--bc)/.5);margin:0;">Kelola recipe produksi beserta biaya, yield, dan komposisi bahan</p>
        </div>
        <a href="{% url 'add_recipe' %}"
           style="height:34px;padding:0 14px;border-radius:9px;background:var(--jade,#00a86b);color:white;font-size:.8rem;font-weight:700;display:inline-flex;align-items:center;gap:6px;text-decoration:none;">
            <svg style="width:14px;height:14px;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
            Buat Recipe
        </a>
    </div>

    <!-- KPI -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-icon" style="background:rgba(59,130,246,.1);"><svg style="width:16px;height:16px;color:#3b82f6;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg></div>
            <div class="kpi-value" x-text="allRecipes.length"></div><div class="kpi-label">Total Recipe</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon" style="background:rgba(0,168,107,.1);"><svg style="width:16px;height:16px;color:#00a86b;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/></svg></div>
            <div class="kpi-value" x-text="filteredRecipes.length"></div><div class="kpi-label">Tampil</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon" style="background:rgba(139,92,246,.1);"><svg style="width:16px;height:16px;color:#8b5cf6;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg></div>
            <div class="kpi-value" x-text="categoryCount"></div><div class="kpi-label">Kategori Aktif</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon" style="background:rgba(0,168,107,.1);"><svg style="width:16px;height:16px;color:#00a86b;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></div>
            <div class="kpi-value" style="color:#00a86b;" x-text="formatCurrencyShort(avgCostPerUnit)"></div><div class="kpi-label">Avg Cost/Unit</div>
        </div>
    </div>

    <!-- Toolbar -->
    <div class="pp-toolbar">
        <div style="display:flex;align-items:center;gap:.625rem;flex-wrap:wrap;">
            <div style="position:relative;">
                <svg style="position:absolute;left:.625rem;top:50%;transform:translateY(-50%);width:14px;height:14px;color:oklch(var(--bc)/.35);" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0"/></svg>
                <input type="text" class="form-input" style="padding-left:2rem;width:240px;height:34px;font-size:.8rem;" placeholder="Cari nama, kategori, atau SKU bahan..." x-model.debounce.200ms="searchQuery" @input="filterRecipes()">
            </div>
            <select class="form-input" style="height:34px;font-size:.8rem;padding:.375rem .75rem;width:auto;" x-model="categoryFilter" @change="filterRecipes()">
                <option value="">Semua Kategori</option>
                {% for category in categories %}
                <option value="{{ category.id }}">{{ category.name }}</option>
                {% endfor %}
            </select>
            <button @click="resetFilters()"
                    style="height:34px;padding:0 12px;border-radius:8px;border:.5px solid oklch(var(--bc)/.12);background:oklch(var(--b2));font-size:.78rem;font-weight:600;color:oklch(var(--bc)/.5);cursor:pointer;">
                Reset
            </button>
        </div>
        <span style="font-size:.75rem;color:oklch(var(--bc)/.4);white-space:nowrap;"><span x-text="filteredRecipes.length"></span> recipe</span>
    </div>

    <!-- Table -->
    <div class="section-card">
        <div class="section-card-header">
            <span class="section-card-title">Recipe Records</span>
            <span style="font-size:.72rem;color:oklch(var(--bc)/.4);">Halaman <span x-text="currentPage"></span> / <span x-text="totalPages"></span></span>
        </div>
        <div style="overflow-x:auto;">
            <table class="dash-table">
                <thead><tr>
                    <th @click="sortBy('name')">
                        Recipe <span class="sort-icon" :class="sortColumn==='name'?'active':''"><span x-text="sortColumn==='name'?(sortDirection==='asc'?'↑':'↓'):'↕'"></span></span>
                    </th>
                    <th @click="sortBy('category')">
                        Kategori <span class="sort-icon" :class="sortColumn==='category'?'active':''"><span x-text="sortColumn==='category'?(sortDirection==='asc'?'↑':'↓'):'↕'"></span></span>
                    </th>
                    <th class="r" @click="sortBy('ingredients_count')">
                        Bahan <span class="sort-icon" :class="sortColumn==='ingredients_count'?'active':''"><span x-text="sortColumn==='ingredients_count'?(sortDirection==='asc'?'↑':'↓'):'↕'"></span></span>
                    </th>
                    <th class="r" @click="sortBy('cost_per_unit')">
                        Cost/Unit <span class="sort-icon" :class="sortColumn==='cost_per_unit'?'active':''"><span x-text="sortColumn==='cost_per_unit'?(sortDirection==='asc'?'↑':'↓'):'↕'"></span></span>
                    </th>
                    <th @click="sortBy('created_at')">
                        Dibuat <span class="sort-icon" :class="sortColumn==='created_at'?'active':''"><span x-text="sortColumn==='created_at'?(sortDirection==='asc'?'↑':'↓'):'↕'"></span></span>
                    </th>
                    <th class="r">Aksi</th>
                </tr></thead>
                <tbody>
                    <template x-for="recipe in pagedRecipes" :key="recipe.id">
                        <tr style="cursor:pointer;" @click="goDetail(recipe.id)">
                            <td>
                                <div style="font-weight:600;color:oklch(var(--bc));" x-text="recipe.name"></div>
                                <div style="font-size:.7rem;color:oklch(var(--bc)/.45);margin-top:.1rem;">
                                    Yield <span x-text="fmtQty(recipe.yield_quantity)"></span> <span x-text="recipe.yield_unit||'unit'"></span>
                                </div>
                            </td>
                            <td style="font-size:.8rem;color:oklch(var(--bc)/.6);" x-text="recipe.category||'Tanpa kategori'"></td>
                            <td class="r" style="font-weight:700;" x-text="recipe.ingredients_count"></td>
                            <td class="r" style="font-weight:700;color:#00a86b;" x-text="formatCurrency(recipe.cost_per_unit||0)"></td>
                            <td style="font-size:.78rem;color:oklch(var(--bc)/.5);" x-text="recipe.created_at||'—'"></td>
                            <td class="r" @click.stop>
                                <div style="display:flex;align-items:center;justify-content:flex-end;gap:.875rem;">
                                    <a :href="detailUrl(recipe.id)" class="action-link">Detail</a>
                                    <a :href="editUrl(recipe.id)" class="action-link" style="color:#3b82f6;">Edit</a>
                                    <button @click="confirmDelete(recipe)" class="action-link danger" style="background:none;border:none;cursor:pointer;padding:0;">Hapus</button>
                                </div>
                            </td>
                        </tr>
                    </template>
                    <tr x-show="filteredRecipes.length===0">
                        <td colspan="6" style="text-align:center;padding:2.5rem;color:oklch(var(--bc)/.35);font-size:.82rem;">
                            Tidak ada recipe yang cocok. <a href="{% url 'add_recipe' %}" style="color:var(--jade,#00a86b);font-weight:700;text-decoration:none;">Buat recipe baru →</a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Pagination -->
    <div x-show="totalPages > 1" style="display:flex;justify-content:center;align-items:center;gap:.375rem;">
        <button class="page-btn" @click="goToPage(currentPage-1)" :disabled="currentPage===1">
            <svg style="width:12px;height:12px;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <template x-for="p in displayedPages" :key="p+'_'+$index">
            <template x-if="p==='...'"><span style="padding:0 .375rem;font-size:.78rem;color:oklch(var(--bc)/.4);">…</span></template>
            <template x-if="p!=='...'"><button class="page-btn" :class="p===currentPage?'active':''" @click="goToPage(p)" x-text="p"></button></template>
        </template>
        <button class="page-btn" @click="goToPage(currentPage+1)" :disabled="currentPage===totalPages">
            <svg style="width:12px;height:12px;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
        </button>
    </div>

</div>

<!-- Delete modal -->
<div x-show="showDeleteModal" x-cloak class="modal-overlay" @click.self="showDeleteModal=false">
    <div class="modal-box" x-show="showDeleteModal" x-transition:enter="transition duration-200" x-transition:enter-start="opacity-0 scale-95" x-transition:enter-end="opacity-100 scale-100" @click.stop>
        <div class="modal-header">
            <span class="modal-title">Hapus Recipe</span>
            <button @click="showDeleteModal=false" style="background:none;border:none;cursor:pointer;color:oklch(var(--bc)/.4);font-size:.9rem;">✕</button>
        </div>
        <div class="modal-body">
            <div style="width:48px;height:48px;border-radius:12px;background:rgba(239,68,68,.1);display:flex;align-items:center;justify-content:center;margin-bottom:.25rem;">
                <svg style="width:20px;height:20px;color:#ef4444;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </div>
            <p style="font-size:.82rem;color:oklch(var(--bc)/.6);line-height:1.5;">
                Recipe <strong x-text="recipeToDelete?.name"></strong> akan dihapus permanen dan tidak dapat dikembalikan.
            </p>
        </div>
        <div class="modal-footer">
            <button @click="showDeleteModal=false" style="flex:1;padding:.625rem;border-radius:9px;border:.5px solid oklch(var(--bc)/.12);background:oklch(var(--b2));font-size:.82rem;font-weight:600;color:oklch(var(--bc)/.6);cursor:pointer;">Batal</button>
            <button @click="deleteRecipe()" :disabled="isDeleting" style="flex:1;padding:.625rem;border-radius:9px;background:#ef4444;border:none;color:#fff;font-size:.82rem;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:.375rem;">
                <svg x-show="isDeleting" class="spin-anim" style="width:13px;height:13px;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                <span x-text="isDeleting?'Menghapus...':'Ya, Hapus'"></span>
            </button>
        </div>
    </div>
</div>

{% csrf_token %}

<script>
function recipesListApp(){return{
    allRecipes:[],filteredRecipes:[],
    searchQuery:'{{ query|escapejs }}',categoryFilter:'{{ category_filter|escapejs }}',
    sortColumn:'name',sortDirection:'asc',
    currentPage:1,pageSize:20,
    showDeleteModal:false,recipeToDelete:null,isDeleting:false,

    get totalPages(){return Math.max(1,Math.ceil(this.filteredRecipes.length/this.pageSize));},
    get pagedRecipes(){const s=(this.currentPage-1)*this.pageSize;return this.filteredRecipes.slice(s,s+this.pageSize);},
    get displayedPages(){
        const total=this.totalPages,cur=this.currentPage;
        if(total<=7) return Array.from({length:total},(_,i)=>i+1);
        if(cur<=4) return [1,2,3,4,5,'...',total];
        if(cur>=total-3) return [1,'...',total-4,total-3,total-2,total-1,total];
        return [1,'...',cur-1,cur,cur+1,'...',total];
    },
    get categoryCount(){return new Set(this.filteredRecipes.map(r=>r.category).filter(Boolean)).size;},
    get avgCostPerUnit(){
        if(!this.filteredRecipes.length) return 0;
        return this.filteredRecipes.reduce((s,r)=>s+Number(r.cost_per_unit||0),0)/this.filteredRecipes.length;
    },

    init(){
        const el=document.getElementById('recipes-data');
        if(el?.textContent) try{this.allRecipes=JSON.parse(el.textContent)||[];}catch(e){}
        this.filterRecipes();
    },
    filterRecipes(){
        const q=this.searchQuery.toLowerCase().trim();
        let rows=this.allRecipes.filter(r=>{
            const mc=!this.categoryFilter||String(r.category_id||'')===String(this.categoryFilter);
            const hs=[r.name,r.category,...(r.ingredients||[]).map(i=>i?.sku||'')];
            const mq=!q||hs.some(v=>String(v||'').toLowerCase().includes(q));
            return mc&&mq;
        });
        this.filteredRecipes=this._sorted(rows);
        this.currentPage=1;
    },
    resetFilters(){this.searchQuery='';this.categoryFilter='';this.filterRecipes();},
    sortBy(col){
        if(this.sortColumn===col) this.sortDirection=this.sortDirection==='asc'?'desc':'asc';
        else{this.sortColumn=col;this.sortDirection='asc';}
        this.filteredRecipes=this._sorted(this.filteredRecipes);
    },
    _sorted(rows){
        return[...rows].sort((a,b)=>{
            let x=a[this.sortColumn]??'',y=b[this.sortColumn]??'';
            if(typeof x==='string') x=x.toLowerCase();
            if(typeof y==='string') y=y.toLowerCase();
            if(x===y) return 0;
            const r=x>y?1:-1;
            return this.sortDirection==='asc'?r:-r;
        });
    },
    goToPage(p){this.currentPage=Math.min(Math.max(p,1),this.totalPages);},
    goDetail(id){window.location.href=`{% url 'recipe_detail' 0 %}`.replace('/0/',`/${id}/`);},
    detailUrl(id){return`{% url 'recipe_detail' 0 %}`.replace('/0/',`/${id}/`);},
    editUrl(id){return`{% url 'edit_recipe' 0 %}`.replace('/0/',`/${id}/edit/`);},
    confirmDelete(r){this.recipeToDelete=r;this.showDeleteModal=true;},
    async deleteRecipe(){
        if(!this.recipeToDelete||this.isDeleting) return;
        this.isDeleting=true;
        const csrf=document.querySelector('[name=csrfmiddlewaretoken]')?.value||'';
        try{
            const res=await fetch(`{% url 'recipe_delete' 0 %}`.replace('/0/',`/${this.recipeToDelete.id}/delete-legacy/`),{method:'POST',headers:{'Accept':'application/json','X-CSRFToken':csrf},body:new URLSearchParams({_ajax:'1'})});
            const d=await res.json();
            if(!res.ok||!d.success) throw new Error(d.message||'Gagal menghapus recipe.');
            this.allRecipes=this.allRecipes.filter(r=>r.id!==this.recipeToDelete.id);
            this.filterRecipes();
            this.showDeleteModal=false;this.recipeToDelete=null;
        }catch(err){alert(err.message||'Gagal menghapus recipe.');}
        finally{this.isDeleting=false;}
    },
    formatCurrency(n){return new Intl.NumberFormat('id-ID',{style:'currency',currency:'IDR',minimumFractionDigits:0}).format(n||0);},
    formatCurrencyShort(n){if(n>=1e6)return'Rp '+(n/1e6).toFixed(1)+'jt';if(n>=1e3)return'Rp '+(n/1e3).toFixed(0)+'rb';return'Rp '+Math.round(n||0);},
    fmtQty(n){return Number(n||0).toLocaleString('id-ID',{maximumFractionDigits:2});},
};}
</script>
{% endblock %}


<!-- ════════════════════════════════════════════════════════
     FILE 2 OF 3 — recipe_form.html
════════════════════════════════════════════════════════ -->
{% extends "base/base_hybrid.html" %}
{% load i18n %}{% load static %}
{% block title %}{% if is_edit %}Edit{% else %}Buat{% endif %} Recipe — Lumra{% endblock %}

{% block extra_css %}
<style>
:root{--card-radius:12px;--card-shadow:0 1px 3px rgba(0,0,0,.06),0 4px 16px rgba(0,0,0,.04);--card-border:rgba(0,0,0,.06);}
.rf-page{padding:1.25rem;display:flex;flex-direction:column;gap:1rem;max-width:1100px;margin:0 auto;}
.section-card{background:oklch(var(--b1));border:.5px solid var(--card-border);border-radius:var(--card-radius);box-shadow:var(--card-shadow);overflow:hidden;}
.section-card-header{padding:1rem 1.25rem;border-bottom:.5px solid oklch(var(--bc)/.06);display:flex;align-items:center;justify-content:space-between;gap:.5rem;}
.section-card-title{font-size:.85rem;font-weight:700;color:oklch(var(--bc));text-transform:uppercase;letter-spacing:.07em;}
.section-card-body{padding:1.25rem;}
.form-group{display:flex;flex-direction:column;gap:.375rem;}
.form-label{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:oklch(var(--bc)/.5);}
.form-input{background:oklch(var(--b2));border:.5px solid oklch(var(--bc)/.12);border-radius:8px;padding:.6rem .875rem;font-size:.85rem;color:oklch(var(--bc));width:100%;outline:none;transition:border-color 150ms,box-shadow 150ms;}
.form-input:focus{border-color:var(--jade,#00a86b);box-shadow:0 0 0 3px rgba(0,168,107,.12);}
.form-input::placeholder{color:oklch(var(--bc)/.3);}
.form-input.err{border-color:#ef4444;box-shadow:0 0 0 3px rgba(239,68,68,.1);}
.form-input.err:focus{border-color:#ef4444;}
textarea.form-input{resize:vertical;}
.form-error{font-size:.72rem;color:#ef4444;margin-top:.25rem;}
/* 2-col layout */
.rf-layout{display:grid;grid-template-columns:1fr 300px;gap:1rem;align-items:start;}
@media(max-width:900px){.rf-layout{grid-template-columns:1fr}}
.form-2col{display:grid;grid-template-columns:1fr 1fr;gap:.875rem;}
@media(max-width:640px){.rf-page{padding:.875rem;gap:.875rem}.form-2col{grid-template-columns:1fr}}
/* ingredient table */
.ing-table-wrap{overflow-x:auto;}
.ing-table{width:100%;border-collapse:collapse;font-size:.82rem;min-width:540px;}
.ing-table th{padding:.5rem .875rem;text-align:left;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:oklch(var(--bc)/.4);border-bottom:.5px solid oklch(var(--bc)/.07);}
.ing-table td{padding:.5rem .875rem;border-bottom:.5px solid oklch(var(--bc)/.05);vertical-align:middle;}
.ing-table tr:last-child td{border-bottom:none;}
.ing-table tr:hover td{background:oklch(var(--b2));}
.ing-input{background:transparent;border:none;outline:none;width:100%;font-size:.82rem;color:oklch(var(--bc));}
.ing-input.err{background:rgba(239,68,68,.07);border-radius:5px;padding:2px 6px;}
.ing-input::placeholder{color:oklch(var(--bc)/.3);}
.ing-input:focus{background:oklch(var(--b3));border-radius:5px;padding:2px 6px;}
/* sku match */
.sku-match{font-size:.65rem;font-weight:700;padding:1px 7px;border-radius:20px;background:rgba(0,168,107,.1);color:#065f46;}
/* sidebar stat */
.stat-tile{background:oklch(var(--b2));border-radius:9px;padding:.875rem 1rem;display:flex;flex-direction:column;gap:.25rem;}
.stat-tile-val{font-size:1.25rem;font-weight:800;letter-spacing:-.02em;color:oklch(var(--bc));}
.stat-tile-lbl{font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:oklch(var(--bc)/.45);}
/* cost dark */
.cost-dark{background:oklch(20% .02 240);border-radius:var(--card-radius);overflow:hidden;color:#e2e8f0;}
[data-theme="dark"] .cost-dark{background:oklch(12% .02 240);}
.cd-row{display:flex;justify-content:space-between;align-items:center;padding:.5rem 1.125rem;font-size:.82rem;border-bottom:.5px solid rgba(255,255,255,.07);}
.cd-row:last-child{border-bottom:none;}.cd-label{color:rgba(255,255,255,.45);}
.spin-anim{animation:spin 1s linear infinite;}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
{% endblock %}

{% block content %}
{{ variants_data|json_script:"recipe-variants-data" }}
{{ formset.management_form }}

<div class="rf-page" x-data="recipeFormApp()" x-init="init()" x-cloak>

    <!-- Header -->
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.75rem;">
        <div>
            <nav style="display:flex;align-items:center;gap:.5rem;font-size:.75rem;color:oklch(var(--bc)/.5);margin-bottom:.375rem;">
                <a href="{% url 'recipe_list' %}" style="color:inherit;text-decoration:none;">Recipe</a>
                <span>/</span>
                <span style="color:oklch(var(--bc));font-weight:600;" x-text="isEdit?'Edit Recipe':'Buat Recipe Baru'"></span>
            </nav>
            <h1 style="font-size:1.3rem;font-weight:800;color:oklch(var(--bc));margin:0;" x-text="isEdit?'Edit Recipe':'Buat Recipe Baru'"></h1>
        </div>
        <div style="display:flex;gap:.625rem;">
            <a href="{% url 'recipe_list' %}" style="height:34px;padding:0 14px;border-radius:9px;border:.5px solid oklch(var(--bc)/.15);background:oklch(var(--b2));font-size:.8rem;font-weight:600;color:oklch(var(--bc)/.6);display:inline-flex;align-items:center;text-decoration:none;">Kembali</a>
            <button @click="submitForm()" :disabled="isSubmitting"
                    style="height:34px;padding:0 14px;border-radius:9px;background:var(--jade,#00a86b);border:none;color:#fff;font-size:.8rem;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:6px;">
                <svg x-show="isSubmitting" class="spin-anim" style="width:13px;height:13px;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                <span x-text="isSubmitting?'Menyimpan...':(isEdit?'Simpan Perubahan':'Simpan Recipe')"></span>
            </button>
        </div>
    </div>

    <!-- 2-col layout -->
    <div class="rf-layout">

        <!-- ════ LEFT ════ -->
        <div style="display:flex;flex-direction:column;gap:1rem;">

            <!-- Identitas -->
            <div class="section-card">
                <div class="section-card-header"><span class="section-card-title">Identitas Recipe</span></div>
                <div class="section-card-body">
                    <div class="form-group" style="margin-bottom:.875rem;">
                        <label class="form-label">Nama Recipe *</label>
                        <input type="text" class="form-input" :class="errors.name?'err':''" placeholder="Contoh: Iced Americano" x-model.trim="formData.name" @blur="validateField('name')">
                        <span class="form-error" x-show="errors.name" x-text="errors.name"></span>
                    </div>
                    <div class="form-2col" style="margin-bottom:.875rem;">
                        <div class="form-group">
                            <label class="form-label">Kategori *</label>
                            <select class="form-input" :class="errors.category?'err':''" x-model="formData.category" @change="validateField('category')">
                                <option value="">— Pilih kategori —</option>
                                {% for category in categories %}
                                <option value="{{ category.id }}">{{ category.name }}</option>
                                {% endfor %}
                            </select>
                            <span class="form-error" x-show="errors.category" x-text="errors.category"></span>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Waktu Persiapan (menit)</label>
                            <input type="number" class="form-input" min="0" placeholder="5" x-model.number="formData.preparation_time">
                        </div>
                    </div>
                    <div class="form-2col" style="margin-bottom:.875rem;">
                        <div class="form-group">
                            <label class="form-label">Yield Quantity</label>
                            <input type="number" class="form-input" min="0" step="0.01" placeholder="1" x-model.number="formData.yield_quantity">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Yield Unit</label>
                            <select class="form-input" x-model="formData.yield_unit">
                                <option value="">— Pilih satuan —</option>
                                {% for unit in units %}<option value="{{ unit.id }}">{{ unit.symbol }}</option>{% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Deskripsi</label>
                        <textarea class="form-input" rows="2" placeholder="Ringkasan singkat fungsi atau karakter recipe" x-model="formData.description"></textarea>
                    </div>
                </div>
            </div>

            <!-- Komposisi Bahan -->
            <div class="section-card">
                <div class="section-card-header">
                    <span class="section-card-title">Komposisi Bahan</span>
                    <button @click="addIngredient()" type="button"
                            style="font-size:.75rem;font-weight:700;color:var(--jade,#00a86b);background:none;border:none;cursor:pointer;display:flex;align-items:center;gap:.375rem;">
                        <svg style="width:13px;height:13px;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
                        Tambah Bahan
                    </button>
                </div>
                <div class="ing-table-wrap">
                    <table class="ing-table">
                        <thead><tr>
                            <th style="width:36%;">Variant Bahan</th>
                            <th style="width:15%;">Qty</th>
                            <th style="width:20%;">Satuan</th>
                            <th style="width:22%;">Est. Cost</th>
                            <th style="width:7%;"></th>
                        </tr></thead>
                        <tbody>
                            <template x-for="(ing, i) in ingredients" :key="ing._key">
                                <tr x-show="!ing._deleted">
                                    <td>
                                        <div style="display:flex;flex-direction:column;gap:.25rem;">
                                            <select class="ing-input" :class="ingredientErrors[i]?.variant?'err':''" x-model="ing.variant" @change="syncMeta(i);validateIng(i)">
                                                <option value="">— Pilih bahan —</option>
                                                <template x-for="v in variants" :key="v.id">
                                                    <option :value="String(v.id)" x-text="v.sku+' · '+v.name"></option>
                                                </template>
                                            </select>
                                            <span x-show="ing.variant_label&&!ingredientErrors[i]?.variant" class="sku-match" x-text="'✓ '+ing.variant_label"></span>
                                            <span x-show="ingredientErrors[i]?.variant" class="form-error" x-text="ingredientErrors[i]?.variant"></span>
                                        </div>
                                    </td>
                                    <td>
                                        <input type="number" class="ing-input" :class="ingredientErrors[i]?.quantity?'err':''" min="0.01" step="0.01" placeholder="0" x-model.number="ing.quantity" @blur="validateIng(i)">
                                        <span x-show="ingredientErrors[i]?.quantity" class="form-error" x-text="ingredientErrors[i]?.quantity"></span>
                                    </td>
                                    <td>
                                        <select class="ing-input" :class="ingredientErrors[i]?.unit?'err':''" x-model="ing.unit" @change="validateIng(i)">
                                            <option value="">—</option>
                                            {% for unit in units %}<option value="{{ unit.id }}">{{ unit.symbol }}</option>{% endfor %}
                                        </select>
                                        <span x-show="ingredientErrors[i]?.unit" class="form-error" x-text="ingredientErrors[i]?.unit"></span>
                                    </td>
                                    <td style="font-size:.78rem;color:oklch(var(--bc)/.5);font-family:ui-monospace,monospace;" x-text="formatCurrency(ingCost(ing))"></td>
                                    <td style="text-align:center;">
                                        <button @click="removeIngredient(i)" :disabled="ingredients.filter(x=>!x._deleted).length<=1" type="button"
                                                style="background:none;border:none;cursor:pointer;color:oklch(var(--bc)/.3);font-size:.8rem;" title="Hapus">
                                            <svg style="width:13px;height:13px;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                                        </button>
                                    </td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </div>
                <span class="form-error" x-show="errors.ingredients" x-text="errors.ingredients" style="display:block;padding:.5rem 1.25rem;"></span>
                <div style="padding:.625rem 1.25rem;border-top:.5px solid oklch(var(--bc)/.05);font-size:.72rem;color:oklch(var(--bc)/.4);">
                    ✦ Pilih variant bahan yang terdaftar agar biaya recipe dihitung stabil.
                </div>
            </div>

            <!-- Instruksi -->
            <div class="section-card">
                <div class="section-card-header"><span class="section-card-title">Instruksi Pembuatan</span></div>
                <div class="section-card-body">
                    <div class="form-group">
                        <textarea class="form-input" :class="errors.instructions?'err':''" rows="8" placeholder="Tuliskan langkah pembuatan secara berurutan..." x-model="formData.instructions" @blur="validateField('instructions')"></textarea>
                        <span class="form-error" x-show="errors.instructions" x-text="errors.instructions"></span>
                    </div>
                </div>
            </div>

        </div>

        <!-- ════ RIGHT: summary sidebar ════ -->
        <div style="position:sticky;top:1.25rem;display:flex;flex-direction:column;gap:1rem;">

            <!-- Stats -->
            <div class="section-card">
                <div class="section-card-header"><span class="section-card-title">Ringkasan</span></div>
                <div style="padding:.875rem 1.125rem;display:flex;flex-direction:column;gap:.625rem;">
                    <div class="stat-tile">
                        <div class="stat-tile-val" x-text="ingredients.filter(i=>!i._deleted).length"></div>
                        <div class="stat-tile-lbl">Bahan Aktif</div>
                    </div>
                    <div class="stat-tile">
                        <div class="stat-tile-val" style="color:#00a86b;" x-text="formatCurrency(estimatedTotalCost)"></div>
                        <div class="stat-tile-lbl">Est. Cost Total</div>
                    </div>
                    <div class="stat-tile">
                        <div class="stat-tile-val" x-text="formatCurrency(costPerUnit)"></div>
                        <div class="stat-tile-lbl">Cost / <span x-text="yieldUnitLabel||'Unit'"></span></div>
                    </div>
                </div>
            </div>

            <!-- Cost dark breakdown -->
            <div class="cost-dark">
                <div style="padding:.75rem 1.125rem;border-bottom:.5px solid rgba(255,255,255,.07);">
                    <span style="font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:rgba(255,255,255,.4);">Breakdown Biaya</span>
                </div>
                <template x-for="ing in ingredients.filter(i=>!i._deleted&&i.variant)" :key="ing._key">
                    <div class="cd-row" x-show="ingCost(ing)>0">
                        <span class="cd-label" style="font-size:.75rem;" x-text="ing.variant_label||'—'"></span>
                        <span style="font-weight:700;font-size:.78rem;" x-text="formatCurrency(ingCost(ing))"></span>
                    </div>
                </template>
                <div x-show="estimatedTotalCost===0" style="padding:1rem 1.125rem;font-size:.75rem;color:rgba(255,255,255,.3);text-align:center;">
                    Pilih bahan dengan harga untuk melihat breakdown
                </div>
                <div x-show="estimatedTotalCost>0" style="padding:.75rem 1.125rem;background:rgba(0,168,107,.12);border-top:.5px solid rgba(0,168,107,.2);">
                    <div style="font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#34d399;margin-bottom:.25rem;">Total</div>
                    <div style="font-size:1rem;font-weight:800;color:#34d399;" x-text="formatCurrency(estimatedTotalCost)"></div>
                </div>
            </div>

            <!-- Submit -->
            <button @click="submitForm()" :disabled="isSubmitting"
                    style="width:100%;padding:.75rem;border-radius:9px;background:var(--jade,#00a86b);border:none;color:#fff;font-size:.85rem;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:.5rem;">
                <svg x-show="isSubmitting" class="spin-anim" style="width:14px;height:14px;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                <span x-text="isSubmitting?'Menyimpan...':(isEdit?'Simpan Perubahan':'Simpan Recipe')"></span>
            </button>
        </div>

    </div><!-- end rf-layout -->
</div>

{% csrf_token %}

<script>
const EXISTING_RECIPE_INGREDIENTS=[
  {% for fs_form in formset %}{% if fs_form.instance.pk %}{
    _key:{{forloop.counter}},id:{{fs_form.instance.pk|default:"null"}},
    variant:"{{fs_form.instance.variant_id|default:''|escapejs}}",
    quantity:{{fs_form.instance.quantity|default:"0"}},
    unit:"{{fs_form.instance.unit_id|default:''|escapejs}}",
    variant_label:"{{fs_form.instance.variant.sku|default:''|escapejs}}{% if fs_form.instance.variant_id %} · {{fs_form.instance.variant.product.name|default:fs_form.instance.variant.sku|escapejs}}{% endif %}",
  },{% endif %}{% endfor %}
];

function recipeFormApp(){return{
    isEdit:{% if is_edit %}true{% else %}false{% endif %},
    isSubmitting:false,
    variants:[],keySeed:1000,
    formData:{
        name:'{{form.name.value|default:""|escapejs}}',
        category:'{{form.category.value|default:""|escapejs}}',
        description:'{{form.description.value|default:""|escapejs}}',
        instructions:'{{form.instructions.value|default:""|escapejs}}',
        yield_quantity:'{{form.yield_quantity.value|default:"1"|escapejs}}',
        yield_unit:'{{form.yield_unit.value|default:""|escapejs}}',
        preparation_time:'{{form.preparation_time.value|default:"5"|escapejs}}',
    },
    ingredients:[],errors:{},ingredientErrors:{},

    get estimatedTotalCost(){
        return this.ingredients.filter(i=>!i._deleted).reduce((s,i)=>s+this.ingCost(i),0);
    },
    get costPerUnit(){
        const y=Number(this.formData.yield_quantity||0);
        return y>0?this.estimatedTotalCost/y:this.estimatedTotalCost;
    },
    get yieldUnitLabel(){
        const el=document.querySelector('select[x-model="formData.yield_unit"]');
        if(!el) return '';
        const opt=[...el.options].find(o=>o.value===String(this.formData.yield_unit||''));
        return opt?opt.text:'';
    },

    ingCost(ing){
        const v=this.variants.find(x=>String(x.id)===String(ing.variant||''));
        return Number(ing.quantity||0)*Number(v?.price_buy||0);
    },
    emptyIng(){this.keySeed++;return{_key:this.keySeed,id:null,variant:'',quantity:1,unit:'',variant_label:''};},
    addIngredient(){this.ingredients.push(this.emptyIng());},
    removeIngredient(i){
        if(this.ingredients[i]?.id) this.ingredients[i]._deleted=true;
        else this.ingredients.splice(i,1);
        const ne={};
        Object.entries(this.ingredientErrors).forEach(([k,v])=>{
            const n=Number(k);
            if(n<i) ne[n]=v;
            if(n>i) ne[n-1]=v;
        });
        this.ingredientErrors=ne;
    },
    syncMeta(i){
        const ing=this.ingredients[i];
        const v=this.variants.find(x=>String(x.id)===String(ing.variant||''));
        ing.variant_label=v?`${v.sku} · ${v.name}`:'';
    },
    validateField(f){
        delete this.errors[f];
        if(f==='name'&&!this.formData.name) this.errors.name='Nama recipe wajib diisi.';
        if(f==='category'&&!this.formData.category) this.errors.category='Kategori wajib dipilih.';
        if(f==='instructions'&&!String(this.formData.instructions||'').trim()) this.errors.instructions='Instruksi pembuatan wajib diisi.';
        return!this.errors[f];
    },
    validateIng(i){
        const ing=this.ingredients[i];
        const e={};
        if(!ing.variant) e.variant='Bahan wajib dipilih.';
        if(!(Number(ing.quantity||0)>0)) e.quantity='Qty harus > 0.';
        if(!ing.unit) e.unit='Satuan wajib dipilih.';
        this.ingredientErrors={...this.ingredientErrors,[i]:e};
        return Object.keys(e).length===0;
    },
    validateAll(){
        this.errors={};
        let ok=true;
        ['name','category','instructions'].forEach(f=>{if(!this.validateField(f)) ok=false;});
        const visible=this.ingredients.filter(i=>!i._deleted);
        if(!visible.some(i=>i.variant&&Number(i.quantity||0)>0&&i.unit)){
            this.errors.ingredients='Tambahkan minimal satu bahan yang lengkap.';ok=false;
        }
        this.ingredients.forEach((_,i)=>{if(!this.ingredients[i]?._deleted&&!this.validateIng(i)) ok=false;});
        return ok;
    },
    async submitForm(){
        if(!this.validateAll()) return;
        this.isSubmitting=true;
        const fd=new FormData();
        fd.append('csrfmiddlewaretoken',document.querySelector('[name=csrfmiddlewaretoken]')?.value||'');
        fd.append('_ajax','1');
        ['name','category','description','instructions','yield_unit','preparation_time'].forEach(k=>fd.append(k,this.formData[k]||''));
        fd.append('yield_quantity',this.formData.yield_quantity||'1');
        fd.append('ingredients-TOTAL_FORMS',String(this.ingredients.length));
        fd.append('ingredients-INITIAL_FORMS',String(EXISTING_RECIPE_INGREDIENTS.filter(i=>i.id).length));
        fd.append('ingredients-MIN_NUM_FORMS','0');
        fd.append('ingredients-MAX_NUM_FORMS','1000');
        this.ingredients.forEach((ing,i)=>{
            fd.append(`ingredients-${i}-id`,ing.id||'');
            fd.append(`ingredients-${i}-variant`,ing.variant||'');
            fd.append(`ingredients-${i}-quantity`,ing.quantity||'');
            fd.append(`ingredients-${i}-unit`,ing.unit||'');
            fd.append(`ingredients-${i}-DELETE`,ing._deleted?'on':'');
        });
        try{
            const res=await fetch(window.location.href,{method:'POST',headers:{Accept:'application/json'},body:fd});
            const d=await res.json();
            if(!res.ok||!d.success){
                if(d.errors) Object.entries(d.errors).forEach(([f,msgs])=>{
                    const msg=Array.isArray(msgs)?msgs[0]:msgs;
                    if(f.startsWith('ingredient_')){
                        const parts=f.split('_'),idx=Number(parts[1]),sf=parts.slice(2).join('_');
                        this.ingredientErrors={...this.ingredientErrors,[idx]:{...(this.ingredientErrors[idx]||{}),[sf]:msg}};
                    } else{this.errors[f]=msg;}
                });
                throw new Error(d.message||'Gagal menyimpan recipe.');
            }
            window.location.href=`{% url 'recipe_detail' 0 %}`.replace('/0/',`/${d.recipe_id}/`);
        }catch(err){alert(err.message||'Gagal menyimpan recipe.');}
        finally{this.isSubmitting=false;}
    },
    init(){
        const el=document.getElementById('recipe-variants-data');
        if(el?.textContent) try{this.variants=JSON.parse(el.textContent)||[];}catch(e){}
        this.ingredients=EXISTING_RECIPE_INGREDIENTS.length
            ?EXISTING_RECIPE_INGREDIENTS.map(i=>({...i,quantity:Number(i.quantity||0)}))
            :[this.emptyIng()];
        this.ingredients.forEach((_,i)=>this.syncMeta(i));
    },
    formatCurrency(n){return new Intl.NumberFormat('id-ID',{style:'currency',currency:'IDR',minimumFractionDigits:0}).format(n||0);},
};}
</script>
{% endblock %}


<!-- ════════════════════════════════════════════════════════
     FILE 3 OF 3 — recipe_detail.html
════════════════════════════════════════════════════════ -->
{% extends "base/base_hybrid.html" %}
{% load i18n %}{% load static %}
{% block title %}Recipe Detail — Lumra{% endblock %}

{% block extra_css %}
<style>
:root{--card-radius:12px;--card-shadow:0 1px 3px rgba(0,0,0,.06),0 4px 16px rgba(0,0,0,.04);--card-border:rgba(0,0,0,.06);}
.rd-page{padding:1.25rem;display:flex;flex-direction:column;gap:1rem;max-width:1100px;margin:0 auto;}
.kpi-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.875rem;}
.kpi-tile{background:oklch(var(--b1));border:.5px solid var(--card-border);border-radius:var(--card-radius);box-shadow:var(--card-shadow);padding:1rem 1.25rem;}
.kpi-tile-val{font-size:1.4rem;font-weight:800;letter-spacing:-.02em;color:oklch(var(--bc));}
.kpi-tile-lbl{font-size:.7rem;font-weight:600;color:oklch(var(--bc)/.5);text-transform:uppercase;letter-spacing:.06em;margin-top:.25rem;}
.section-card{background:oklch(var(--b1));border:.5px solid var(--card-border);border-radius:var(--card-radius);box-shadow:var(--card-shadow);overflow:hidden;}
.section-card-header{padding:1rem 1.25rem;border-bottom:.5px solid oklch(var(--bc)/.06);display:flex;align-items:center;justify-content:space-between;gap:.5rem;flex-wrap:wrap;}
.section-card-title{font-size:.85rem;font-weight:700;color:oklch(var(--bc));text-transform:uppercase;letter-spacing:.07em;}
.rd-layout{display:grid;grid-template-columns:1fr 320px;gap:1rem;align-items:start;}
@media(max-width:900px){.rd-layout{grid-template-columns:1fr}}
.dash-table{width:100%;border-collapse:collapse;font-size:.82rem;}
.dash-table th{padding:.625rem 1rem;text-align:left;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:oklch(var(--bc)/.4);border-bottom:.5px solid oklch(var(--bc)/.07);}
.dash-table td{padding:.75rem 1rem;border-bottom:.5px solid oklch(var(--bc)/.05);color:oklch(var(--bc)/.8);vertical-align:middle;}
.dash-table tr:last-child td{border-bottom:none;}.dash-table tr:hover td{background:oklch(var(--b2));}
.dash-table th.r,.dash-table td.r{text-align:right;}
/* cost share bar */
.share-bar-wrap{width:60px;height:5px;background:oklch(var(--b3));border-radius:99px;overflow:hidden;display:inline-block;vertical-align:middle;margin-right:.375rem;}
.share-bar-fill{height:100%;border-radius:99px;background:var(--jade,#00a86b);}
/* meta row */
.meta-row{display:flex;justify-content:space-between;align-items:center;padding:.5rem .875rem;background:oklch(var(--b2));border-radius:8px;font-size:.82rem;margin-bottom:.375rem;}
.meta-lbl{color:oklch(var(--bc)/.5);}
.meta-val{font-weight:700;color:oklch(var(--bc));}
/* instructions */
.instructions-box{background:oklch(var(--b2));border-radius:10px;padding:.875rem 1rem;max-height:260px;overflow-y:auto;}
/* cost dark */
.cost-dark{background:oklch(20% .02 240);border-radius:var(--card-radius);overflow:hidden;color:#e2e8f0;}
[data-theme="dark"] .cost-dark{background:oklch(12% .02 240);}
.cd-row{display:flex;justify-content:space-between;align-items:center;padding:.5rem 1.125rem;font-size:.82rem;border-bottom:.5px solid rgba(255,255,255,.07);}
.cd-row:last-child{border-bottom:none;}.cd-label{color:rgba(255,255,255,.45);}
.form-input{background:oklch(var(--b2));border:.5px solid oklch(var(--bc)/.12);border-radius:8px;padding:.6rem .875rem;font-size:.85rem;color:oklch(var(--bc));width:100%;outline:none;transition:border-color 150ms,box-shadow 150ms;}
.form-input:focus{border-color:var(--jade,#00a86b);box-shadow:0 0 0 3px rgba(0,168,107,.12);}
.form-input::placeholder{color:oklch(var(--bc)/.3);}
@media(max-width:640px){.rd-page{padding:.875rem;gap:.875rem}.kpi-tile-val{font-size:1.2rem}}
</style>
{% endblock %}

{% block content %}
{{ recipe_data|json_script:"recipe-data" }}

<div class="rd-page" x-data="recipeDetailApp()" x-init="init()" x-cloak>

    <!-- Header -->
    <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:.75rem;">
        <div>
            <nav style="display:flex;align-items:center;gap:.5rem;font-size:.75rem;color:oklch(var(--bc)/.5);margin-bottom:.5rem;">
                <a href="{% url 'recipe_list' %}" style="color:inherit;text-decoration:none;">Recipe</a>
                <span>/</span>
                <span style="color:oklch(var(--bc));font-weight:600;" x-text="recipe.name||'Detail'"></span>
            </nav>
            <h1 style="font-size:1.3rem;font-weight:800;color:oklch(var(--bc));margin:0 0 .25rem;" x-text="recipe.name"></h1>
            <p style="font-size:.8rem;color:oklch(var(--bc)/.5);margin:0;">
                <span x-text="recipe.category||'Uncategorized'"></span>
                &bull;
                <span x-text="recipe.ingredients.length + ' bahan'"></span>
            </p>
        </div>
        <div style="display:flex;gap:.625rem;">
            <a href="{% url 'recipe_list' %}" style="height:34px;padding:0 14px;border-radius:9px;border:.5px solid oklch(var(--bc)/.15);background:oklch(var(--b2));font-size:.8rem;font-weight:600;color:oklch(var(--bc)/.6);display:inline-flex;align-items:center;text-decoration:none;">← Daftar</a>
            <a href="{% url 'edit_recipe' recipe.id %}" style="height:34px;padding:0 14px;border-radius:9px;background:var(--jade,#00a86b);border:none;color:#fff;font-size:.8rem;font-weight:700;display:inline-flex;align-items:center;text-decoration:none;">Edit Recipe</a>
        </div>
    </div>

    <!-- KPI strip -->
    <div class="kpi-strip">
        <div class="kpi-tile">
            <div class="kpi-tile-val" x-text="fmtQty(recipe.yield_quantity)"></div>
            <div class="kpi-tile-lbl">Yield (<span x-text="recipe.yield_unit||'unit'"></span>)</div>
        </div>
        <div class="kpi-tile">
            <div class="kpi-tile-val" x-text="(recipe.preparation_time||0)+' mnt'"></div>
            <div class="kpi-tile-lbl">Waktu Persiapan</div>
        </div>
        <div class="kpi-tile">
            <div class="kpi-tile-val" style="color:#00a86b;" x-text="formatCurrency(recipe.total_cost||0)"></div>
            <div class="kpi-tile-lbl">Total Cost</div>
        </div>
        <div class="kpi-tile">
            <div class="kpi-tile-val" x-text="formatCurrency(costPerUnit)"></div>
            <div class="kpi-tile-lbl">Cost / <span x-text="recipe.yield_unit||'unit'"></span></div>
        </div>
    </div>

    <!-- Main 2-col -->
    <div class="rd-layout">

        <!-- LEFT: Ingredients table -->
        <div style="display:flex;flex-direction:column;gap:1rem;">
            <div class="section-card">
                <div class="section-card-header">
                    <span class="section-card-title">Ingredients</span>
                    <div style="position:relative;">
                        <svg style="position:absolute;left:.625rem;top:50%;transform:translateY(-50%);width:13px;height:13px;color:oklch(var(--bc)/.35);" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0"/></svg>
                        <input type="text" class="form-input" style="padding-left:2rem;width:200px;height:30px;font-size:.78rem;" placeholder="Cari ingredient atau SKU..." x-model.debounce.200ms="searchQuery" @input="applyFilter()">
                    </div>
                </div>
                <div style="overflow-x:auto;">
                    <table class="dash-table">
                        <thead><tr>
                            <th>Ingredient</th>
                            <th class="r">Qty</th>
                            <th class="r">Unit Cost</th>
                            <th class="r">% Biaya</th>
                            <th class="r">Subtotal</th>
                        </tr></thead>
                        <tbody>
                            <template x-for="item in filteredIngredients" :key="item.id">
                                <tr>
                                    <td>
                                        <div style="font-weight:600;color:oklch(var(--bc));" x-text="item.name"></div>
                                        <div style="font-size:.7rem;font-family:ui-monospace,monospace;color:oklch(var(--bc)/.4);" x-text="item.sku||'—'"></div>
                                    </td>
                                    <td class="r" style="font-size:.8rem;" x-text="fmtQty(item.quantity)+' '+(item.unit||'')"></td>
                                    <td class="r" style="font-size:.8rem;" x-text="formatCurrency(item.unit_cost||0)"></td>
                                    <td class="r">
                                        <div style="display:flex;align-items:center;justify-content:flex-end;">
                                            <div class="share-bar-wrap">
                                                <div class="share-bar-fill" :style="`width:${sharePct(item)}%`"></div>
                                            </div>
                                            <span style="font-size:.75rem;font-weight:700;min-width:2.5rem;text-align:right;" x-text="sharePct(item)+'%'"></span>
                                        </div>
                                    </td>
                                    <td class="r" style="font-weight:700;" x-text="formatCurrency(item.subtotal_cost||0)"></td>
                                </tr>
                            </template>
                            <tr x-show="filteredIngredients.length===0">
                                <td colspan="5" style="text-align:center;padding:2.5rem;color:oklch(var(--bc)/.35);font-size:.82rem;">Tidak ada ingredient yang cocok</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Instructions -->
            <div class="section-card">
                <div class="section-card-header"><span class="section-card-title">Instruksi Pembuatan</span></div>
                <div style="padding:.875rem 1.25rem;">
                    <div class="instructions-box">
                        <p style="font-size:.82rem;line-height:1.7;white-space:pre-line;color:oklch(var(--bc)/.7);" x-text="recipe.instructions||'Belum ada instruksi.'"></p>
                    </div>
                </div>
            </div>
        </div>

        <!-- RIGHT sidebar -->
        <div style="position:sticky;top:1.25rem;display:flex;flex-direction:column;gap:1rem;">

            <!-- Cost dark summary -->
            <div class="cost-dark">
                <div style="padding:.75rem 1.125rem;border-bottom:.5px solid rgba(255,255,255,.07);">
                    <span style="font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:rgba(255,255,255,.4);">Cost Breakdown</span>
                </div>
                <template x-for="item in recipe.ingredients.slice(0,6)" :key="item.id">
                    <div class="cd-row">
                        <span class="cd-label" style="font-size:.75rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:60%;" x-text="item.name||'—'"></span>
                        <span style="font-weight:700;font-size:.78rem;" x-text="formatCurrency(item.subtotal_cost||0)"></span>
                    </div>
                </template>
                <div x-show="recipe.ingredients.length>6" style="padding:.375rem 1.125rem;font-size:.7rem;color:rgba(255,255,255,.3);text-align:center;" x-text="'+'+(recipe.ingredients.length-6)+' lainnya'"></div>
                <div x-show="recipe.total_cost>0" style="padding:.75rem 1.125rem;background:rgba(0,168,107,.12);border-top:.5px solid rgba(0,168,107,.2);">
                    <div style="font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#34d399;margin-bottom:.25rem;">Total Cost</div>
                    <div style="font-size:1rem;font-weight:800;color:#34d399;" x-text="formatCurrency(recipe.total_cost||0)"></div>
                </div>
            </div>

            <!-- Metadata -->
            <div class="section-card">
                <div class="section-card-header"><span class="section-card-title">Metadata</span></div>
                <div style="padding:.875rem 1.125rem;">
                    <div class="meta-row"><span class="meta-lbl">Kategori</span><span class="meta-val" x-text="recipe.category||'—'"></span></div>
                    <div class="meta-row"><span class="meta-lbl">Dibuat</span><span class="meta-val" style="font-size:.78rem;" x-text="recipe.created_at||'—'"></span></div>
                    <div class="meta-row"><span class="meta-lbl">Diperbarui</span><span class="meta-val" style="font-size:.78rem;" x-text="recipe.updated_at||'—'"></span></div>
                    <div class="meta-row">
                        <span class="meta-lbl">BOM Terkait</span>
                        <template x-if="recipe.bom_id">
                            <a :href="`{% url 'bom_detail' 0 %}`.replace('/0/',`/${recipe.bom_id}/`)"
                               style="font-size:.8rem;font-weight:700;color:var(--jade,#00a86b);text-decoration:none;">Lihat BOM →</a>
                        </template>
                        <span x-show="!recipe.bom_id" class="meta-val" style="color:oklch(var(--bc)/.35);">Belum ada BOM</span>
                    </div>
                </div>
            </div>

            <!-- Description -->
            <div class="section-card" x-show="recipe.description">
                <div class="section-card-header"><span class="section-card-title">Deskripsi</span></div>
                <div style="padding:.875rem 1.25rem;">
                    <p style="font-size:.82rem;line-height:1.6;color:oklch(var(--bc)/.7);" x-text="recipe.description"></p>
                </div>
            </div>

        </div><!-- end right -->
    </div><!-- end rd-layout -->

</div>

<script>
function recipeDetailApp(){return{
    recipe:{ingredients:[]},filteredIngredients:[],searchQuery:'',

    get costPerUnit(){
        if(Number(this.recipe.cost_per_unit||0)>0) return Number(this.recipe.cost_per_unit||0);
        const y=Number(this.recipe.yield_quantity||1);
        return Number(this.recipe.total_cost||0)/(y||1);
    },
    sharePct(item){
        const total=Number(this.recipe.total_cost||0);
        if(!total) return 0;
        return Math.round((Number(item.subtotal_cost||0)/total)*100);
    },

    init(){
        const el=document.getElementById('recipe-data');
        if(!el?.textContent) return;
        try{this.recipe=JSON.parse(el.textContent)||{ingredients:[]};}
        catch(e){this.recipe={ingredients:[]};}
        this.applyFilter();
    },
    applyFilter(){
        const q=this.searchQuery.toLowerCase().trim();
        this.filteredIngredients=(this.recipe.ingredients||[]).filter(i=>
            !q||(i.name||'').toLowerCase().includes(q)||(i.sku||'').toLowerCase().includes(q)
        );
    },
    formatCurrency(n){return new Intl.NumberFormat('id-ID',{style:'currency',currency:'IDR',minimumFractionDigits:0}).format(n||0);},
    fmtQty(n){return Number(n||0).toLocaleString('id-ID',{maximumFractionDigits:2});},
};}
</script>
{% endblock %}