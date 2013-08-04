import os, sys
from gumby.plugin import pluginmgr
from gumby.config import Config
from gumby.utils import matches_dependency, update_dependency, init_repo, get_dependencies, POM_NS
import re
from fnmatch import fnmatch
from clize import clize, run
from slugify import slugify
from elementtree.ElementTree import ElementTree
from subprocess import call, Popen, PIPE

config = None
plugins = pluginmgr.get_plugins()

def update_plugin(project):
    project_path = os.path.join(config["staging_path"], slugify(project))
    project_path = os.path.expanduser(project_path)
    if not os.path.isdir(project_path):
        os.makedirs(project_path)
    repo = init_repo(project_path, config["plugins"][project]["git_url"])
    pom_path = os.path.join(project_path, "pom.xml")
    updated_files = []

    dependencies = get_dependencies(pom_path)
    chdeps = []

    pl = []

    for p in plugins:
        mask = '*'
        if hasattr(plugins[p], 'dep_mask'):
            mask=plugins[p].dep_mask
        else:
            plugins[p].dep_mask = "*"

        if matches_dependency(dependencies.keys(), mask):
            pl.append(plugins[p])

    for dep in dependencies.keys():
        update_dependency(config, pl, dep)
        if dep in config["dependencies"].keys():
            if config["dependencies"][dep]["version"] != dependencies[dep]:
                chdeps.append(dep)
                for p in pl:
                    for root, subfolders, files in os.walk(project_path):
                        for f in files:
                            file_path = os.path.join(root, f)
                            if fnmatch(dep, p.dep_mask):
                                if f.endswith('.java'):
                                    f = open(file_path, 'r')
                                    c = f.read()
                                    f.close()
                                    p.process_file(dep, config, file_path)
                                    f = open(file_path, 'r')
                                    n = f.read()
                                    f.close()

                                    if n.strip() != c.strip():
                                        updated_files.append(file_path)

                            if file_path.endswith("pom.xml"):
                                s = dep.rsplit(".", 1)
                                groupId = s[0]
                                artifactId = s[1]
                                doc = ElementTree(file=file_path)
                                deps = doc.findall('/{POM}dependencies/{POM}dependency'.format(POM=POM_NS))
                                for d in deps:
                                    if (d.find("{POM}groupId".format(POM=POM_NS)).text == groupId) and d.find("{POM}artifactId".format(POM=POM_NS)).text == artifactId:
                                        dependency = d
                                        break

                                re_dep = re.compile(r'(<dependency>\s+<groupId>{groupId}</groupId>\s+<artifactId>{artifactId}</artifactId>\s+<version>)([A-Za-z0-9.\-]+)(</version>)'.format(groupId=groupId, artifactId=artifactId),re.MULTILINE)

                                f = open(pom_path, 'r')
                                contents = f.read()
                                c = contents
                                f.close()

                                contents = re_dep.sub(r'\1{{replaceme}}\3', contents)
                                contents = contents.replace('{{replaceme}}', config["dependencies"][dep]["version"])

                                f = open(pom_path, 'w')
                                f.write(contents)
                                f.close()

                                if c.strip() != contents.strip():
                                    updated_files.append(file_path)

    message = []
    for change in chdeps:
        message.append("%s for version %s" % (config["dependencies"][change]["name"], dependencies[change]))

    cwd = os.getcwd()
    os.chdir(project_path)

    for f in updated_files:
        p = Popen(["git", "add", f])
        out, err = p.communicate()

    p = Popen(["git", "commit", "-m", "Update for: " + ", ".join(message)])
    out, err = p.communicate()
    p = Popen(["git", "push", "origin", "master"])
    out, err = p.communicate()
    os.chdir(cwd)


@clize
def update_plugins(*plugins):
    pl = []
    if len(plugins) > 0:
        for p in plugins:
            if p in config["plugins"]:
                pl.append(p)
    else:
        for p in config["plugins"]:
            pl.append(p)

    if len(pl) == 0:
        print "No plugins to update."
        return

    print "Updating plugins " + ", ".join(pl)

    for p in pl:
        update_plugin(p)

if __name__ == "__main__":
    config = Config()
    config.loadOrCreate()

    run((update_plugins,))

    config.save()

