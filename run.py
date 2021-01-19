#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os
import argparse
import logging
from flask import Flask

from stacosys.conf.config import Config, ConfigParameter
from stacosys.core import database
from stacosys.core.rss import Rss
from stacosys.core.mailer import Mailer
from stacosys.interface import app
from stacosys.interface import api
from stacosys.interface import form
from stacosys.interface import scheduler


# configure logging
def configure_logging(level):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter
    formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    root_logger.addHandler(ch)


def stacosys_server(config_pathname):

    conf = Config.load(config_pathname)

    # configure logging
    logger = logging.getLogger(__name__)
    configure_logging(logging.INFO)
    logging.getLogger("werkzeug").level = logging.WARNING
    logging.getLogger("apscheduler.executors").level = logging.WARNING

    # initialize database
    db = database.Database()
    db.setup(conf.get(ConfigParameter.DB_URL))

    logger.info("Start Stacosys application")

    # generate RSS for all sites
    rss = Rss(
        conf.get(ConfigParameter.LANG),
        conf.get(ConfigParameter.RSS_FILE),
        conf.get(ConfigParameter.RSS_PROTO),
        conf.get(ConfigParameter.SITE_NAME),
        conf.get(ConfigParameter.SITE_URL)
    )
    rss.generate()

    # configure mailer
    mailer = Mailer(
        conf.get(ConfigParameter.IMAP_HOST),
        conf.get_int(ConfigParameter.IMAP_PORT),
        conf.get_bool(ConfigParameter.IMAP_SSL),
        conf.get(ConfigParameter.IMAP_LOGIN),
        conf.get(ConfigParameter.IMAP_PASSWORD),
        conf.get(ConfigParameter.SMTP_HOST),
        conf.get_int(ConfigParameter.SMTP_PORT),
        conf.get_bool(ConfigParameter.SMTP_STARTTLS),
        conf.get(ConfigParameter.SMTP_LOGIN),
        conf.get(ConfigParameter.SMTP_PASSWORD),
    )

    # configure scheduler
    scheduler.configure(
        conf.get_int(ConfigParameter.IMAP_POLLING),
        conf.get_int(ConfigParameter.COMMENT_POLLING),
        conf.get(ConfigParameter.LANG),
        conf.get(ConfigParameter.SITE_NAME),
        conf.get(ConfigParameter.SITE_TOKEN),
        conf.get(ConfigParameter.SITE_ADMIN_EMAIL),
        mailer,
        rss,
    )

    # inject config parameters into flask
    app.config.update(SITE_TOKEN=conf.get(ConfigParameter.SITE_TOKEN))

    # start Flask
    app.run(
        host=conf.get(ConfigParameter.HTTP_HOST),
        port=conf.get(ConfigParameter.HTTP_PORT),
        debug=False,
        use_reloader=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="config path name")
    args = parser.parse_args()
    stacosys_server(args.config)