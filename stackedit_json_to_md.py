import os
import json
import re
import platform


JSON_DIR = None # directory where json file is located. e.g. r"C:\Users\<username>\Downloads".
JSON_NAME = "StackEdit workspace.json"
WIN_ILLEGAL_CHARS = r'[>*|<"?:]'  # regex


if not JSON_DIR:
    raise FileNotFoundError("Specify where "+JSON_NAME+" is located")



def main():
    is_windows = platform.system() == "Windows"
    file_dir = os.path.join(JSON_DIR, "StackEdit")

    read_stackedit_json(file_dir=file_dir, encoding='utf-8-sig',
                        remove_illegal_chars=is_windows, update=False)
    print("Done.")


def read_stackedit_json(file_dir=JSON_DIR, encoding='utf-8-sig', remove_illegal_chars=False, update=False):
    """reads "StackEdit workspace.json" file and creates Markdown files accordingly

    :param str file_dir: where the files will be located
    :param str encoding: encoding to use when opening file
    :param bool remove_illegal_chars: remove illegal characters for Windows filenames
    :param bool update: truncate and write to file even when file already exists.
    """

    paths = dict()  # id : path

    with open(os.path.join(JSON_DIR, JSON_NAME), mode='r', encoding=encoding) as json_file:
        data = json.load(json_file)

    # fill in `paths`
    for data_id, v in data.items():
        if v["type"] == "file":
            stackedit_path = get_stackedit_path(data, data_id)
            filepath = os.path.join(file_dir, stackedit_path + ".md")
            paths.update({data_id: filepath})

    if remove_illegal_chars:
        for k, path in paths.items():
            dirve, the_rest = os.path.splitdrive(path)
            paths[k] = os.path.join(dirve, re.sub(
                WIN_ILLEGAL_CHARS, "", the_rest))

    # create markdown files accordingly
    for data_id, filepath in paths.items():

        # ensure directory exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        if not update and os.path.exists(filepath):
            raise FileExistsError(filepath+" already exists.")

        with open(filepath, mode='w', encoding=encoding) as md_file:
            content_id = data_id + "/content"
            md_file.write(data[content_id]["text"])


def get_stackedit_path(data: dict, data_id: str) -> str:
    """a recursion function that builds path from
    stackedit file structure using data from "StackEdit workspace.json" file.

    :parm dict data: stackedit's json export data.
    :param int data_id: each data's id, key.
    :return: path stackedit file structure.
    :rtype: str
    """
    parent_id = data[data_id]["parentId"]
    name = data[data_id]["name"]

    if not parent_id:
        return name

    elif parent_id == "trash":
        return os.path.join(".trash", name)

    else:
        return os.path.join(get_stackedit_path(data, parent_id), name)


if __name__ == '__main__':
    main()
