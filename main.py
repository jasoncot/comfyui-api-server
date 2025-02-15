from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from myserver import MyServer

hostName = "0.0.0.0"
serverPort = 8041

def main():
    # this is a main here
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

if __name__ == "__main__":
    main()
