
import tempfile

import pytest

from atlas.task.api.http import HTTPConnection
from atlas.task import FuncTask
from atlas import Scheduler, session
from atlas.conditions import IsParameter
from atlas.parameters import Private

from threading import Thread
import requests
import time, os, logging

from dateutil.tz import tzlocal

import pandas as pd


@pytest.fixture
def client(tmpdir):
    app = HTTPConnection().create_app()
    #db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    #orig_cwd = os.getcwd()
    #tmpdir.chdir()
    with tmpdir.as_cwd() as old_cwd:
        with app.test_client() as client:
            session.reset()
            #with app.app_context():
            #    myapp.init_db()
            yield client
    #os.chdir(orig_cwd)
    #os.close(db_fd)
    #os.unlink(flaskr.app.config['DATABASE'])
