import os
import pytest
import requests
from datetime import datetime
from operator import itemgetter
from docstring_parser import parse
from app.main import get_application
from app.models.model_base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Any, Generator
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.db.base import get_db
from fastapi_sqlalchemy import DBSessionMiddleware
from dotenv import load_dotenv

load_dotenv(verbose=True)

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', '/tests')
connect_args = {}
if SQLALCHEMY_DATABASE_URL[:6] == 'sqlite':
    connect_args['check_same_thread'] = False
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, 'test_outcome', rep)


def pytest_addoption(parser):
    parser.addoption('--submit-tests',
                     action='store_true',
                     help='Submit tests to Jira')


class JiraTestService:
    def __init__(self, jira_settings):
        self.project_key = jira_settings['project_key']
        self.auth_string = (jira_settings['user'], jira_settings['password'])
        self.url = jira_settings['url'] + '/rest/atm/1.0'
        self.issue_url = jira_settings['url'] + '/rest/api/latest/issue'

    def get_issue_info(self, issue_key):
        return requests.get(
            url=self.issue_url + '/' + issue_key,
            auth=self.auth_string
        ).json()

    def get_tests_in_issue(self, issue_key):
        params = {
            'query':
            'projectKey = "%s" AND issueKeys IN (%s)' %
            (self.project_key, issue_key)
        }
        response = requests.get(url=self.url + '/testcase/search',
                                params=params,
                                auth=self.auth_string).json()
        return list(map(itemgetter('name', 'key'), response))

    def create_test(self, test_name, issue_key, objective, steps):
        json = {
            'name': test_name,
            'projectKey': self.project_key,
            'issueLinks': [issue_key],
            'status': 'Approved',
            'objective': objective,
            "testScript": {
                'type': 'PLAIN_TEXT',
                'text': steps or "Default"
            }
        }
        response = requests.post(url=self.url + '/testcase',
                                 json=json,
                                 auth=self.auth_string)
        if response.status_code != 201:
            raise Exception('Create test return with error status code',
                            response.status_code)

        test_key = response.json()['key']
        return test_key

    def delete_test(self, test_key):
        response = requests.delete(url=self.url + '/testcase/' + test_key,
                                   auth=self.auth_string)
        if response.status_code != 204:
            raise Exception('Delete test return with error status code',
                            response.status_code)

    def create_test_cycle(self, name, issue_key, items):
        def get_current_time():
            return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        json = {
            'name': name,
            'projectKey': self.project_key,
            'issueKey': issue_key,
            'plannedStartDate': get_current_time(),
            'plannedEndDate': get_current_time(),
            'items': items
        }
        response = requests.post(url=self.url + '/testrun',
                                 json=json,
                                 auth=self.auth_string)
        if response.status_code != 201:
            raise Exception('Create test cycle return with error status code',
                            response.status_code)


def jira_test_service():
    return JiraTestService({
        'url': os.getenv('JIRA_URL', '/tests'),
        'user': os.getenv('JIRA_USER', '/tests'),
        'password': os.getenv('JIRA_PASSWORD', '/tests'),
        'project_key': os.getenv('JIRA_PROJECT_KEY', '/tests')
    })


delete_tests_on_issue = set()


@pytest.fixture(scope='class')
def each_test_suite(request):
    # Before each test suite
    cls = request.cls
    cls.results = {}
    cls.tests_list = []

    test_service = jira_test_service()  # Currently only support Jira

    submit_tests = request.config.getoption('--submit-tests', default=False)
    if not getattr(cls, 'ISSUE_KEY', None):
        submit_tests = False
    if submit_tests:
        issue_info = test_service.get_issue_info(cls.ISSUE_KEY)
        if issue_info['fields']['status']['name'] == 'Closed':
            submit_tests = False

    if submit_tests:
        cls.tests_list = test_service.get_tests_in_issue(cls.ISSUE_KEY)

        if cls.ISSUE_KEY not in delete_tests_on_issue:
            for _, test_key in cls.tests_list:
                test_service.delete_test(test_key)
            delete_tests_on_issue.add(cls.ISSUE_KEY)

    yield

    # After each test suite
    if submit_tests:
        # Create test keys
        for name in cls.results:
            test_key = test_service.create_test(
                cls.__name__ + '_' + name,
                cls.ISSUE_KEY,
                cls.results[name]['objective'],
                cls.results[name]['steps']
            )
            cls.results[name]['testCaseKey'] = test_key
        test_cycle_items = []

        for k, v in cls.results.items():
            del v['objective']
            del v['steps']
            test_cycle_items.append(v)

        # Create test cycle
        test_service.create_test_cycle(
            cls.ISSUE_KEY + ' - ' + cls.__name__,
            cls.ISSUE_KEY,
            test_cycle_items
        )


@pytest.fixture()
def each_test_case(request):
    # Before each test case
    MAX_NAME_LENGTH = 255
    name = request._pyfuncitem.name
    if len(name) > MAX_NAME_LENGTH:
        name = name.substring(0, MAX_NAME_LENGTH)
    request.cls.results[name] = {'status': 'Pass'}
    yield

    # After each test case
    if request.node.test_outcome.failed:
        request.cls.results[name]['status'] = 'Fail'

    docstring = parse(request._pyfuncitem._obj.__doc__)

    step_string = 'Step by step:'
    if docstring.long_description and step_string in docstring.long_description:
        objective, steps = map(
            str.strip, docstring.long_description.split(step_string, 1))
        steps = '<pre>' + steps + '</pre>'
    else:
        objective = docstring.long_description
        steps = None

    request.cls.results[name]['objective'] = objective
    request.cls.results[name]['steps'] = steps


@pytest.fixture(autouse=True)
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(engine)  # Create the tables.
    _app = get_application()
    _app.add_middleware(DBSessionMiddleware, db_url=SQLALCHEMY_DATABASE_URL)
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(app: FastAPI) -> Generator[TestingSessionLocal, Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """

    # connect to the database
    connection = engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    session = TestingSessionLocal(bind=connection)
    yield session  # use the session in tests.
    session.close()
    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    transaction.rollback()
    # return connection to the Engine
    connection.close()


@pytest.fixture()
def client(app: FastAPI, db_session: TestingSessionLocal) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture
def app_class(request, app):
    if request.cls is not None:
        request.cls.app = app


# For Jira Test
@pytest.mark.usefixtures('each_test_case', 'each_test_suite')
class Jira:
    pass
