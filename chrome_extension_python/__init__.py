from urllib.parse import urlparse
import glob
from threading import Lock
import re
from requests import get
from zipfile import ZipFile, BadZipFile
from io import BytesIO
import os
from urllib.parse import unquote
from .package_storage import PackageStorage


def relative_path(path, goback=0):
    levels = [".."] * (goback + -1)
    return os.path.abspath(os.path.join(os.getcwd(), *levels, path.strip()))


def download_and_unzip_chrome_extension(extension_id, download_dir):
    chrome_version = "120.0.0.0"
    crx_url = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion={chrome_version}&x=id%3D{extension_id}%26installsource%3Dondemand%26uc&acceptformat=crx2,crx3"

    response = get(crx_url)

    if response.status_code != 200:
        raise Exception(f"Failed to download extension {extension_id}")

    try:
        with ZipFile(BytesIO(response.content)) as z:
            z.extractall(download_dir)
    except BadZipFile:
        raise Exception(
            "Failed to unzip the CRX file. It might not be a valid zip file."
        )


def extract_name(path):
    parts = path.split("/")
    return parts[-1] if parts else None


def extract_extension_id_and_name(path: str):
    pattern = r".+?\/([a-z]{32})(?=[\/#?]|$)"
    path = unquote(path.lstrip("/webstore"))

    match = re.search(pattern, path)
    if match:
        extension_id = match.group(1)
        name = extract_name(path.strip("/").replace(extension_id, "").strip("/"))
        if name:
            return name, extension_id
        else:
            raise Exception("Failed to extract extension name from link")

    raise Exception("Failed to extract extension ID from link")


def extract_path_from_link(link):
    return urlparse(link).path


class File:
    def __init__(self, path):
        self.path = path

    def update_contents(self, update_function):
        file_contents = self.get_contents()

        updated_contents = update_function(file_contents)

        if updated_contents is None:
            raise Exception("No content is returned from update_function")

        self.write_contents(updated_contents)

    def write_contents(self, updated_contents):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(updated_contents)

    def get_contents(self):
        with open(self.path, "r", encoding="utf-8") as file:
            file_contents = file.read()
        return file_contents


def create_directory_if_not_exists(passed_path):
    dir_path = relative_path(passed_path, 0)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def create_extensions_directory_if_not_exists():
    create_directory_if_not_exists("extensions/")


lock = Lock()


class Extension:
    def __init__(
        self,
        extension_link=None,
        extension_id=None,
        extension_name=None,
        force_update=False,
        
        **kwargs,
    ):
        self.extension_link = extension_link
        self.force_update = force_update

        if extension_link:

            extension_name, extension_id  = extract_extension_id_and_name(
                extract_path_from_link(extension_link)
            )

        self.extension_id = extension_id
        self.extension_name = extension_name

        if not extension_id:
            raise ValueError("Extension ID is required.")

        if not extension_name:
            raise ValueError("Extension name is required.")

        self.kwargs = kwargs

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.extension_path = f"extensions/{extension_name}"

        self.extension_absolute_path = relative_path(self.extension_path)


    def download(self):
        print(f"Downloading {self.extension_name} Extension ...")
        create_extensions_directory_if_not_exists()
        download_and_unzip_chrome_extension(
            self.extension_id, self.extension_absolute_path
        )

    def get_files(self, ext):
        files = glob.glob(self.extension_path + "/**/*" + ext, recursive=True)
        files = [os.path.abspath(file) for file in files]

        files = [File(file) for file in files]

        return files

    def exists(self):
        return os.path.exists(self.extension_absolute_path)

    def get_file(self, path):
        return File(relative_path(self.extension_path + path))

    def get_js_files(self):
        return self.get_files(".js")

    def get_json_files(self):
        return self.get_files(".json")

    def get_html_files(self):
        return self.get_files(".html")

    def get_css_files(self):
        return self.get_files(".css")

    def should_update_files(self):

        item = PackageStorage.get_item(self.extension_absolute_path, {})
        extension_data = item.get(self.extension_id)

        if extension_data is None:
            return True
        
        return extension_data != self.kwargs

    def updated_extension_data(self):
        dirname = self.extension_absolute_path

        item = PackageStorage.get_item(dirname, {})
        item[self.extension_id] = self.kwargs

        PackageStorage.set_item(dirname, item)

    def update_files(
        self,
    ):
        pass

    def load(self, with_command_line_option=True):
        with lock:
            if not self.exists() or self.should_update_files() or self.force_update:
                self.download()
                self.update_files(**self.kwargs)
                self.updated_extension_data()

        extension_path = self.extension_absolute_path
        if with_command_line_option:
            return f"--load-extension={extension_path}"
        else:
            return extension_path