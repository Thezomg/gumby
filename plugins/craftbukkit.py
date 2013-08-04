#!/usr/bin/env python

"""CraftBukkit Plugin"""

__author__ = "Deaygo"
__credits__ = ["Deaygo"]
__version__ = "0.1"
__maintainer__ = "Deaygo"
__email__ = "deaygo@thezomg.com"

from gumby.plugin import _Plugin
from elementtree.ElementTree import ElementTree
from gumby.utils import POM_NS
import re

class CBPlugin(_Plugin):
    name = "CraftBukkit Plugin"
    dep_mask = "org.bukkit.craftbukkit"

    def get_name(self):
        return self.name

    def process_file(self, dep, config, file_path):
        if file_path.endswith('.java') and dep == "org.bukkit.craftbukkit":
            f = open(file_path, 'r')

            nms_re = re.compile(r'(net\.minecraft\.server\.v)([A-Za-z0-9_]+)')
            cb_re = re.compile(r'(org\.bukkit\.craftbukkit\.v)([A-Za-z0-9_]+)')
            contents = f.read()
            f.close()

            contents = nms_re.sub(r'\1{{MINECRAFTVERSIONHERE}}', contents)
            contents = cb_re.sub(r'\1{{MINECRAFTVERSIONHERE}}', contents)
            contents = contents.replace('{{MINECRAFTVERSIONHERE}}', config["dependencies"][dep]["minecraft_version"])

            f = open(file_path, 'w')
            f.write(contents)
            f.close()

    def process_pom(self, config, pom_path):
        doc = ElementTree(file=pom_path)
        mc_version = ""
        try:
            mc_version = doc.findall('/{POM}properties/{POM}minecraft_version'.format(POM=POM_NS))[0].text
        except:
            mc_version = ""

        config["minecraft_version"] = mc_version