import os
from config import ConfigLoader
from game import Game

if __name__ == '__main__':
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    conf_path = os.path.join(root, 'conf', 'conf.ini')
    config = ConfigLoader.load(conf_path)
    Game(config).run()
