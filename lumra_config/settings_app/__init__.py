# lumra_config/settings_app/views.py
# Auto-generated oleh lumra_fix.py
# Stub ini mengimpor ulang semua fungsi dari lumra_config.views
# sehingga urls.py bisa menggunakan path 'lumra_config.settings_app.views.fungsi_name'

from django.shortcuts import redirect

from lumra_config.views import (
    users_view,
    profile_view,
    settings_view,
    system_status_view,
    business_settings_view,
    business_form_general_view,
    business_feature_matrix_view,
    user_roles_permissions_view,
    about_view,
    contact_view,
    search_view,
    # New views
    users_list,
    user_list,
    roles,
    role_form,
    user_roles_permissions,
    permission_matrix,
    business_profile,
    business_settings,
    business_form_general,
    business_feature_matrix,
    system_status,
    email_settings,
    notification_settings,
    numbering_settings,
    backup_restore,
    api_keys,
    about,
    contact,
    search,
)


def user_form(request):
    return redirect("users_list")


__all__ = ['users_view', 'profile_view', 'settings_view', 'system_status_view', 'business_settings_view', 'business_form_general_view', 'business_feature_matrix_view', 'user_roles_permissions_view', 'about_view', 'contact_view', 'search_view', 'users_list', 'user_list', 'roles', 'role_form', 'user_roles_permissions', 'permission_matrix', 'business_profile', 'business_settings', 'business_form_general', 'business_feature_matrix', 'system_status', 'email_settings', 'notification_settings', 'numbering_settings', 'backup_restore', 'api_keys', 'about', 'contact', 'search', 'user_form']
