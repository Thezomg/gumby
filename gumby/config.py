import os, sys, yaml, copy

DEFAULT = {
    "plugins": {
        "NerdMessage": {
            "git_url": "git@github.com:NerdNu/NerdMessage.git"
        },
        "ModMode": {
            "git_url": "git@github.com:NerdNu/ModMode.git"
        }
    },
    "dependencies": {
        "org.bukkit.bukkit": {
            "name": "Bukkit",
            "git_url": "https://github.com/Bukkit/Bukkit.git"
        },
        "org.bukkit.craftbukkit": {
            "name": "CraftBukkit",
            "git_url": "https://github.com/Bukkit/CraftBukkit.git"
        }
    },
    "staging_path": "~/gumby_staging"
}

class Config(dict):
    def __init__(self, fn="config.yml", init={}):
        self.update(init)
        self.filename = fn

    def save(self):
        with open(self.filename, 'w') as f:
            yaml.dump(dict(**self), f, default_flow_style=False)

    def _load(self):
        with open(self.filename, 'r') as f:
            self.update(yaml.load(f))
    
    def _create(self):
        with open(self.filename, 'w') as f:
            yaml.dump(DEFAULT, f)

    def loadOrCreate(self):
        if os.path.exists(self.filename):
            self._load()
        else:
            self._create()
            print "config.yml saved, please configure and run again."
            sys.exit(1)