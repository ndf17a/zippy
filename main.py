import shutil
import zipfile
import os
import subprocess
import re
from html.parser import HTMLParser
from io import StringIO
from os.path import exists
import requests
import urllib.request

rootPath = "C:/Users/Nicolas/Desktop/root"
headers = {'Authorization': 'Bearer 1~OEjTUpaq01Xh0jxbu0uTlpaAm3Smhcyh6pVuUcLqPEtUpoYvnlvDxdEBsaGxgzjJ'}

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def downloadzips(code, a):

     #= "Week 03 check - Dynamic Unit Test"
    aCount = 0
    for j in a.json():
        jname = strip_tags(j['name'])
        jid = j['id']
        if str(aCount) == code:
            print(color.YELLOW + "Downloading Assignments from '" + jname, str(jid) + color.END)
            sUrl = "https://acu.instructure.com/api/v1/courses/3425464/assignments/" + str(jid) + "/submissions?per_page=100"
            count = 0
            for i in requests.get(sUrl, headers=headers).json():
                if 'attachments' in i:
                    att = i['attachments'][0]
                    if 'url' in att:
                        downloadUrl = att['url']
                        displayName = att['display_name']
                        r = requests.get(downloadUrl, allow_redirects=True, headers=headers)
                        openPath = rootPath + "/" + str(count) + "_" + displayName
                        if os.path.exists(openPath):
                            print(str(count) + "_" + displayName + " already exists")
                        else:
                            with open(openPath, 'wb') as f:
                                f.write(r.content)
                            print(str(count) + "_" + displayName + " downloaded")

                        count += 1
                    else:
                        print("No url")
                else:
                    print("No submission")
        aCount+=1


def unzip(zipped_files):
    remake = False
    for zip_file in zipped_files:
        mkfile = (zip_file.replace(".zip", "-unzipped"))
        if exists(mkfile):
            shutil.rmtree(mkfile)
            remake = True

        os.mkdir(mkfile)
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(mkfile)

    if remake:
        print(color.YELLOW + "Deleted and Re-Unzipped some files that already existed" + color.END)


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


# mvn -f path/pom.xml clean test
def runMvn(mvnPaths):
    passed = 0
    failed = 0
    u = "https://acu.instructure.com/api/v1/courses/3425464/enrollments"
    userRequest = requests.get(u, headers=headers)


    for path in mvnPaths:
        authorID = re.findall("\D{3}\d{2}\D", path)[0].replace("/","") if re.findall("\D{3}\d{2}\D", path) else (
            "AuthorID not found: ", path)
        list_files = subprocess.run(['mvn', '-f', path, 'clean', 'test'],
                                    shell=True,
                                    encoding='UTF-8',
                                    stdout=subprocess.PIPE)
        output = list_files.stdout

        authorName = ""
        for i in userRequest.json():
            if i['user']['login_id'] == authorID:
                authorName = i['user']['name']
        print("---------------------------------------\n"
              + "Author:", authorName)
        if "[INFO] BUILD FAILURE" in output:
            print(color.YELLOW + "Compilation error mvn test output:" + color.END + "\n"
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
            result = color.GREEN + "Passed" + color.END if testRuns and testFails == 0 and testErrors == 0 and testSkips == 0 else color.RED + "Failed" + color.RED
            print("Result:",  result)

            if "Passed" in result:
                passed+=1
            if "Failed" in result:
                failed+=1

    print("\n")
    print("===============")
    print("|  Passed:", passed, "|")
    print("|  Failed:", failed, " |")
    print("===============")

def outputAssignments():
    count = 0
    aUrl = "https://acu.instructure.com/api/v1/courses/3425464/assignments?per_page=100"
    r = requests.get(aUrl, headers=headers)

    for j in r.json():
        print(color.PURPLE + str(count) + color.END + ": " + strip_tags(j['name']))
        count+=1

    return r;

if __name__ == '__main__':



    #r = outputAssignments()
    #code = input(color.YELLOW + '\n\nChoose an Assignments number?\n' + color.CYAN + 'i.e. enter 18 for "Week 03 check - Dynamic Unit Test"\n' + color.END)
    #downloadzips(code, r)
    #unzip(files_in_dir(rootPath))
    paths = find_files('pom.xml', rootPath)
    print(color.YELLOW + "Projects to be tested: " + color.END)
    print(paths)
    runMvn(paths)
