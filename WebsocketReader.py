
import time
import json
from threading import Lock, Thread
from lomond import WebSocket

class YerFaceWebsocketReader:
    def __init__(self, uri):
        self.packets = None
        self.packetsLock = Lock()
        self.websocket = None
        self.thread = None
        self.running = False
        self.uri = uri
        print("YerFaceWebsocketReader initialized with URI: ", self.uri)
    def openWebsocket(self):
        self.packets = []
        self.running = True
        self.thread = Thread(target=self.runWebsocketThread)
        self.thread.start()
    def closeWebsocket(self):
        self.running = False
        self.websocket.close()
        self.thread.join()
        self.thread = None
        self.websocket = None
    def runWebsocketThread(self):
        attempt = 0
        while self.running:
            if attempt > 0:
                time.sleep(0.25)
            attempt = attempt + 1
            self.websocket = WebSocket(self.uri)
            for event in self.websocket:
                if event.name == 'text':
                    packetObj = None
                    try:
                        packetObj = json.loads(event.text)
                    except:
                        print("Failed parsing a Websocket event as JSON: " + event.text)
                        continue
                    if packetObj == None:
                        print("Got a NULL event for some reason.")
                        continue
                    self.packetsLock.acquire()
                    self.packets.append(packetObj)
                    self.packetsLock.release()
                else:
                    if not self.running:
                        print("Websocket client thread exiting.")
                        return
    def returnNextPackets(self):
        self.packetsLock.acquire()
        copyPackets = list(self.packets)
        self.packetsLock.release()
        return copyPackets
