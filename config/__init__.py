#!/usr/bin/env python

import sys, os, json, copy
from pythonutils.odict import OrderedDict

class Config():
        
    def __init__(self):
        self.config = OrderedDict()
        
    def add_category(self, category):
        if not self.config.has_key(category):
            self.config[category] = OrderedDict()
            
    def add_setting(self, category, setting, value, about='', type=0, stub=False, **kwargs):
        assert category!=None, 'Must specify a category'
        assert setting!=None, 'Must specify a setting'
        assert value!=None, 'Must specify a value'
        self.add_category(category)
        if not self.config[category].has_key(setting):
            self.config[category][setting] = OrderedDict()
        self.config[category][setting]['value'] = value
        if not stub:
            self.config[category][setting]['about'] = about
            self.config[category][setting]['type'] = type
            for k in kwargs:
                self.config[category][setting][k] = kwargs[k]
        
    def get_setting(self, category, setting, complete=False):
        assert category!=None, 'Must specify a category'
        assert setting!=None, 'Must specify a setting'
        assert self.config.has_key(category), 'Category does not exist'
        assert self.config[category].has_key(setting), 'Setting in category does not exist'
        assert self.config[category][setting].has_key('value'), 'Setting in category has no value'
        if complete:
            return self.config[category][setting]
        else:
            return self.config[category][setting]['value']
        
    def update_setting_value(self, category, setting, value):
        assert category!=None, 'Must specify a category'
        assert setting!=None, 'Must specify a setting'
        assert value!=None, 'Must specify a value'
        if self.config.has_key(category):
            if self.config[category].has_key(setting):
                self.config[category][setting]['value'] = value
    
    def get_settings(self, category):
        assert category!=None, 'Must specify a category'
        assert self.config.has_key(category), 'Category does not exist'
        return self.config[category].keys()
    
    def get_categories(self):
        return self.config.keys()
        
    def update(self, json_config):
        config = json.loads(json_config)
        for c in config.keys():
            for s in config[c].keys():
                self.update_setting_value(c,s,config[c][s]['value'])
                
    def save_config(config_file):
        with open(config_file, 'w+') as f:
            json.dump(self.config, f, separators=(',',': '), indent=4, sort_keys=True)
                            
"""                            
os.path.join(get_config_home(),'config')
        if os.path.isfile(config_file):
            with open(config_file, 'r') as f:
                s = f.read()
                
def diff_config(config):
    defC = Config(load=False)
    if json.dumps(defC.config) == json.dumps(config.config):
        return False
    defC = Config()
    if json.dumps(defC.config) != json.dumps(config.config):
        defC = Config(load=False)
        newC = Config(defaults=False, load=False)
        for c in config.config.keys():
            for s in config.config[c].keys():
                if config.config[c][s]['value'] != defC.config[c][s]['value']:
                    newC.add_setting(c, s, config.config[c][s]['value'], stub=True)    
        return newC.config
    else:
        return None
                

        
def delete_config():
    config_file = os.path.join(get_config_home(),'config')
    if os.path.isfile(config_file):
        os.remove(config_file)

def gen_config():
    config = Config()
    save_config(config.config)
"""