import sys
import os
import re
import json
import platform
import subprocess
from git import Repo

workspace_path = ".."
repo_path = ".."

def main():
    try:
        if len (sys.argv) < 2:
            print("\nERROR: Please enter a command!\n")
            return
        
        command = sys.argv[1]

        if command == "save":   
            if len(sys.argv) < 3:
                print("\nERROR: Please specify a folder name!\n")
                return
            
            folder_name = sys.argv[2]
            folder_name = os.path.join(workspace_path, folder_name)
            version_info_value = get_version_info(folder_name)
            save_to_json(folder_name, version_info_value, txt_read(folder_name))

        elif command == "restore":
            if len(sys.argv) < 3:
                print("\nPlease enter a repo name!\n")

            repo_name = sys.argv[2]
            version_name = sys.argv[3]

            try:
                with open("output.json","r") as read_file:
                    json_info = json.load(read_file)
                    deps = json_info[repo_name][version_name]
                    
                    change_exists = check_git_repos(deps)

                    if change_exists:
                        print("Change exists, aborting")
                        return

                    for dep in deps:
                        version = deps[dep]
                        repo = Repo(os.path.join(repo_path, dep))
                        git_checkout(repo, "v" + version)
            except FileNotFoundError:
                print("JSON file not found!")

        elif command == "status":
            check_git_repos(repo_path)

        else:
            print("\nERROR: Invalid command!\n")

    except Exception as e:
        print("Something went wrong:",e)

def git_checkout(repo, branch_name):
    try:
        repo.git.checkout(branch_name)
        print(f"Checked out to branch: {branch_name}")
    except Exception as e:
        print("Error: ", e)


def check_git_repos(repo_list):
    for elem in repo_list:
        repo = os.path.join(repo_path, elem)

        try:
            # Git status komutunu çağırarak repodaki durumu kontrol et
            status_output = subprocess.check_output(['git','status'], cwd=repo).decode('utf-8')

            return not "nothing to commit, working tree clean" in status_output
        except subprocess.CalledProcessError as e:
            print("An error occurred while checking git status:  ", e)


def txt_read(folder_name):
    try:
        txt_file = "CMakeLists.txt"
        txt_path = os.path.join(folder_name, txt_file)

        if os.path.exists(txt_path):
            with open(txt_path, "r") as file:
                bottom_line = False
                received_values = []
                for line in file:
                    curline = line.strip()
                    if bottom_line:
                        if "{CMAKE_CURRENT_SOURCE_DIR}" in curline:
                            # Eşleşme bulundu, burada yapmak istediğiniz işlemi yapabilirsiniz
                            file_path = curline.replace("${CMAKE_CURRENT_SOURCE_DIR}/../", "").strip()
                            received_values.append(file_path)
                        else:
                            # Başka bir ifade geldiğinde alt satırdan çık
                            bottom_line = False
                    elif curline.startswith("include_directories(${PROJECT_NAME} PUBLIC"):
                        # "include_directories(${PROJECT_NAME} PUBLIC" ile başlayan satır bulundu
                        bottom_line = True
            a = {}
            for file_path in received_values:
                try:
                    versions = get_versions(read_received_values(file_path))
                    if versions:
                        file_path = file_path.split("/")[0]
                        a[file_path] = versions
                except Exception as e:
                    print("ERROR:", e)
                    pass
            return a
    except Exception as e:
        print("ERROR! txt_read:",e)
        return None
    

def read_received_values(file_path):
    try:
        if platform.system() == "Windows":
            file_path = file_path.replace("/", "\\")  # Ters slash'ları normal slash'a dönüştür

        version_h_path = os.path.join(workspace_path,file_path)
        version_h_path = os.path.join(version_h_path,'version.h')

        if os.path.exists(version_h_path):
            with open(version_h_path,"r") as file3:
                contents_of_version_h = file3.read()
                return contents_of_version_h
        else:
            print("version.h not found: " + file_path)
    except Exception as e:
        print("ERROR! read_received_values:",e)
        return None


def get_versions(contents_of_version_h):
    try:
        if contents_of_version_h:
            majorv = re.search(r'#define\s\S+MAJOR_VERSION\s+(\d+)', contents_of_version_h)
            minorv = re.search(r'#define\s\S+MINOR_VERSION\s+(\d+)', contents_of_version_h)
            patchv = re.search(r'#define\s\S+PATCH_VERSION\s+(\d+)', contents_of_version_h)

            if majorv and minorv and patchv:
                # Değeleri alıp istenen formatta versiyon bilgisini oluşturma
                version_info_d = f"{majorv.group(1)}.{minorv.group(1)}.{patchv.group(1)}"
                return version_info_d
            else:
                print("Not found version info!")
    except Exception as e:
        print("ERROR! get_versions:",e)
        return None
        

def get_version_info(folder_name):
    try:
        include_path = os.path.join(folder_name, "include")

        if os.path.exists(include_path):
            version_path = os.path.join(include_path, "version.h")

            if os.path.exists(version_path):
                with open(version_path,"r") as file2:
                    content = file2.read()
                    # Düzenli ifadeyle MAJOR_VERSION, MINOR_VERSION ve PATCH_VERSION değerlerini bulma
                    major = re.search(r'#define\s\S+MAJOR_VERSION\s+(\d+)', content)
                    minor = re.search(r'#define\s\S+MINOR_VERSION\s+(\d+)', content)
                    patch = re.search(r'#define\s\S+PATCH_VERSION\s+(\d+)', content)

                    if major and minor and patch:
                        # Değeleri alıp istenen formatta versiyon bilgisini oluşturma
                        version_info = f"{major.group(1)}.{minor.group(1)}.{patch.group(1)}"

                    else:
                        print("\nERROR: Not found version informations!\n")

            else:
                print("\nERROR: Not found 'version.h'!\n")

        else:
            print(f"\nERROR: No folder named 'include' found in {folder_name}!\n")

        return version_info
    except Exception as e:
        print("ERROR! get_version_info:",e)
        return None


def save_to_json(folder_name, version_info, a={}):
    try:
        try:
            with open("output.json", "r") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {}

        if folder_name not in data:
            data[folder_name] = {}

        if "version " + version_info not in data[folder_name]:
            data[folder_name][version_info] = {}

        data[folder_name][version_info].update(a)

        with open("output.json", "w") as json_file:
            json.dump(data, json_file, indent=3)
            print("\nWritten to JSON file.\n")
    except Exception as e:
        print("ERROR! save_to_json:",e)


if __name__ == "__main__":
    main()
