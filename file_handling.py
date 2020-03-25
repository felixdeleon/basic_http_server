import os
import json
import hashlib
import base64


class ClientInfo:
    def __init__(self, data):
        self.request = str(data).split()[0]  # GET or POST request
        try:
            self.path = str(data).split()[1]  # The path that is being requested

        except IndexError:
            print("Error with path!")
        self.cookies = []  # The cookies that are present for the client
        self.form = []  # The contents of a submitted form
        self.length = 0  # Length of the contents of the form
        self.web_socket_key = False
        x = ""

        x = str(data).find("Cookie")
        if x != -1:
            x = str(data)[x:]
            end = x.find('\\r\\n')
            x = x[:end]
            if "jpeg" not in str(data):
                for i in x.split():  # This parses and stores all of the cookies
                    self.cookies.append(str(i))

        x = str(data).find("Content-Length:")
        if x != -1:
            x = str(data)[x:]
            end = x.find('\\r\\n')
            x = x[:end]
            x = x[len("Content-Length:"):]
            self.length = x

        x = str(data).find("Sec-WebSocket-Key:")
        if x != -1:
            x = data[x:]
            end = x.find(b'\r\n')
            x = x[:end]
            x = x.replace(b"Sec-WebSocket-Key: ", b"")
            x += b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            m = hashlib.sha1()
            m.update(x)
            self.web_socket_key = m.hexdigest()

        if "POST" in self.request and "jpeg" not in str(data) and ".json" not in self.path:  # If it is a POST request there is more to do
            walker = str(data)
            while "Content-Disposition:" in walker:
                x = walker.find("name=")
                walker = walker[x:]
                x = walker[:walker.find("\\r\\n\\r\\n")]
                name = x.split("=")[1]
                name = name.replace('"', '')
                x = walker.find("\\r\\n\\r\\n")
                walker = walker[x + 8:]
                content = walker.split("\\r\\n")[0]
                self.form.append((name, content))

        elif ".json" in self.path:
            walker = str(data)
            x = walker.find("\\r\\n\\r\\n")
            y = walker.find("}")
            walker = walker[x + 8: y + 1]
            info = json.loads(walker)

            with open("data/ajax_file.txt", "a") as file:
                for x in info:
                    file.write("The contents of " + x + " is: " + info[x]+'\r\n')
                file.close()
            print(walker)


def build_html(file, info):

    while "{{loop}}" in file:
        start = file.find("{{loop}}")
        end = file.find("{{end_loop}}")
        temp_file = file[start + 8: end]
        swap = ""
        for i in info:
            if ("{{" + i[0] + "}}") in temp_file:
                for j in i[1]:
                    swap += temp_file
                    swap = swap.replace(("{{" + i[0] + "}}"), j)
        temp_file = "{{loop}}" + temp_file + "{{end_loop}}"
        file = file.replace(temp_file, swap)

    for i in info:
        if ("{{" + i[0] + "}}") in file:
            file = file.replace(("{{" + i[0] + "}}"), i[1])

    return file


def response_builder(code, file_type, length):
    response = "HTTP/1.1 "

    if code == 101:
        response = bytes(response.encode('utf-8'))
        temp = base64.b64encode(bytes(file_type.encode('utf-8')))
        response += b"101 Switching Protocols\r\n"
        response += b"Upgrade: websocket\r\n"
        response += b"Connection: Upgrade\r\n"
        response += b"Sec-WebSocket-Accept:" + temp + b"\r\n\r\n"
        return response
    elif code == 200:
        response += "200 OK\r\n"
    elif code == 301:
        response += "301 Moved Permanently\r\nLocation: " + file_type + "\r\n\r\n"
        return response
    else:
        response += "404 Not Found\r\n"

    response += "Content-Type: "

    if file_type == "css":
        response += "text/css;charset=UTF-8;X-Content-Type-Options: nosniff"
    elif file_type == "js":
        response += "text/javascript;charset=UTF-8;X-Content-Type-Options: nosniff"
    elif file_type == "html":
        response += "text/html;charset=UTF-8;X-Content-Type-Options: nosniff\r\nSet-Cookie: id=100"
    elif file_type == "jpeg":
        response += "image/jpeg;"
    elif file_type == "txt":
        response += "text/plain;charset=UTF-8;X-Content-Type-Options: nosniff"

    response += "\r\nContent-Length: " + str(length) + "\r\n\r\n"
    return response


def getFileSize(file):
    f = os.stat(file)
    return f.st_size

