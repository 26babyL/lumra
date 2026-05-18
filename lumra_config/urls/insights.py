from django.urls import path
from lumra_config.views.reports_views import (
    financial_reports_view,
    market_insights_view,
    trends_analysis_view,
    activity_log_view,
    download_report_view,
    export_trends_view,
)

urlpatterns = [
    path("financial/", financial_reports_view, name="financial_reports"),
    path("market/", market_insights_view, name="market_insights"),
    path("trends/", trends_analysis_view, name="trends_analysis"),
    path("activity/", activity_log_view, name="activity_log"),
    path("download-report/<str:report_type>/", download_report_view, name="download_report"),
    path("export-trends/<str:trend_type>/", export_trends_view, name="export_trends"),
]