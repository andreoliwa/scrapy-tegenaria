# -*- coding: utf-8 -*-
"""Click commands."""
import os
from glob import glob
from subprocess import call

import click
from flask import current_app
from flask.cli import with_appcontext
from plumbum import RETCODE, local
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings
from werkzeug.exceptions import MethodNotAllowed, NotFound

from tegenaria.generic import read_from_keyring
from tegenaria.models import Apartment
from tegenaria.settings import CRAWL_MINUTE_LIMIT, DISTANCE_MINUTE_LIMIT
from tegenaria.utils import PROJECT_NAME, DistanceCalculator, remove_inactive_apartments, reprocess_invalid_apartments

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
def test():
    """Run the tests and check spider contracts."""
    import pytest
    rv = pytest.main([TEST_PATH, '--verbose'])
    if rv:
        exit(rv)

    # Run scrapy check with a return code, in the foreground.
    scrapy = local['scrapy']
    rv = scrapy['check', '-v'] & RETCODE(FG=True)
    exit(rv)


@click.command()
@click.option('-f', '--fix-imports', default=False, is_flag=True,
              help='Fix imports using isort, before linting')
def lint(fix_imports):
    """Lint and check code style with flake8 and isort."""
    skip = ['node_modules', 'requirements']
    root_files = glob('*.py')
    root_directories = [
        name for name in next(os.walk('.'))[1] if not name.startswith('.')]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo('{}: {}'.format(description, ' '.join(command_line)))
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    if fix_imports:
        execute_tool('Fixing import order', 'isort', '-rc')
    execute_tool('Checking code style', 'flake8')


@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.

    Borrowed from Flask-Script, converted to use Click.
    """
    for dir_path, _dir_names, file_names in os.walk('.'):
        for filename in file_names:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dir_path, filename)
                click.echo('Removing {}'.format(full_pathname))
                os.remove(full_pathname)


@click.command()
@click.option('--url', default=None,
              help='Url to test (ex. /static/image.png)')
@click.option('--order', default='rule',
              help='Property on Rule to order by (default: rule)')
@with_appcontext
def urls(url, order):
    """Display all of the url matching routes for the project.

    Borrowed from Flask-Script, converted to use Click.
    """
    rows = []
    column_length = 0
    column_headers = ('Rule', 'Endpoint', 'Arguments')

    if url:
        try:
            rule, arguments = (
                current_app.url_map
                           .bind('localhost')
                           .match(url, return_rule=True))
            rows.append((rule.rule, rule.endpoint, arguments))
            column_length = 3
        except (NotFound, MethodNotAllowed) as e:
            rows.append(('<{}>'.format(e), None, None))
            column_length = 1
    else:
        rules = sorted(
            current_app.url_map.iter_rules(),
            key=lambda rule: getattr(rule, order))
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, None))
        column_length = 2

    str_template = ''
    table_width = 0

    if column_length >= 1:
        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4
        str_template += '{:' + str(max_rule_length) + '}'
        table_width += max_rule_length

    if column_length >= 2:
        max_endpoint_length = max(len(str(r[1])) for r in rows)
        # max_endpoint_length = max(rows, key=len)
        max_endpoint_length = (
            max_endpoint_length if max_endpoint_length > 8 else 8)
        str_template += '  {:' + str(max_endpoint_length) + '}'
        table_width += 2 + max_endpoint_length

    if column_length >= 3:
        max_arguments_length = max(len(str(r[2])) for r in rows)
        max_arguments_length = (
            max_arguments_length if max_arguments_length > 9 else 9)
        str_template += '  {:' + str(max_arguments_length) + '}'
        table_width += 2 + max_arguments_length

    click.echo(str_template.format(*column_headers[:column_length]))
    click.echo('-' * table_width)

    for row in rows:
        click.echo(str_template.format(*row[:column_length]))


@click.command()
@click.option('--cron', default=False, is_flag=True, help='Cron job: run only if no apartment was updated recently')
@with_appcontext
def distance(cron: bool):
    """Calculate distances."""
    if cron and Apartment.check_recently_updated(DISTANCE_MINUTE_LIMIT):
        return

    DistanceCalculator().calculate()


@click.command()
@with_appcontext
def vacuum():
    """Vacuum clean apartments: deactivate 404 pages, reprocess records with empty addresses."""
    remove_inactive_apartments()
    reprocess_invalid_apartments(read_from_keyring(PROJECT_NAME, 'json_dir', secret=False))


@click.command()
@click.option('--cron', default=False, is_flag=True, help='Cron job: run only if no apartment was updated recently')
@click.argument('spiders', nargs=-1)
@with_appcontext
def crawl(cron: bool, spiders):
    """Crawl the desired spiders.

    Type the name or part of the name of the spider.
    Multiple spiders can be provided.
    If none is given, all spiders will be crawled.
    """
    if cron and Apartment.check_recently_updated(CRAWL_MINUTE_LIMIT):
        return

    settings = get_project_settings()
    loader = SpiderLoader(settings)

    process = CrawlerProcess(settings)
    for spider_name in loader.list():
        if not spiders or any(part for part in spiders if part in spider_name):
            process.crawl(spider_name)

    # The script will block here until the crawling is finished
    process.start()
