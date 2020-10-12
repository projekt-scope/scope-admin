import logging

from flask import Flask
import coloredlogs
from scope_admin import ScopeAdmin

LOGGER = logging.getLogger("scope-admin")
# FORMAT_CONS = "%(asctime)s %(name)-12s %(pathname)s:%(lineno)d %(levelname)8s\t%(message)s"
FORMAT_CONS = "%(asctime)s %(name)-12s %(levelname)8s\t%(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)
logging.getLogger("urllib3.connectionpool").disabled = True
coloredlogs.install(level="DEBUG", fmt=FORMAT_CONS)


app = Flask("admin", static_url_path="")

LOGGER.info(
    """
░██████╗░█████╗░░█████╗░██████╗░███████╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝
╚█████╗░██║░░╚═╝██║░░██║██████╔╝█████╗░░
░╚═══██╗██║░░██╗██║░░██║██╔═══╝░██╔══╝░░
██████╔╝╚█████╔╝╚█████╔╝██║░░░░░███████╗
╚═════╝░░╚════╝░░╚════╝░╚═╝░░░░░╚══════╝
█                                       █
█  https://www.projekt-scope.de/        █
█             scope-admin               █
    """
)


SCOPE_ADMIN = ScopeAdmin()

from frontend import frontend_bp
from api import api_bp

app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

app.register_blueprint(frontend_bp)
app.register_blueprint(api_bp)


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host="0.0.0.0", port=1234, debug=True, threaded=True)
