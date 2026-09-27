"""
Sidebar module registry for the portal dashboard.

To add a new module later (e.g. the planned document approval workflows),
add one dict to MODULES below with a `visible_to(user)` check. Nothing else
needs to change — the sidebar template just loops over whatever this
context processor returns.
"""


def _is_staff(user):
    return hasattr(user, "staff_profile")


def _is_admin_staff(user):
    return _is_staff(user) and user.staff_profile.role == "admin"


MODULES = [
    {
        "name": "Dashboard",
        "icon": "speedometer2",
        "url_name": "portal:staff_dashboard",
        "visible_to": _is_staff,
    },
    {
        "name": "Shipments",
        "icon": "box-seam",
        "url_name": "portal:shipment_list",
        "visible_to": lambda user: True,  # every logged-in user (client or staff)
    },
    {
        "name": "New Shipment",
        "icon": "plus-circle",
        "url_name": "portal:shipment_create",
        "visible_to": _is_staff,
    },
    {
        "name": "Clients",
        "icon": "people",
        "url_name": "portal:client_list",
        "visible_to": _is_staff,
    },
    {
        "name": "Staff Accounts",
        "icon": "person-badge",
        "url_name": "portal:staff_list",
        "visible_to": _is_admin_staff,
    },
    {
        "name": "Document Workflows",
        "icon": "file-earmark-check",
        "url_name": None,  # not built yet
        "badge": "Coming soon",
        "visible_to": _is_staff,
    },
]


def sidebar_modules(request):
    """Injects `sidebar_modules` into every template's context."""
    user = request.user
    if not user.is_authenticated:
        return {}
    modules = [m for m in MODULES if m["visible_to"](user)]
    return {"sidebar_modules": modules}
