# 📊 Mapping Logic Lumra

> Dokumen otomatis: koneksi **Views** ↔ **Templates** ↔ **Database**

## 📈 Statistik

| Metrik | Jumlah |
|:---|:---|
| **Total Views** | 33 |
| FBV / CBV | 33 / 0 |
| Web / API | 26 / 7 |
| **Models** | 1 |
| **Templates** | 19 |
| **Forms** | 0 |

## 📋 Tabel Mapping Utama

| # | Path File | View | Type | URL | Template | Model/DB | Form | Methods | API? |
|:--:|:----------|:-----|:----:|:----|:---------|:---------|:-----|:-------|:----:|
| 1 | `lumra_config/settings_app/views.py` | `user_form` | FBV | - | - | - | - | `GET` |  |
| 2 | `lumra_config/views/api_views.py` | `_parse_json` | FBV | - | - | - | - | `POST` | 🌐 |
| 3 | `lumra_config/views/auth_views.py` | `login_view` | FBV | - | `lumra_pages/auth/login.html` | - | - | `POST` |  |
| 4 | `lumra_config/views/auth_views.py` | `logout_view` | FBV | - | - | - | - | `GET` |  |
| 5 | `lumra_config/views/dashboard_views.py` | `dashboard_view` | FBV | - | `lumra_pages/sales_insight/dashboard.html` | - | - | `GET` |  |
| 6 | `lumra_config/views/dashboard_views.py` | `notification_view` | FBV | - | `lumra_pages/messages/notification.html` | - | - | `GET` |  |
| 7 | `lumra_config/views/dashboard_views.py` | `api_dashboard_data` | FBV | - | - | - | - | `GET` | 🌐 |
| 8 | `lumra_config/views/dashboard_views.py` | `api_dashboard_chart_data` | FBV | - | - | - | - | `GET` | 🌐 |
| 9 | `lumra_config/views/inventory_views.py` | `products_import_template` | FBV | - | - | - | - | `GET` | 🌐 |
| 10 | `lumra_config/views/logistics_views.py` | `_parse_json_body` | FBV | - | - | - | - | `POST` | 🌐 |
| 11 | `lumra_config/views/marketing_views.py` | `campaign_list` | FBV | - | `lumra_pages/marketing/campaign_list.html` | - | - | `GET` |  |
| 12 | `lumra_config/views/masterdata_views.py` | `_wants_json` | FBV | - | - | - | - | `POST` |  |
| 13 | `lumra_config/views/master_data_extended_views.py` | `bank_accounts` | FBV | - | `lumra_pages/master_data/bank_accounts.html` | - | - | `GET` |  |
| 14 | `lumra_config/views/master_data_extended_views.py` | `bank_account_form` | FBV | - | `lumra_pages/master_data/bank_account_form.html` | - | - | `GET` |  |
| 15 | `lumra_config/views/master_data_extended_views.py` | `payment_terms_list` | FBV | - | `lumra_pages/master_data/payment_terms_list.html` | - | - | `GET` |  |
| 16 | `lumra_config/views/master_data_extended_views.py` | `payment_terms_form` | FBV | - | `lumra_pages/master_data/payment_terms_form.html` | - | - | `GET` |  |
| 17 | `lumra_config/views/messages_views.py` | `inbox` | FBV | `notifications/` | `lumra_pages/messages/inbox.html` | - | - | `GET` |  |
| 18 | `lumra_config/views/messages_views.py` | `message_detail` | FBV | - | `lumra_pages/messages/message_detail.html` | - | - | `GET` |  |
| 19 | `lumra_config/views/messages_views.py` | `compose_message` | FBV | - | `lumra_pages/messages/compose.html` | - | - | `GET` |  |
| 20 | `lumra_config/views/messages_views.py` | `notification_center` | FBV | - | `lumra_pages/messages/notification.html` | - | - | `GET` |  |
| 21 | `lumra_config/views/messages_views.py` | `broadcast_message` | FBV | - | `lumra_pages/messages/broadcast.html` | - | - | `GET` |  |
| 22 | `lumra_config/views/messages_views.py` | `message_templates` | FBV | - | `lumra_pages/messages/message_templates.html` | - | - | `GET` |  |
| 23 | `lumra_config/views/onboarding_views.py` | `onboarding_welcome` | FBV | - | `lumra_pages/onboarding/welcome.html` | - | - | `GET` |  |
| 24 | `lumra_config/views/onboarding_views.py` | `onboarding_step_business` | FBV | - | `lumra_pages/onboarding/step_business.html` | - | - | `GET` |  |
| 25 | `lumra_config/views/onboarding_views.py` | `onboarding_step_location` | FBV | - | `lumra_pages/onboarding/step_location.html` | - | - | `GET` |  |
| 26 | `lumra_config/views/onboarding_views.py` | `onboarding_step_category` | FBV | - | `lumra_pages/onboarding/step_category.html` | - | - | `GET` |  |
| 27 | `lumra_config/views/onboarding_views.py` | `onboarding_step_complete` | FBV | - | `lumra_pages/onboarding/step_complete.html` | - | - | `GET` |  |
| 28 | `lumra_config/views/onboarding_views.py` | `onboarding_save_step` | FBV | - | - | - | - | `POST` | 🌐 |
| 29 | `lumra_config/views/production_ops_views.py` | `_parse_json_body` | FBV | - | - | - | - | `POST` | 🌐 |
| 30 | `lumra_config/views/production_ops_views.py` | `_load_rnd_records` | FBV | - | - | - | - | `GET` |  |
| 31 | `lumra_config/views/production_ops_views.py` | `_save_rnd_records` | FBV | - | - | - | - | `GET` |  |
| 32 | `lumra_config/views/production_ops_views.py` | `bom_list` | FBV | - | `lumra_pages/production/bom_list.html` | **b** | - | `GET` |  |
| 33 | `lumra_config/views/settings_views.py` | `_business_context` | FBV | - | - | - | - | `GET` |  |

---

## 📁 Detail Per File

### 📄 `lumra_config/settings_app/views.py`

#### `user_form` — L43 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Redirects** | `users_list` |

### 📄 `lumra_config/views/api_views.py`

#### `_parse_json` — L31 — 🌐 API

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `POST` |

### 📄 `lumra_config/views/auth_views.py`

#### `login_view` — L16 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `POST` |
| **Templates** | `lumra_pages/auth/login.html` |
| **Redirects** | `dashboard` |

#### `logout_view` — L44 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Redirects** | `login` |

### 📄 `lumra_config/views/dashboard_views.py`

#### `dashboard_view` — L425 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/sales_insight/dashboard.html` |

#### `notification_view` — L468 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/messages/notification.html` |

#### `api_dashboard_data` — L501 — 🌐 API

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |

#### `api_dashboard_chart_data` — L523 — 🌐 API

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |

### 📄 `lumra_config/views/inventory_views.py`

#### `products_import_template` — L83 — 🌐 API

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required`, `require_GET` |

### 📄 `lumra_config/views/logistics_views.py`

#### `_parse_json_body` — L27 — 🌐 API

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `POST` |

### 📄 `lumra_config/views/marketing_views.py`

#### `campaign_list` — L46 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/marketing/campaign_list.html` |

### 📄 `lumra_config/views/master_data_extended_views.py`

#### `bank_accounts` — L33 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/master_data/bank_accounts.html` |

#### `bank_account_form` — L43 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/master_data/bank_account_form.html` |

#### `payment_terms_list` — L52 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/master_data/payment_terms_list.html` |

#### `payment_terms_form` — L62 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/master_data/payment_terms_form.html` |

### 📄 `lumra_config/views/masterdata_views.py`

#### `_wants_json` — L22 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `POST` |

### 📄 `lumra_config/views/messages_views.py`

#### `inbox` — L17 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **URL** | `notifications/` |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/messages/inbox.html` |

#### `message_detail` — L26 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/messages/message_detail.html` |

#### `compose_message` — L35 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/messages/compose.html` |

#### `notification_center` — L44 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/messages/notification.html` |

#### `broadcast_message` — L53 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/messages/broadcast.html` |

#### `message_templates` — L62 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/messages/message_templates.html` |

### 📄 `lumra_config/views/onboarding_views.py`

#### `onboarding_welcome` — L15 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/onboarding/welcome.html` |

#### `onboarding_step_business` — L22 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/onboarding/step_business.html` |

#### `onboarding_step_location` — L29 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/onboarding/step_location.html` |

#### `onboarding_step_category` — L36 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/onboarding/step_category.html` |

#### `onboarding_step_complete` — L43 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/onboarding/step_complete.html` |

#### `onboarding_save_step` — L51 — 🌐 API

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `POST` |
| **Decorators** | `login_required`, `require_POST` |

### 📄 `lumra_config/views/production_ops_views.py`

#### `_parse_json_body` — L28 — 🌐 API

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `POST` |

#### `_load_rnd_records` — L130 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |

#### `_save_rnd_records` — L138 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |

#### `bom_list` — L152 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |
| **Decorators** | `login_required` |
| **Templates** | `lumra_pages/production/bom_list.html` |
| **Models** | **b** |

### 📄 `lumra_config/views/settings_views.py`

#### `_business_context` — L237 — 🕸️ Web

| Property | Value |
|:---------|:------|
| **Type** | FBV |
| **Methods** | `GET` |

---

## 🗄️ Penggunaan Models

| Model | Views |
|:------|:------|
| **b** | `bom_list` |

---

## 📝 Penggunaan Templates

| Template | Views |
|:---------|:------|
| `lumra_pages/auth/login.html` | `login_view` |
| `lumra_pages/marketing/campaign_list.html` | `campaign_list` |
| `lumra_pages/master_data/bank_account_form.html` | `bank_account_form` |
| `lumra_pages/master_data/bank_accounts.html` | `bank_accounts` |
| `lumra_pages/master_data/payment_terms_form.html` | `payment_terms_form` |
| `lumra_pages/master_data/payment_terms_list.html` | `payment_terms_list` |
| `lumra_pages/messages/broadcast.html` | `broadcast_message` |
| `lumra_pages/messages/compose.html` | `compose_message` |
| `lumra_pages/messages/inbox.html` | `inbox` |
| `lumra_pages/messages/message_detail.html` | `message_detail` |
| `lumra_pages/messages/message_templates.html` | `message_templates` |
| `lumra_pages/messages/notification.html` | `notification_view`, `notification_center` |
| `lumra_pages/onboarding/step_business.html` | `onboarding_step_business` |
| `lumra_pages/onboarding/step_category.html` | `onboarding_step_category` |
| `lumra_pages/onboarding/step_complete.html` | `onboarding_step_complete` |
| `lumra_pages/onboarding/step_location.html` | `onboarding_step_location` |
| `lumra_pages/onboarding/welcome.html` | `onboarding_welcome` |
| `lumra_pages/production/bom_list.html` | `bom_list` |
| `lumra_pages/sales_insight/dashboard.html` | `dashboard_view` |

---

## 🌐 API Endpoints

| # | Endpoint | Path File | View | Methods | Models |
|:--:|:---------|:----------|:-----|:--------|:-------|
| 1 | `?` | `lumra_config/views/api_views.py` | `_parse_json` | `POST` | - |
| 2 | `?` | `lumra_config/views/dashboard_views.py` | `api_dashboard_data` | `GET` | - |
| 3 | `?` | `lumra_config/views/dashboard_views.py` | `api_dashboard_chart_data` | `GET` | - |
| 4 | `?` | `lumra_config/views/inventory_views.py` | `products_import_template` | `GET` | - |
| 5 | `?` | `lumra_config/views/logistics_views.py` | `_parse_json_body` | `POST` | - |
| 6 | `?` | `lumra_config/views/onboarding_views.py` | `onboarding_save_step` | `POST` | - |
| 7 | `?` | `lumra_config/views/production_ops_views.py` | `_parse_json_body` | `POST` | - |

---

## ⚠️ Potensi Masalah

### Views Tanpa URL Pattern

- `user_form` — `lumra_config/settings_app/views.py`
- `_parse_json` — `lumra_config/views/api_views.py`
- `login_view` — `lumra_config/views/auth_views.py`
- `logout_view` — `lumra_config/views/auth_views.py`
- `dashboard_view` — `lumra_config/views/dashboard_views.py`
- `notification_view` — `lumra_config/views/dashboard_views.py`
- `api_dashboard_data` — `lumra_config/views/dashboard_views.py`
- `api_dashboard_chart_data` — `lumra_config/views/dashboard_views.py`
- `products_import_template` — `lumra_config/views/inventory_views.py`
- `_parse_json_body` — `lumra_config/views/logistics_views.py`
- `campaign_list` — `lumra_config/views/marketing_views.py`
- `_wants_json` — `lumra_config/views/masterdata_views.py`
- `bank_accounts` — `lumra_config/views/master_data_extended_views.py`
- `bank_account_form` — `lumra_config/views/master_data_extended_views.py`
- `payment_terms_list` — `lumra_config/views/master_data_extended_views.py`
- `payment_terms_form` — `lumra_config/views/master_data_extended_views.py`
- `message_detail` — `lumra_config/views/messages_views.py`
- `compose_message` — `lumra_config/views/messages_views.py`
- `notification_center` — `lumra_config/views/messages_views.py`
- `broadcast_message` — `lumra_config/views/messages_views.py`
- `message_templates` — `lumra_config/views/messages_views.py`
- `onboarding_welcome` — `lumra_config/views/onboarding_views.py`
- `onboarding_step_business` — `lumra_config/views/onboarding_views.py`
- `onboarding_step_location` — `lumra_config/views/onboarding_views.py`
- `onboarding_step_category` — `lumra_config/views/onboarding_views.py`
- `onboarding_step_complete` — `lumra_config/views/onboarding_views.py`
- `onboarding_save_step` — `lumra_config/views/onboarding_views.py`
- `_parse_json_body` — `lumra_config/views/production_ops_views.py`
- `_load_rnd_records` — `lumra_config/views/production_ops_views.py`
- `_save_rnd_records` — `lumra_config/views/production_ops_views.py`
- `bom_list` — `lumra_config/views/production_ops_views.py`
- `_business_context` — `lumra_config/views/settings_views.py`

### Web Views Tanpa Template

- `_wants_json` — `lumra_config/views/masterdata_views.py`
- `_load_rnd_records` — `lumra_config/views/production_ops_views.py`
- `_save_rnd_records` — `lumra_config/views/production_ops_views.py`
- `_business_context` — `lumra_config/views/settings_views.py`

