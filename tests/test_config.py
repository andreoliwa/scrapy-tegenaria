# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name
"""Test configurations."""
from tegenaria.app import create_app
from tegenaria.settings import DevConfig, ProdConfig


def test_production_config():
    """Production."""
    app = create_app(ProdConfig)
    assert app.config['ENV'] == 'prod'
    assert app.config['DEBUG'] is False
    assert app.config['DEBUG_TB_ENABLED'] is False
    assert app.config['ASSETS_DEBUG'] is False


def test_dev_config():
    """Development."""
    app = create_app(DevConfig)
    assert app.config['ENV'] == 'dev'
    assert app.config['DEBUG'] is True
    assert app.config['ASSETS_DEBUG'] is True
