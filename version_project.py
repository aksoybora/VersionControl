import sys
import os
import re
import json
import platform

workspace_path = ".."

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
                print("\nPlease enter a client name!\n")

            client_name = sys.argv[2]
            version_name = sys.argv[3]
            read_the_versions(client_name,version_name)

        elif command == "control":
            if len(sys.argv) < 3:
                print("\nPlease enter a client name!\n")

            client_name = sys.argv[2]
            control_version(client_name)

        else:
            print("\nERROR: Invalid command!\n")

    except Exception as e:
        print("Something went wrong:",e)


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
            majorv = re.search(r'#define\s+MAJOR_VERSION\s+(\d+)', contents_of_version_h)
            minorv = re.search(r'#define\s+MINOR_VERSION\s+(\d+)', contents_of_version_h)
            patchv = re.search(r'#define\s+PATCH_VERSION\s+(\d+)', contents_of_version_h)

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
                    major = re.search(r'#define\s+MAJOR_VERSION\s+(\d+)', content)
                    minor = re.search(r'#define\s+MINOR_VERSION\s+(\d+)', content)
                    patch = re.search(r'#define\s+PATCH_VERSION\s+(\d+)', content)

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


def read_the_versions(client_name, version_name):
    try:
        with open("output.json","r") as read_file:
            json_info = json.load(read_file)
    except FileNotFoundError:
        print("JSON file not found!")

    if json_info[client_name][version_name]:
        print("\nFound the json_info: \n", json_info)
        print(json_info[client_name][version_name])
    else:
        print("Wrong command!")


# def control_version(client_name):
#     try:
#         with open("output.json","r") as control_file:
#             control_versions = json.load(control_file)
#     except FileNotFoundError:
#         print("JSON file not found!")

#     if control_versions:
#         desired_control_versions = control_versions[client_name]
#         versions_list = list(desired_control_versions.keys()) # Gets all version numbers as a list

#     for i in range(len(versions_list)-1): # To compare successive versions
#         old_version = versions_list[i]
#         new_version = versions_list[i+1]

#         old_files = desired_control_versions[old_version] # Old version file information
#         new_files = desired_control_versions[new_version] # New version file information

#         print(f"\n--- {old_version} vs {new_version} ---\n")

#         # Compares version information for each file
#         for control_file, old_version in old_files.items():
#             new_version = new_files.get(control_file) # Check if the file is available in the new version
#             if new_version:
#                 if old_version != new_version:
#                     print(f"File: {control_file} --> old version: {old_version} , new version: {new_version}")
#                 else:
#                     print(f"File: {control_file} --> No version change.")
#             else:
#                 print(f"File: {control_file} is not available in the new version.")

if __name__ == "__main__":
    main()
