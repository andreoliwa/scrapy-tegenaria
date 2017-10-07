# -*- coding: utf-8 -*-
"""Basic tests."""
from tegenaria.app import create_app
from tegenaria.items import sanitize_price
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


def test_sanitize_price():
    """Price cleaning."""
    assert sanitize_price('1,000.00') == '1000'
    assert sanitize_price('1,000.00 EUR ') == '1000'
    assert sanitize_price('1.000,00') == '1000'
    assert sanitize_price('EUR 1.000,00 ') == '1000'
    assert sanitize_price(' 644.28') == '644.28'
    assert sanitize_price(' 644,28') == '644.28'
    assert sanitize_price('1,644.28') == '1644.28'
    assert sanitize_price('1644,28  ') == '1644.28'
    assert sanitize_price('1.644,28') == '1644.28'

    assert sanitize_price('1,000,000') == '1000000'
    assert sanitize_price('2.123.000') == '2123000'
    assert sanitize_price('1,000') == '1000'
    assert sanitize_price('2.123') == '2123'
