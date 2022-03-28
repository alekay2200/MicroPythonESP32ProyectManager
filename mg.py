from argparse import ArgumentParser
from subprocess import Popen, PIPE
from PyFileSystem.fileSystem import get_files, get_directories
from os.path import join

MAIN = "main.py"

def __isMicroPythonDir(item: str):
    return item.find(".") == -1

def __is_hidden(item: str):
    return item[0] == "."

def cli():
    parser = ArgumentParser(prog="mg", 
                            description="MicroPython ESP32 proyect manager")

    parser.add_argument("port", help="specify port where esp32 is connected")
    parser.add_argument("--upload", help="upload the entire proyect, must containt a main.py on the root")
    parser.add_argument("--tree", help="", action="store_true")
    parser.add_argument("--run", help="run especify file")

    return parser.parse_args()


def upload_command(path_to_proyect: str, device_port: str):
    root_files = get_files(path_to_proyect)
    if not MAIN in root_files:
        print("Theres no '", MAIN, "' file on root folder of the proyect")
        exit(0)
    
    files_and_folders = root_files + get_directories(path_to_proyect)
    for item in files_and_folders:
        if __is_hidden(item): continue
        p = Popen(f"ampy --port {device_port} put {join(path_to_proyect, item)}", stdout=PIPE, shell=True)
        print(f"Uploading {join(path_to_proyect, item)}...")
        p.communicate()

def run_from_board_command(file: str, device_port: str):
    path = file.split("/")
    if len(path) > 1:
        path = "/".join(path[:-1])
    else:
        path = ""
    p = Popen(f"ampy --port {device_port} ls {path}", stdout=PIPE, shell=True)
    out_bytes, err = p.communicate()
    out = out_bytes.decode("utf-8")
    out = out.split("\n")
    content = out[:-1] # Remove last element, is an empty line break

    exists = False
    for f in content:
        _file = f.split("/")[-1]
        if _file == file.split("/")[-1]:
            exists = True
            break
    
    if exists:
        p = Popen(f"ampy --port {device_port} run {file}", stdout=PIPE, shell=True)
        print(f"Executing {file}...")
        print(p.communicate())

    else:
        print(f"File {file} not exists")
    
def tree_command(path: str, device_port: str, deep: int):
    p = Popen(f"ampy --port {device_port} ls {path}", stdout=PIPE, shell=True)
    out_bytes, err = p.communicate()
    out = out_bytes.decode("utf-8")
    out = out.split("\n")
    out = out[:-1] # Remove last element, is an empty line break
    
    for item in out:
        if deep > 0:
            _item = item.split("/")[-1]
        else:
            _item = item[1:]

        # Print \t
        for i in range(0,deep):
            print("  ", end="")

        print(" ", _item)
        if __isMicroPythonDir(item):
            tree_command(join(path, _item), device_port, deep+1)

if __name__ == "__main__":
    args = cli()

    if args.tree:
        tree_command("", args.port, 0)

    if args.upload:
        upload_command(args.upload, args.port)