import socket
from os import listdir
from file_handling import *

# codes to be used in response builder
OK = 200
MOVED = 301
NOT = 404

entries = os.listdir("image")
for i in range(len(entries)):
    temp = "/image/" + entries[i]
    entries[i] = temp
# standard buffer size to be used
buffer_size = 2048
# create a socket
sock = socket.socket()
# the port number to be used
port = 8000
socket.SO_REUSEPORT = socket.SO_REUSEADDR
# this is for quality of life when I testS
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# bind the socket
sock.bind(('', port))
print("socket binded to port: " + str(port))

# listen for a connection
sock.listen(5)
print("socket is listening")

# an infinite loop so that the server goes on until its asked to stop
while True:
    data = b''
    # Establish connection with client.
    (client, addr) = sock.accept()

    print('Got connection from', addr)

    # recieve a message from the client
    while True:
        raw = client.recv(buffer_size)
        data += raw
        if len(raw) < buffer_size:
            break
    print(data)
    img_form = False
    if str(data).find("/image-form") != -1 and str(data).find("POST") != -1:
        name = ""
        for i in str(data).split():
            if i.find("filename") != -1:
                name = i.split("=")[1]
                break
        name = name.split('\\r\\n')[0]
        name = name.replace('"', '')
        x = data.find(b'\r\n\r\n')
        print("Raw contents: \n" + str(data))

        data = data[x + 4:]
        x = data.find(b'\r\n\r\n')
        data = data[x + 4:]
        print("\n\n" + str(data) + "\n\n")
        new_image = open("image/"+name, "wb")
        new_image.write(data)
        new_image.close()
        img_form = True

    # this makes it easier to access specific data from the user
    c = ClientInfo(data)
    _id = False

    if "id=100" in c.cookies:
        _id = True
    image = False
    print(c.path)
    # send a response to the user
    if c.path == "/" or c.path == "/index.html":
        info = []
        if _id:
            info.append(("user", "returning"))
        else:
            info.append(("user", "new"))
        file = open("front_end/index.html", "r")

        file = build_html(file.read(), info)
        file_size = getFileSize("front_end/index.html")

        message = response_builder(OK, "html", file_size)
        message += file
    elif c.path == "/form-data":
        print("Form was submitted\n")
        out = open("data/submissions.txt", "a")
        for i in c.form:
            out.write("For " + i[0])
            out.write(" the value was: " + i[1] + "\n")
        file = open("front_end/view/table.html")
        file_size = getFileSize("front_end/view/table.html")
        message = response_builder(OK, "html", file_size)
        message += file.read()
        out.close()
        file.close()
    elif img_form:
        file = open("front_end/view/dark_lord.html")
        file_size = getFileSize("front_end/view/dark_lord.html")
        message = response_builder(OK, "html", file_size)
        message += file.read()
        file.close()
    elif c.request == "POST":
        print("A form was submitted!")
        out = open(c.path, "a")

    else:
        try:
            image = False
            html = False
            info = [("images", entries)]
            c.path = c.path.replace("/", "", 1)   # If data is present get rid of the first '/'
            contents = ""
            if "jpeg" in c.path or "jpg" in c.path:        # If an image is being requested take note of it and open it
                file = open(c.path, "rb")             # and open it as binary
                image = True
                file_size = getFileSize(c.path)
                message = response_builder(OK, "jpeg", file_size)
                client.sendall(message.encode('utf-8'))
                message = file.read()
                file.close()
            elif "html" in c.path:                                       # If it is a normal file just open it
                file = open(c.path, "r")
                contents = build_html(file.read(), info)
                html = True
            else:
                file = open(c.path, "r")
                contents = file.read()
                if ".txt" in c.path:
                    contents = contents.replace("&", "&amp")
                    contents = contents.replace("<", "&lt")
                    contents = contents.replace(">", "&gt")

            if not image:
                file_size = len(contents)            # Get the size of the contents of the file
                message = response_builder(OK, c.path.split(".")[1], file_size)  # Call response_builder to create response
                message += contents

        except FileNotFoundError:                  # If no file can be found send a 404
            print("File requested could not be found sending 404!\n")
            c.path = "front_end/view/404.html"
            file = open(c.path, "r")
            file_size = getFileSize(c.path)
            message = response_builder(NOT, c.path.split(".")[1], file_size)
            message += file.read()
            file.close()
    # Send message to the client
    if image:
        client.sendall(message)
    else:
        client.sendall(message.encode('utf-8'))

    # Close the connection to the client
    client.close()

