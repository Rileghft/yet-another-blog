# -*- coding: utf-8 -*-

import simplejson as json


config = {}


def init(params):
    init_config(params['config_path'])


def init_config(config_path):
    global config
    with open(config_path) as config_file:
        config = json.load(config_file)
