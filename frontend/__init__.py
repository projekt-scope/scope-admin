from flask import Blueprint

frontend_bp = Blueprint(
    "frontend_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="",
)
from frontend import views
