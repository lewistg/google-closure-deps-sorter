import re
import shlex
import subprocess
import sys

class CircularDependencyException(Exception):
    pass

def buildFileDependencyGraph(filePaths):
    def getProvidedNamespaces(filePath):
        try:
            command = shlex.split("grep -e \"goog.provide(\".*\")\" -e \"goog.provide('.*')\" -e \"goog.module('.*')\" -e \"goog.module(\".*\")\" {}".format(filePath))
            rawMatches = subprocess.check_output(command)
            return map(lambda m: m[0] if m[0] else m[1], re.findall("\('(.*)'\)|\(\"(.*)\"\)", rawMatches))
        except:
            return ""

    def getRequiredNamespaces(filePath):
        try:
            command = shlex.split("grep -e \"goog.require(\".*\")\" -e \"goog.require('.*')\" {}".format(filePath))
            rawMatches = subprocess.check_output(command)
            return map(lambda m: m[0] if m[0] else m[1], re.findall("\('(.*)'\)|\(\"(.*)\"\)", rawMatches))
        except:
            return ""

    fileProvidingNamespace = {}
    requiredNamespaces = {}
    for filePath in filePaths:
        providedNamespaces = getProvidedNamespaces(filePath)
        for namespace in providedNamespaces:
            fileProvidingNamespace[namespace] = filePath

        requiredNamespaces[filePath] = getRequiredNamespaces(filePath)

    fileDependencyGraph = {}
    for filePath in filePaths:
        requiredFiles = set()
        for namespace in requiredNamespaces[filePath]:
            if namespace in fileProvidingNamespace:
                requiredFiles.add(fileProvidingNamespace.get(namespace))

        fileDependencyGraph[filePath] = requiredFiles

    return fileDependencyGraph

def getTopologicalSort(fileDependencyGraph):
    sortedFiles = []
    alreadySortedFiles = set()

    alreadyVisiting = set()
    def visit(filePath):
        if filePath in alreadySortedFiles:
            return

        alreadyVisiting.add(filePath)
        for requiredFilePath in fileDependencyGraph[filePath]:
            if requiredFilePath in alreadyVisiting:
                raise CircularDependencyException
            visit(requiredFilePath)

        alreadyVisiting.remove(filePath)
        sortedFiles.append(filePath)
        alreadySortedFiles.add(filePath)

    for filePath in fileDependencyGraph:
        visit(filePath)

    return sortedFiles

def getDependencyOrder(filePaths):
    fileDependencyGraph = buildFileDependencyGraph(filePaths)
    return getTopologicalSort(fileDependencyGraph)

if __name__ == "__main__":
    print getDependencyOrder(sys.argv[1:])
