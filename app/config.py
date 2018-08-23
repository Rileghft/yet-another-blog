# -*- coding: utf-8 -*-

import simplejson as json


config = {}


def init(config_path):
    global config
    with open(config_path) as config_file:
        config = json.load(config_file, encoding='utf-8')
