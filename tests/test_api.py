#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import logging

import pytest

from stacosys.db import database, dao
from stacosys.interface import api
from stacosys.interface import app


def init_test_db():
    c1 = dao.create_comment("/site1", "Bob", "/bob.site", "", "comment 1")
    c2 = dao.create_comment("/site2", "Bill", "/bill.site", "", "comment 2")
    c3 = dao.create_comment("/site3", "Jack", "/jack.site", "", "comment 3")
    dao.publish_comment(c1)
    dao.publish_comment(c3)


@pytest.fixture
def client():
    logger = logging.getLogger(__name__)
    db = database.Database()
    db.setup(":memory:")
    init_test_db()
    app.config.update(SITE_TOKEN="ETC")
    logger.info(f"start interface {api}")
    return app.test_client()


def test_api_ping(client):
    resp = client.get('/ping')
    assert resp.data == b"OK"


def test_api_count_global(client):
    resp = client.get('/comments/count')
    d = json.loads(resp.data)
    assert d and d['count'] == 2


def test_api_count_url(client):
    resp = client.get('/comments/count?url=/site1')
    d = json.loads(resp.data)
    assert d and d['count'] == 1
    resp = client.get('/comments/count?url=/site2')
    d = json.loads(resp.data)
    assert d and d['count'] == 0


def test_api_comment(client):
    resp = client.get('/comments?url=/site1')
    d = json.loads(resp.data)
    assert d and len(d['data']) == 1
    comment = d['data'][0]
    assert comment['author'] == 'Bob'
    assert comment['content'] == 'comment 1'


def test_api_comment_not_found(client):
    resp = client.get('/comments?url=/site2')
    d = json.loads(resp.data)
    assert d and d['data'] == []