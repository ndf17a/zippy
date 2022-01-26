import zipfile
import os
import subprocess
import re

rootPath = "C:/Users/ndf17a/Desktop/root"


def unzip(zipped_files):
    for zip_file in zipped_files:
        mkfile = (zip_file.replace(".zip", "-unzipped"))
        os.mkdir(mkfile)
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(mkfile)


def find_files(filename, search_path):
    result = []
    for root, dir, files in os.walk(search_path):
        if filename in files:
            result.append(os.path.join(root, filename).replace("\\", "/"))

    return result


def files_in_dir(path):
    file_names = []
    for file in os.listdir(path):
        if file.endswith(".zip"):
            file_names.append(os.path.join(path, file).replace("\\", "/"))

    return file_names


# mvn -f path/pom.xml test
def runMvn(mvnPaths):
    for path in mvnPaths:
        authorID = re.findall("-\D{3}\d{2}\D", path)[0].replace('-', '') if re.findall("-\D{3}\d{2}\D", path) else path
        list_files = subprocess.run(['mvn', '-f', path, 'clean', 'test'],
                                    shell=True,
                                    encoding='UTF-8',
                                    stdout=subprocess.PIPE)
        output = list_files.stdout
        print("---------------------------------------\n"
              + authorID)
        if "[INFO] BUILD FAILURE" in output:
            print("Compilation error mvn test output:\n"
                  + "/////////////////////////////////////////////////////////////////////\n"
                  + output
                  + "\n/////////////////////////////////////////////////////////////////////")
        else:
            indexStart = output.find("Tests run: ")
            indexEnd = output.find("Time elapsed:") - 2
            # Grabs the numbers of of e.x. "Tests run: 2, Failures: 0, Errors: 1, Skipped: 0,"
            testResults = re.findall("\d+", output[indexStart:indexEnd])

            testRuns = int(testResults[0])
            testFails = int(testResults[1])
            testErrors = int(testResults[2])
            testSkips = int(testResults[3])

            print(output[indexStart:indexEnd])
            print("pass" if testRuns and testFails == 0 and testErrors == 0 and testSkips == 0 else "fail")


if __name__ == '__main__':
    unzip(files_in_dir(rootPath))
    paths = find_files('pom.xml', rootPath)
    print(paths)
    runMvn(paths)
