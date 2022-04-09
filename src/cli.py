#!/usr/bin/env python
import os
import psutil
import asyncio
import argparse
import logging
import sentry_sdk
import sys
import platform
import tracemalloc

tracemalloc.start()


from distutils.util import strtobool
from sanic import Sanic
from sanic.log import logger
from sanic.response import json
from sentry_sdk.integrations.sanic import SanicIntegration

# import newrelic.agent

from app_classificator.config import settings
from app_classificator.api_handlers import api_v1
from app_classificator.model.classificator import init_classificator

from pathlib import Path  # for testing using trigger


__version__ = "1.0"
appName = "datasentics-invoicereader-baseservice"


def make_app():
    if not settings.DEBUG:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN.get_secret_value(),
            integrations=[SanicIntegration()],
        )

    app = Sanic(appName)
    app.config.update_config(settings.dict())
    return app


def memory_metrics():
    pid = os.getpid()
    p = psutil.Process(os.getpid())
    m = p.memory_info()

    yield ("Custom/Memory/Physical", float(m.rss) / (1024 * 1024))
    yield ("Custom/Memory/Virtual", float(m.vms) / (1024 * 1024))


# application = newrelic.agent.register_application()


def main():
    app = make_app()
    app.blueprint(api_v1)

    @app.route("/_/hc")
    async def healthcheck(request):
        # some internal values in config are not serializable, so filter them
        conf = {k: v for k, v in request.app.config.items() if not k.startswith("_")}
        return json(
            {
                "app_name": appName,
                "version": __version__,
                "python_version": sys.version,
                "platform": platform.platform(),
                "uname": platform.uname(),
                "config": conf,
            },
        )

    @app.listener("before_server_start")
    async def before_server_start(app, loop):
        init_classificator(settings.MODEL_PATH)

    @app.listener("after_server_stop")
    async def after_server_stop(app, loop):
        logging.info("Server stopping")
        
    if settings.DEBUG:
        try:
            # allowing cors for all domains and routes
            # SEE: https://github.com/ashleysommer/sanic-cors#simple-usage
            from sanic_cors import CORS

            app.config.CORS = "*"

        except Exception as e:
            logger.exception("Cant import some debug modules.")

    async def supply_test_one_pdf_queue_loop(app):

        while True:
            logger.debug("Logging mem")
            # newrelic.agent.record_custom_metrics(memory_metrics(), application)
            await asyncio.sleep(30)

    app.run(
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
        auto_reload=False,
    )
    return app


def run(args):
    main()

if __name__ == "__main__":
    # SEE: https://docs.python.org/3/library/argparse.html#sub-commands
    parser = argparse.ArgumentParser(
        description="Datasentics InvoiceReader BaseService"
    )
    subparsers = parser.add_subparsers()
    # create the parser for the "run" command
    run_parser = subparsers.add_parser("run", help="run application")
    run_parser.set_defaults(func=run)
    parser.set_defaults(func=run)

    args = parser.parse_args()
    args.func(args)
