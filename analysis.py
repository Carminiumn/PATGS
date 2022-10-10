from utils import *
from sys import argv

if len(argv) != 2:
    print("Please provide the path to the XML files.")
    exit(1)

XML_PATH = argv[1]
IMAGE_PATH = argv[1] + 'images/'

if __name__ == '__main__':
    num_of_files = 0
    num_of_files_without_alt = 0
    xml_files = get_xml_files(XML_PATH)

    for inx, xml_name in enumerate(xml_files):
        alt_with_index = extract_alt_from_xml(XML_PATH + xml_name)
        pic_wo_alt = 0
        for _, v in alt_with_index.items():
            if v == '' or v is None:
                pic_wo_alt += 1
        print(f"{xml_name}: {len(alt_with_index.items())}/{pic_wo_alt}")
        num_of_files += 1
        if all(v == '' or v is None for v in alt_with_index.values()):
            num_of_files_without_alt += 1

    print('Number of files: ', num_of_files)
    print('Number of files without alt: ', num_of_files_without_alt)



