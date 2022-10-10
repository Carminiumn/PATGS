from utils import *
from sys import argv

if len(argv) != 2:
    print("Please provide the path to the XML files.")
    exit(1)

XML_PATH = argv[1]
IMAGE_PATH = argv[1] + 'images/'

if __name__ == '__main__':

    try:
        drive_service = build('drive', 'v3', credentials=get_auth_info())
        sheet_service = build('sheets', 'v4', credentials=get_auth_info())

        # Setup, only need to run once
        parent_id = create_folder(drive_service, "Test")
        share_with_everyone(drive_service, parent_id)

        xml_files = get_xml_files(XML_PATH)

        for inx, xml_name in enumerate(xml_files):

            alt_with_index = {}
            link_with_index = {}
            curr_imgs = get_images_with_given_xml(IMAGE_PATH, xml_name)
            doc_folder_id = create_folder(drive_service, xml_name.rstrip(".xml"), [parent_id])
            img_folder_id = create_folder(drive_service, "images", [doc_folder_id])

            for img in curr_imgs:
                link_with_index[os.path.basename(img)] = upload_to_folder(drive_service, IMAGE_PATH + img,
                                                                          img_folder_id)

            curr_sheet = create_sheet(drive_service, xml_name.rstrip(".xml") + "_alt", doc_folder_id)
            alt_with_index = extract_alt_from_xml(XML_PATH + xml_name)

            cell_data = [[f'=IMAGE("{link_with_index[k.rstrip(digits)]}")',
                          f'=HYPERLINK("{link_with_index[k.rstrip(digits)]}", "Image Link")',
                          v] if link_with_index.get(k.rstrip(digits)) is not None else ['No source image', '', v] for
                         k, v in
                         alt_with_index.items()]

            fill_sheet(sheet_service, curr_sheet, cell_data)

            if inx == 1:
                break

    except HttpError as error:
        print(F'An error occurred: {error}')
