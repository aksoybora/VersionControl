import sys
import os
import re
import json
import platform


def main():
    try:
        if len (sys.argv) < 2:
            print("\nHATA: Lutfen bir komut belirtin!!\n")
            return
        
        komut = sys.argv[1]

        if komut == "save":
            if len(sys.argv) < 3:
                print("\nHATA: Lutfen klasor ismini belirtin!\n")
                return
            
            klasor_ismi = sys.argv[2]
            #txt_oku_ve_kaydet(klasor_ismi)
            versiyon_bilgisi_degeri = versiyon_bilgisini_al(klasor_ismi)
            json_kaydet(klasor_ismi, versiyon_bilgisi_degeri, txt_oku_ve_kaydet(klasor_ismi))
        
        else:
            print("\nHATA: Gecersiz Komut!\n")
    except Exception as e:
        print("Bir hata olustu:",e)


def txt_oku_ve_kaydet(klasor_ismi):
    try:
        txt_dosyasi = "CMakeLists.txt"
        txt_yolu = os.path.join(klasor_ismi, txt_dosyasi)

        if os.path.exists(txt_yolu):
            with open(txt_yolu, "r") as dosya:
                alt_satir = False
                alinan_degerler = []
                for line in dosya:
                    curline = line.strip()
                    if alt_satir:
                        if "{CMAKE_CURRENT_SOURCE_DIR}" in curline:
                            # Eşleşme bulundu, burada yapmak istediğiniz işlemi yapabilirsiniz
                            dosya_yolu = curline.replace("${CMAKE_CURRENT_SOURCE_DIR}/../", "").strip()
                            alinan_degerler.append(dosya_yolu)
                        else:
                            # Başka bir ifade geldiğinde alt satırdan çık
                            alt_satir = False
                    elif curline.startswith("include_directories(${PROJECT_NAME} PUBLIC"):
                        # "include_directories(${PROJECT_NAME} PUBLIC" ile başlayan satır bulundu
                        alt_satir = True
            a = {}
            for dosya_yolu in alinan_degerler:
                try:
                    versiyonlar = versiyonları_al(alinan_degerleri_oku(dosya_yolu))
                    if versiyonlar:
                        dosya_yolu = dosya_yolu.split("/")[0]
                        a[dosya_yolu] = versiyonlar
                except Exception as e:
                    print("Hata:", e)
                    pass
            return a
    except Exception as e:
        print("HATA! txt_oku_ve_kaydet:",e)
        return None
    

def alinan_degerleri_oku(dosya_yolu):
    try:
        if platform.system() == "Windows":
            dosya_yolu = dosya_yolu.replace("/", "\\")  # Ters slash'ları normal slash'a dönüştür
        version_h_yolu = os.path.join(dosya_yolu,'version.h')
        if os.path.exists(version_h_yolu):
            with open(version_h_yolu,"r") as dosya3:
                version_h_larin_icerikleri = dosya3.read()
                return version_h_larin_icerikleri
        else:
            print("version.h bulunamadi " + dosya_yolu)
    except Exception as e:
        print("HATA! alinan_degerleri_oku:",e)
        return None


def versiyonları_al(version_h_larin_icerikleri):
    try:
        if version_h_larin_icerikleri:
            majorv = re.search(r'#define\s+MAJOR_VERSION\s+(\d+)', version_h_larin_icerikleri)
            minorv = re.search(r'#define\s+MINOR_VERSION\s+(\d+)', version_h_larin_icerikleri)
            patchv = re.search(r'#define\s+PATCH_VERSION\s+(\d+)', version_h_larin_icerikleri)

            if majorv and minorv and patchv:
                # Değeleri alıp istenen formatta versiyon bilgisini oluşturma
                versiyon_bilgisi_d = f"{majorv.group(1)}.{minorv.group(1)}.{patchv.group(1)}"
                return versiyon_bilgisi_d
            else:
                print("version bilgisini bulamadim")
    except Exception as e:
        print("HATA! versiyonları_al:",e)
        return None
        

def versiyon_bilgisini_al(klasor_ismi):
    try:
        include_yolu = os.path.join(klasor_ismi, "include")

        if os.path.exists(include_yolu):
            version_yolu = os.path.join(include_yolu, "version.h")

            if os.path.exists(version_yolu):
                with open(version_yolu,"r") as dosya_2:
                    icerik = dosya_2.read()
                    # Düzenli ifadeyle MAJOR_VERSION, MINOR_VERSION ve PATCH_VERSION değerlerini bulma
                    major = re.search(r'#define\s+MAJOR_VERSION\s+(\d+)', icerik)
                    minor = re.search(r'#define\s+MINOR_VERSION\s+(\d+)', icerik)
                    patch = re.search(r'#define\s+PATCH_VERSION\s+(\d+)', icerik)

                    if major and minor and patch:
                        # Değeleri alıp istenen formatta versiyon bilgisini oluşturma
                        versiyon_bilgisi = f"{major.group(1)}.{minor.group(1)}.{patch.group(1)}"

                    else:
                        print("\nHATA: Versiyon bilgileri bulunamadı!\n")

            else:
                print("\nHATA: 'version.h' dosyası bulunamadı!\n")

        else:
            print(f"\nHATA: {klasor_ismi} icinde 'include' adinda bir klasor bulunamadi!\n")

        return versiyon_bilgisi
    except Exception as e:
        print("HATA! versiyon_bilgisini_al:",e)
        return None


def json_kaydet(klasor_ismi, versiyon_bilgisi, a={}):
    try:
        try:
            with open("output.json", "r") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {}

        if klasor_ismi not in data:
            data[klasor_ismi] = {}

        if "version " + versiyon_bilgisi not in data[klasor_ismi]:
            data[klasor_ismi]["version " + versiyon_bilgisi] = {}

        data[klasor_ismi]["version " + versiyon_bilgisi].update(a)

        with open("output.json", "w") as json_file:
            json.dump(data, json_file, indent=3)
    except Exception as e:
        print("HATA! json_kaydet:",e)


if __name__ == "__main__":
    main()
