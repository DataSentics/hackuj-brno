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
            dumps=dumps,
        )

    @app.listener("before_server_start")
    async def before_server_start(app, loop):
       pass
   
    @app.listener("after_server_stop")
    async def after_server_stop(app, loop):
   
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

    app.add_task(supply_test_one_pdf_queue_loop)

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


def trigger(args):
    """
    Triggers action by sending message with RabbitMQ, saves to S3.
    """
    import logging
    import magic
    from datetime import datetime
    from ds_invoicereader_common.types import guid
    from ds_invoicereader_common.types.messaging import DocumentEnquedForExtraction
    from glob import glob

    logging.basicConfig()
    logger = logging.getLogger(f"{appName}-cli")
    logger.setLevel(logging.DEBUG)
    document_paths = glob(args.path + "/*")
    logger.info(f"{document_paths=} {args.repeats=}")

    async def _run():
        storage.client = FileStorage(
            settings.STORAGE_CONTAINER_NAME,
            settings.STORAGE_CONNECTION,
            logger=logger,
            secure=settings.STORAGE_SECURE,
        )

        rabbitmq.client = await RabbitMQClient.create(
            asyncio.get_running_loop(),
            settings.RABBITMQ_URI.get_secret_value(),
            f"{appName}-cli",
            logger=logger,
        )

        for _ in range(args.repeats):
            for document in document_paths:
                with open(document, "rb") as document_file:
                    doc_id = guid.generate()
                    doc_path = Path(
                        f"documents/{doc_id}/document{Path(document).suffix}"
                    )
                    doc_mime_type = magic.from_file(document, mime=True)
                    doc_url = await storage.client.save(
                        document_file.read(), doc_path, content_type=doc_mime_type
                    )

                await rabbitmq.client.send_event(
                    DocumentEnquedForExtraction(
                        id=doc_id,
                        created_at=datetime.now(),
                        file_name=doc_path.name,
                        file_path=doc_path,
                        file_url=doc_url,
                        mime_type=doc_mime_type,
                        status="enqueued-for-extraction",
                        queue_id="704eddab-98f3-4d96-a2f1-6932831a7228",
                        updated_at=datetime.now(),
                    )
                )

    asyncio.run(_run())


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

    # create parser for "trigger" command
    trigger_parser = subparsers.add_parser("trigger")
    trigger_parser.set_defaults(func=trigger)

    args = parser.parse_args()
    args.func(args)
