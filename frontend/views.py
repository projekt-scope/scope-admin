import os
import logging
from flask import render_template
from frontend import frontend_bp as bp
from runserver import SCOPE_ADMIN as admin

# service_tags = admin.registered_internal_service_tags
ext_services = admin.external_service_infos


LOGGER = logging.getLogger("scope-admin")


@bp.route("/")
@bp.route("/index")
def index():
    """index route

    Returns:
        html: page / dashboard of scope-admin
    """
    # try:
    service_tags = admin.registered_internal_service_tags

    status = admin.check_status_of_services()

    return render_template(
        "index.html",
        service_tags=service_tags,
        status=status,
        ext_services=ext_services,
    )
    # except Exception as e:
    #     return f"No Docker Client found. Start your Docker Client! {e}"


@bp.route("/service/<tag>")
def service(tag):
    """service route

    Args:
        tag (str): tag of service

    Returns:
        html: page of service, show information, config file, status, logs, etc
    """
    config = ""
    service_tags = admin.registered_internal_service_tags
    try:
        service_instance = admin.get_service_with_tag(tag)
        config = service_instance.config
        if not service_instance.container:
            LOGGER.warning(f"Currently no container for {tag}.")
            status = "no container"
            logs = ""
            if not config:
                config = ""
        status = service_instance.running
        try:
            logs = service_instance.logs.decode("UTF 8")
        except Exception as e:
            LOGGER.warning(f"Currently no logs for {tag}. {e}")
            logs = ""
    except Exception as e:
        LOGGER.warning(f"Currently no container for {tag}. {e}")
        status = "no container"
        logs = ""
        if not config:
            config = ""

    return render_template(
        "service.html",
        service_tags=service_tags,
        tag=tag,
        config=config,
        logs=logs,
        status=status,
        ext_services=ext_services,
    )


@bp.route("/webinterface/<tag>")
def webinterface(tag):
    """webinterface route

    Args:
        tag (str): tag of service

    Returns:
        html: page of webinterface of service inside a iframe
    """
    service_tags = admin.registered_internal_service_tags
    service_instance = admin.get_service_with_tag(tag)
    start = service_instance.config["start-page"]
    if os.environ["MODE"] == "PRODUCTION":
        domain = "https://" + os.environ["DOMAIN"]
    else:
        domain = "http://localhost"

    return render_template(
        "webinterface.html",
        service_tags=service_tags,
        domain=domain,
        tag=tag,
        start=start,
        ext_services=ext_services,
    )


@bp.route("/service_external/<tag>")
def service_external(tag):
    """service_external route

    Args:
        tag (str): tag of service

    Returns:
        html: page of external service
    """
    service_tags = admin.registered_internal_service_tags

    return render_template(
        "service-external.html",
        service_tags=service_tags,
        tag=tag,
        ext_services=ext_services,
    )


@bp.route("/registration")
def registration():
    """registration route

    Returns:
        html: page for registration of a new service
    """
    service_tags = admin.registered_internal_service_tags

    return render_template(
        "service-registration.html",
        service_tags=service_tags,
        ext_services=ext_services,
    )
