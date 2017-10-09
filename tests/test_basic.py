# -*- coding: utf-8 -*-
"""Basic tests."""
from tegenaria.app import create_app
from tegenaria.items import clean_number
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


def test_clean_number():
    """Number cleaning."""
    data = {
        '1,000.00': '1000',
        '1,000.00 EUR ': '1000',
        '1.000,00': '1000',
        'EUR 1.000,00 ': '1000',
        ' 644.28': '644.28',
        ' 644,28': '644.28',
        '1,644.28': '1644.28',
        '1644,28  ': '1644.28',
        '1.644,28': '1644.28',
        '1,000,000': '1000000',
        '2.123.000': '2123000',
        '1,000': '1000',
        '2.123': '2123',
        '103.88 m²': '103.88',
        '103,88 m²': '103.88',
        '3 rooms': '3',
        ' 2.0 room(s)': '2',
        ' 5.0': '5',
        ' 5.00 ': '5',
        ' 5.000 ': '5000',
        ' 5,000 ': '5000',
        '2,0': '2',
        ' 10,0 ': '10',
        '2,5': '2.5',
        '2.5': '2.5',
        '3,50': '3.50',
        '3.50': '3.50',
    }
    for input_value, expected_output in data.items():
        assert clean_number(input_value) == expected_output, 'In: {} Out: {}'.format(input_value, expected_output)
