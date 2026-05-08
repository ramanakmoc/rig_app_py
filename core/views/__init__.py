from .dashboard import dashboard
from .entries  import add_entry, edit_entry, delete_entry
from .reports  import report_daily, report_weekly, report_monthly, alerts
from .exports  import export_excel, export_pdf_daily, export_pdf_weekly, export_pdf_monthly
from .users    import user_list, create_user, delete_user, profile_view
from core.views.home import home


def get_accessible_rigs(request, all_rigs):
    """Return only rigs the current user can access."""
    try:
        return request.user.profile.filter_rigs(list(all_rigs))
    except Exception:
        return list(all_rigs)
