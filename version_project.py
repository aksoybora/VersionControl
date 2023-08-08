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
        
        else:
            print("\nERROR: Invalid command!\n")
    except Exception as e:
        print("Something went wrong:",e)


def txt_read(folder_name):
    try:
        txt_file = "CMakeLists.txt"
        txt_path = os.path.join(folder_name, txt_file)

        print("AAA" + txt_path)

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
            print("ilk ife girdim :P\n")

        version_h_path = os.path.join(workspace_path,file_path)
        version_h_path = os.path.join(version_h_path,'version.h')
        print("BURADAYIM! "+version_h_path)

        if os.path.exists(version_h_path):
            with open(version_h_path,"r") as file3:
                contents_of_version_h = file3.read()
                print("ikinci ife girdim "+ contents_of_version_h)
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
            data[folder_name]["version " + version_info] = {}

        data[folder_name]["version " + version_info].update(a)

        with open("output.json", "w") as json_file:
            json.dump(data, json_file, indent=3)
    except Exception as e:
        print("ERROR! save_to_json:",e)


if __name__ == "__main__":
    main()
