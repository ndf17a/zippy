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

def checkIfDownloads(subs):
    for i in subs:
        if not i['submitted_at'] is None:
            if 'attachments' in i:
                attach = i['attachments'][0]
                if 'url' in attach:
                    return True

def downloadzips(code, a):

     #= "Week 03 check - Dynamic Unit Test"
    aCount = 0
    for j in a.json():
        jname = strip_tags(j['name'])
        jid = j['id']
        if str(aCount) == code:
            sUrl = "https://acu.instructure.com/api/v1/courses/3425464/assignments/" + str(jid) + "/submissions?per_page=100"
            count = 0
            subR = requests.get(sUrl, headers=headers).json()
            if not checkIfDownloads(subR):
                print(color.YELLOW + "No Downloads in this assignment!" + color.END)
                return False
            print(color.YELLOW + "Downloading Assignments from '" + jname, str(jid) + color.END)
            for i in subR:
                if i['submitted_at'] is None:
                    print("No submission")
                else:
                    att = i['attachments'][0]
                    downloadUrl = att['url']
                    displayName = att['display_name']
                    downloadR = requests.get(downloadUrl, allow_redirects=True, headers=headers)
                    openPath = rootPath + "/" + str(count) + "_" + displayName
                    if os.path.exists(openPath):
                        print(str(count) + "_" + displayName + " already exists")
                    else:
                        with open(openPath, 'wb') as f:
                            f.write(downloadR.content)
                        print(str(count) + "_" + displayName + " downloaded")

                count += 1
        aCount+=1
    return True

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
    submissionsR = requests.get(aUrl, headers=headers)

    for j in submissionsR.json():
        cid = j['id']
        sub_type = []
        sub_type = j['submission_types']
        if count < 10:
            space = " "
        else:
            space = ""

        if "check" in j['name'].lower():
            output = color.PURPLE + str(count) + color.END + ": " + color.YELLOW + space + strip_tags(j['name'] + color.END)
        else:
            output = color.PURPLE + str(count) + color.END+ ": " + space + strip_tags(j['name'])

        if not sub_type[0] == "none":
            output += ":"
            typeCount = 0
            for type in sub_type:
                if type == "online_quiz":
                    output = output + " quiz"
                if type == "online_text_entry":
                    output = output + " text-entry"
                if type == "online_upload":
                    output = output + " upload"
                if typeCount < len(sub_type)-1:
                    output = output + ","
                typeCount += 1

        print(output)
        count+=1

    return submissionsR;

if __name__ == '__main__':

    r = outputAssignments()
    assignmentCode = input(color.YELLOW + '\n\nChoose an Assignments number?\n' + color.CYAN + 'i.e. enter 18 for "Week 03 check - Dynamic Unit Test"\n' + color.END)

    if downloadzips(assignmentCode, r):
        unzip(files_in_dir(rootPath))
        paths = find_files('pom.xml', rootPath)
        print(color.YELLOW + "Projects to be tested: " + color.END)
        print(paths)
        runMvn(paths)
