import zipfile
import os
import subprocess
import re


def unzip():
    with zipfile.ZipFile('C:/Users/ndf17a/Desktop/EndGameGame.zip', 'r') as zip_ref:
        zip_ref.extractall('C:/Users/ndf17a/Desktop/here')


def find_files(filename, search_path):
    result = []

    for root, dir, files in os.walk(search_path):
        if filename in files:
            p = os.path.join(root, filename).replace("\\", "/")
            result.append(p)
    return result


# mvn -f path/pom.xml test
def cmd(mvnPaths):
    for path in mvnPaths:
        print("Path: " + path)
        print(re.findall("SE2-.*/$", path))

        list_files = subprocess.run(['mvn', '-f', path, 'test'], shell=True, encoding='UTF-8', stdout=subprocess.PIPE)
        output = list_files.stdout
        indexStart = output.find("Tests run: ")
        indexEnd = output.find("Time elapsed:")
        print(output[indexStart:indexEnd])


if __name__ == '__main__':
    # unzip()
    paths = find_files('pom.xml', 'C:/Onedrive/Desktop/New folder')
    cmd(paths)
