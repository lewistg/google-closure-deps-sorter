import googdepsorter as gds
import shlex
import subprocess
import unittest

class TestDepsSorter(unittest.TestCase):
    def getTestFileList(self, testFilesDirName):
        testFiles = subprocess.check_output(shlex.split('find {} -name *.js -print0'.format(testFilesDirName)))
        testFiles = testFiles.split('\0')[:-1]
        return testFiles

    def test_circularDependencyDetection(self):
        with self.assertRaises(gds.CircularDependencyException):
            gds.getDependencyOrder(self.getTestFileList('./test_files/circular_dependency_case/'))

    def test_DagDependencyCase0(self):
        testFileRoot = './test_files/dag_dependency_cases/case0/'
        expectedOrdering = map(
                lambda f: testFileRoot + f,
                ['test5.js', 'test4.js', 'test3.js', 'test2.js', 'test1.js'])
        actualOrdering = gds.getDependencyOrder(self.getTestFileList(testFileRoot))
        self.assertListEqual(expectedOrdering, actualOrdering)

if __name__ == '__main__':
    unittest.main()
