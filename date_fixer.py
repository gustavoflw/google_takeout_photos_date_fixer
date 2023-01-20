import os
import exif
import json
from datetime import datetime
import shutil
import filedate
import pathlib

albums_input_path = "albums_input"
albums_output_path = "albums_output"

class JsonMetadata:
    def __init__(self, json_data):
        self.creationTime           = str(datetime.fromtimestamp(int(json_data["creationTime"]["timestamp"]))).replace("-", ":")
        self.photoTakenTime         = str(datetime.fromtimestamp(int(json_data["photoTakenTime"]["timestamp"]))).replace("-", ":")
        self.photoLastModifiedTime  = str(datetime.fromtimestamp(int(json_data["photoLastModifiedTime"]["timestamp"]))).replace("-", ":")

class Process:
    
    @staticmethod
    def Image(file_path, output_path, allow_print):
        try:
            file_extension = file_path.split(".")[-1]

            json_path = file_path.replace(file_extension, "{}.json".format(file_extension))
            json_exists = os.path.isfile(json_path)

            if allow_print:
                print("  * {}".format(file_path))
                print("    * Expected JSON: {}".format(json_path))
                print("    * JSON exists: {}".format(json_exists))
                print("    * Output path: {}".format(output_path))

            print("    * Creating output file")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy(file_path, output_path)

            with open(file_path, "rb") as file:
                img = exif.Image(file)
                if allow_print:
                    print("    * Current EXIF")
                    print("      * datetime:              {}".format(img.datetime))
                    print("      * datetime_original:     {}".format(img.datetime_original))
                    print("      * datetime_digitized:    {}".format(img.datetime_digitized))

            with open(json_path) as json_file:
                json_data = json.load(json_file)
                json_metadata = JsonMetadata(json_data)
                if allow_print:
                    print("    * JSON metadata")
                    print("      * photoLastModifiedTime: {}".format(json_metadata.photoLastModifiedTime))
                    print("      * photoTakenTime:        {}".format(json_metadata.photoTakenTime))
                    print("      * creationTime:          {}".format(json_metadata.creationTime))

            img.datetime = json_metadata.photoLastModifiedTime
            img.datetime_original = json_metadata.photoTakenTime
            img.datetime_digitized = json_metadata.creationTime

            print("    * Modifying EXIF in output file")
            with open(output_path, 'wb') as file:
                file.write(img.get_file())
            print("    * Done")
        except Exception as exception:
            print("    * ERROR ({})".format(exception))
    
    @staticmethod
    def Video(file_path, output_path, allow_print):
        try:
            file_extension = file_path.split(".")[-1]

            json_path = file_path.replace(file_extension, "{}.json".format(file_extension))
            json_exists = os.path.isfile(json_path)

            if allow_print:
                print("  * {}".format(file_path))
                print("    * Expected JSON: {}".format(json_path))
                print("    * JSON exists: {}".format(json_exists))
                print("    * Output path: {}".format(output_path))

            print("    * Creating output file")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy(file_path, output_path)

            dates = filedate.File(file_path).get()
            date_created = dates["created"]
            date_modified = dates["modified"]
            date_accessed = dates["accessed"]
            print("    * Current metadata")
            print("      * date_created:  {}".format(date_created))
            print("      * date_modified: {}".format(date_modified))
            print("      * date_accessed: {}".format(date_accessed))

            with open(json_path) as json_file:
                json_data = json.load(json_file)
                json_metadata = JsonMetadata(json_data)
                if allow_print:
                    print("    * JSON metadata")
                    print("      * photoLastModifiedTime: {}".format(json_metadata.photoLastModifiedTime))
                    print("      * photoTakenTime:        {}".format(json_metadata.photoTakenTime))
                    print("      * creationTime:          {}".format(json_metadata.creationTime))

            filedate_output_file = filedate.File(output_path)
            filedate_output_file.set(
                created  = json_metadata.creationTime,
                modified = json_metadata.photoLastModifiedTime,
                accessed = json_metadata.photoLastModifiedTime)

        except Exception as exception:
            print("    * ERROR ({})".format(exception))

if __name__ == "__main__":
    if os.path.exists(albums_output_path):
        shutil.rmtree(albums_output_path)

    all_extensions     = set()
    handled_extensions = set()

    for dir in os.listdir(albums_input_path):
        print("\n*", dir)
        dir_path = albums_input_path + "/" + dir
        for item in os.listdir(dir_path):
            file_extension = item.split(".")[-1]
            all_extensions.add(file_extension)

            file_path = dir_path + "/" + item
            output_path = file_path.replace(albums_input_path, albums_output_path)

            if file_extension == "jpeg":
                handled_extensions.add(file_extension)
                Process.Image(file_path, output_path, False)
            elif file_extension == "jpg":
                handled_extensions.add(file_extension)
                Process.Image(file_path, output_path, True)
            elif file_extension == "mp4":
                handled_extensions.add(file_extension)
                Process.Video(file_path, output_path, True)
            elif file_extension == "webp":
                handled_extensions.add(file_extension)
                Process.Video(file_path, output_path, True)

    print("\n* Handled extensions: {}".format(handled_extensions))
    for extension in all_extensions:
        if (extension in handled_extensions) == False and extension != "json":
            print("  * WARNING: .{} not handled!".format(extension))

    print()