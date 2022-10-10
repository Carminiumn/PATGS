from __future__ import print_function

import os  # For file IO
from typing import *  # For type check
from string import digits  # For string stripping

# Google Drive APIs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# For parsing XML files
from bs4 import BeautifulSoup

# Scopes for permissions that the program needs
SCOPES: Final[list[str]] = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
# XML_PATH: Final[str] = "data/"  # Path to the folder containing the XML files
# IMAGE_PATH: Final[str] = "data/images/"  # Path to the folder containing all images


def get_auth_info() -> Any:
    """
    Authorize the user and return the credentials
    ----------
    Read credentials from the credentials.json file, and authorize the user and write the token to the token.json file.

    :return: Credentials object
    """

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def create_folder(service_client: Any, folder_name: str, parent_folder: list[str] = None) -> str:
    """
    Create a folder in the Google Drive and prints the folder ID
    ----------
    # TODO: Add detailed description

    :param service_client: Drive API client
    :param folder_name: Name of the folder to be created
    :param parent_folder: List of IDs of the parent folders
    :return: ID of the folder created
    """

    # creds, _ = google.auth.default()
    if parent_folder is None:
        parent_folder = []

    try:
        # create drive api client
        service = service_client
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': parent_folder
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Folder has created with ID: "{file.get("id")}".')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')


def share_with_everyone(service_client: Any, file_id: str) -> bool:
    try:
        # create drive api client
        service = service_client

        user_permission = {
            'type': 'anyone',
            'role': 'writer',
        }
        service.permissions().create(fileId=file_id,
                                     body=user_permission,
                                     fields='id', ).execute()

        print(f'File with ID "{file_id}" has been shared with everyone.')

    except HttpError as error:
        print(F'An error occurred: {error}')

    return True


def upload_to_folder(service_client: Any, file_path: str, real_folder_id: str) -> str:
    """Upload a file to the specified folder and prints file ID, folder ID
    Args: Id of the folder
    Returns: ID of the file uploaded
    """

    try:
        # create drive api client
        service = service_client

        folder_id = real_folder_id
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path,
                                mimetype='image/jpeg', resumable=True)
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File with ID: "{file.get("id")}" has added to the folder with '
              F'ID "{real_folder_id}".')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return "https://drive.google.com/uc?id=" + file.get('id')


def get_xml_files(folder_path: str) -> list[str]:
    # list to store all xml file names
    xml_files = []

    # determine if each file in 'path' is a xml file
    # append the file name to xml_files if it is xml
    for file in os.listdir(folder_path):
        if file.endswith('.xml'):
            xml_files.append(file)

    return xml_files


def get_images_with_given_xml(folder_path: str, xml_file: str) -> list[str]:
    images = []

    for image in os.listdir(folder_path):
        if image.startswith(xml_file.rstrip(".xml")):
            images.append(image)

    return sorted(images, key=lambda index: int(index.rstrip(".jpg").split("_")[-1]))


def create_sheet(service_client: Any, sheet_name: str, parent_folder: str = None) -> str:
    if parent_folder is None:
        parent_folder = []

    try:
        # create drive api client
        service = service_client
        file_metadata = {
            'name': sheet_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [parent_folder]
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Sheet has created with ID: "{file.get("id")}".')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('id')


def fill_sheet(service_client: Any, sheet_id: str, values: list[list[str]]) -> Any:
    # pylint: disable=maybe-no-member
    try:
        service = service_client
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range="A1",
            valueInputOption="USER_ENTERED", body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def extract_alt_from_xml(xml_file: str) -> dict[Union[str, bytes], Any]:
    with open(xml_file, 'r') as f:
        data = f.read()

    bs_data = BeautifulSoup(data, "xml")
    figure_tags = bs_data.find_all('Figure')

    alt_with_idx = {}

    suffix_1 = 2
    suffix_2 = 2
    for tag in figure_tags:
        imagedata_tag = tag.find('ImageData')
        if imagedata_tag is None:
            if alt_with_idx.get('No name') is None:
                alt_with_idx["No name"] = tag.get('Alt')
            else:
                alt_with_idx[f"No name{suffix_1}"] = tag.get('Alt')
                suffix_1 += 1
        else:
            if alt_with_idx.get(os.path.basename(imagedata_tag.get('src')).rstrip(digits)) is None:
                # print(os.path.basename(imagedata_tag.get('src')))
                alt_with_idx[os.path.basename(imagedata_tag.get('src'))] = tag.get('Alt') if tag.get(
                    'Alt') is not None else ""

            # Edge case when an image is reused
            else:
                # print(f"{os.path.basename(imagedata_tag.get('src'))}{suffix_2}")
                alt_with_idx[f"{os.path.basename(imagedata_tag.get('src'))}{suffix_2}"] = tag.get('Alt')
                suffix_2 += 1

    return alt_with_idx
