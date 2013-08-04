import git
import os
from elementtree.ElementTree import ElementTree
from fnmatch import fnmatch
from slugify import slugify
from subprocess import call, Popen, PIPE

POM_NS = "{http://maven.apache.org/POM/4.0.0}"

updated_dependencies = []

def matches_dependency(deps, mask):
    for d in deps:
        if fnmatch(d, mask):
            return True
    return False

def init_repo(repo_path, git_url):
    p = Popen(["git", "clone", git_url, repo_path], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    cwd = os.getcwd()
    os.chdir(repo_path)
    p = Popen(["git", "pull", "origin", "master"], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    os.chdir(cwd)

def get_dependencies(path):
    dependencies = {}
    doc = ElementTree(file=path)
    deps = doc.findall('/%sdependencies' % POM_NS)
    for dep in deps[0]:
        groupId = dep.findall("%sgroupId" % POM_NS)[0].text
        artifactId = dep.findall("%sartifactId" % POM_NS)[0].text
        version = dep.findall("%sversion" % POM_NS)[0].text

        path = ".".join([groupId, artifactId])
        dependencies[path] = version

    return dependencies

def update_dependency(config, plugins, path, force=False):
    if path in updated_dependencies and not force:
        return

    if path in config["dependencies"]:
        git_url = config["dependencies"][path]["git_url"]

        dependency_path = os.path.join(config["staging_path"], slugify(unicode(path)))
        dependency_path = os.path.expanduser(dependency_path)
        if not os.path.isdir(dependency_path):
            os.makedirs(dependency_path)
        repo = init_repo(dependency_path, git_url)

        pom_path = os.path.join(dependency_path, 'pom.xml')

        doc = ElementTree(file=pom_path)
        version = doc.findall('/%sversion' % POM_NS)[0].text

        for p in plugins:
            p.process_pom(config["dependencies"][path], pom_path)

        config["dependencies"][path]["version"] = version
        updated_dependencies.append(path)