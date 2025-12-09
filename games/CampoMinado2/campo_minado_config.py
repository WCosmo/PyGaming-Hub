import os, configparser, pygame

class ConfigLoader:
    DEFAULT_CONF = {
        'Display': {'width':'800','height':'600','fullscreen':'False'},
        'Controls': {'up':'w','down':'s','left':'a','right':'d','action_a':'space','action_b':'f','pause':'escape'}
    }

    @staticmethod
    def load(conf_path):
        config = configparser.ConfigParser()
        config.read_dict(ConfigLoader.DEFAULT_CONF)
        if os.path.exists(conf_path): config.read(conf_path)
        return config

    @staticmethod
    def map_key(name):
        if not name: return None
        try: return pygame.key.key_code(name)
        except: pass
        keyname = name.upper()
        if not keyname.startswith('K_'): keyname = 'K_' + keyname
        return getattr(pygame, keyname, None)
