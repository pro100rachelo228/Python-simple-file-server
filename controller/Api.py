from json import JSONDecoder, JSONEncoder
from os import listdir, path
from pathlib import PurePath
from urllib.parse import unquote
from Functions import determinator, read_file
from exceptions.IncorrectApiRequest import IncorrectApiRequestException
from assets.icons import icons


class ApiController:

    @staticmethod
    def getFolder(root, url):
        if len(url) > 0 and url[0] == "/": url = url[1:]
        real_path = path.realpath(path.join(root, unquote(url)))
        try:
            rurl = PurePath(real_path).relative_to(PurePath(path.realpath(root)))
            if path.exists(path.join(root, str(rurl))):
                url = str(rurl)
            else:
                return JSONEncoder().encode({
                    "result": "error",
                    "cause": f"Didn't find path {url}",
                    "data": []
                })
        except ValueError:
            if url == "/":
                real_path = root
            else:
                return JSONEncoder().encode({
                    "result": "error",
                    "cause": f"Didn't find path {url}",
                    "data": []
                })
        if url != "/" and not path.isdir(real_path):
            url = "/"
            real_path = root
        url = url.replace("\\", '/')
        if url == "/": url = ""
        files, folders = [], []
        for current_file in listdir(real_path):
            if path.isdir(path.join(real_path, current_file)) :
                folders.append(current_file)
            else:
                files.append(current_file)
        data = []
        for current_file in folders + files:
            is_folder = current_file in folders
            if is_folder:
                icon = read_file("assets/icons/folder.svg").decode()
            else:
                ext = current_file.split(".")[-1]
                icon = read_file(f'assets/icons/{ext if ext in icons else "blank"}.svg').decode()
            actual_size = path.getsize(path.join(real_path, current_file))
            size = determinator(actual_size) if current_file not in folders else "-"
            data.append({
                "name": current_file,
                "size": size,
                "icon": icon,
                "is_folder": is_folder
            })     
        return JSONEncoder().encode({
            "result": "ok",
            "cause": "",
            "data": data
        })       
        

    def handle(self, handler, url):
        if handler.command != "POST":
            raise IncorrectApiRequestException("api request was not POST.")
        req = url[0]
        cont_len = int(handler.headers.get('content-length'))
        data = handler.rfile.read(cont_len).decode()
        data = JSONDecoder().decode(data)
        result = ""
        match req:
            case "get-folder":
                if "path" not in data or type(data["path"]) != str:
                    raise IncorrectApiRequestException("no path argument in get-folder request data")
                handler.reactive_headers["Content-Type"] = "application/json"
                result = ApiController.getFolder(handler.root, data["path"])
        return result.encode()