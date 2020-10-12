import os
import json
import logging
from flask_restx import Resource, Api, fields
from flask import request, Response, make_response, jsonify
from git import Repo, exc
from api import api_bp

# from runserver import app

from runserver import SCOPE_ADMIN as admin

LOGGER = logging.getLogger("scope-admin")


# service_tags = admin.registered_internal_service_tags
# ext_services = admin.external_service_infos

api = Api(
    app=api_bp,
    version="0.1",
    title="scope-admin",
    description="This api helps controlling scope-services via the admin interface",
)

namespace_api = api.namespace("api", description="scope-admin")

model_service = api.model(
    "model_service",
    {
        "tag": fields.String(required=True, description="Tag of service"),
        "function": fields.String(required=True, description="Function"),
    },
)


@namespace_api.route("/service")
class Service(Resource):
    """Service
    """

    @api.expect(model_service)
    @api.doc(
        responses={
            200: "OK",
            400: "Invalid Argument",
            500: "Server Error",
            501: "Not implemended.",
        }
    )
    def post(self):
        """post route

        Returns:
            Response: Statuscode and response text
        """
        body = request.json
        service_instance = admin.get_service_with_tag(body["tag"])
        function = body["function"]
        try:
            data = {"message": ""}
            if function == "restart":
                data["message"] = service_instance.restart()
            elif function == "stop":
                 data["message"] = service_instance.stop()
            elif function == "logs":
                 data["message"] = {"logs": service_instance.logs.decode("UTF 8")}
            elif function == "status":
                 data["message"] = service_instance.running
            elif function == "build":
                build, message = service_instance.build()
                if build:
                    if service_instance.run():
                         data["message"] = message
            elif function == "uninstall":
                service_instance.remove_container()
                service_instance.uninstall()
                data["message"] = "True"
        except Exception as e:
            LOGGER.error(e)
            return Response(response=str(e), status=500)
        try:
            return make_response(jsonify(data), 201)
        except NameError:
            return Response(response="Not implemended.", status=501)


@namespace_api.route("/service/config")
class ServiceConfig(Resource):
    """ServiceConfig
    """

    @api.doc(
        responses={
            200: "OK",
            400: "Invalid Argument",
            500: "Mapping Key Error",
        }
    )
    def post(self):
        """post route service config

        Returns:
            Response: Statuscode and response text
        """
        try:
            body = request.json
            service = admin.get_service_with_tag(body["tag"])
            config = json.loads(str(body["config"]))
            if service.change_config("environment", config):
                data = {"message": "Config updated!"}
                return make_response(jsonify(data), 201)
        except json.JSONDecodeError as e:
            return Response(response=f"Config not updated! {e}", status=500)


@namespace_api.route("/service/port")
class ServicePort(Resource):
    """ServicePort
    """

    @api.doc(
        responses={
            200: "OK",
            400: "Invalid Argument",
            500: "Mapping Key Error",
        }
    )
    def post(self):
        """post route service port

        Returns:
            Response: Statuscode and response text
        """
        body = request.json
        service = admin.get_service_with_tag(body["tag"])
        port = body["port"]
        if service.change_config("ports", port):
            data = {"message": "Port updated!"}
            return make_response(jsonify(data), 201)
        return Response(response=f"Port not updated!", status=500)


@namespace_api.route("/service/register")
class RegisterService(Resource):
    """RegisterService
    """

    @api.doc(
        responses={
            200: "OK",
            400: "Invalid Argument",
            500: "Mapping Key Error",
        }
    )
    def post(self):
        """post route register service

        Returns:
            Response: Statuscode and response text
        """
        body = request.json
        giturl = body["giturl"]
        folder = giturl.split("/")[-1].split(".git")[0]
        if not admin.check_if_services_is_already_registered(folder):
            try:
                path = os.path.join("services", folder)
                if os.path.exists(path):
                    raise Exception(
                        "Destination path "
                        + path
                        + " already exists and/or is not an empty directory"
                    )
                try:
                    Repo.clone_from(giturl, path)
                except exc.GitError as giterror:
                    return Response(
                        response=f"Register or clone failed: {str(giterror)}",
                        status=500,
                    )
                config_path = os.path.join(path, "config.json")
                if os.path.exists(config_path):
                    with open(config_path) as config_file:
                        config = json.load(config_file)
                admin.register_service(folder, config["tag"])
            except Exception as e:
                return Response(
                    response=f"Register or clone failed: {str(e)}", status=500
                )
            data = {"message": "Registered service!"}
            return make_response(jsonify(data), 201)
        return Response(
            response=f"The service tag {folder} is already registred\
                in service_config.json. You need to deleted this first.",
            status=500,
        )
