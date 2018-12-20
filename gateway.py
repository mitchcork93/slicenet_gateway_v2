from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory
import trollius as asyncio
from twisted.logger import globalLogBeginner, textFileLogObserver
import pyrealsense2 as rs
import numpy as np
import cv2
import cPickle
import sys
import logging
import thread
import json
import time


class MyClientProtocol(WebSocketClientProtocol):

    def __init__(self):
        WebSocketClientProtocol.__init__(self)
        self.capture_thread = None
        self.isComplete = False

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
		
		"""
			you might need to edit the parameter inside cv2.VideoCapture(1) to either 0 or higher than one
		"""
		
        self.cap = cv2.VideoCapture(1)

        def run():
            try:
                while True:

                    ret, frame = self.cap.read()

                    if frame is not None:
                        cv2.imencode('.jpg', frame, self.encode_param)

                        # Render images
                        cv2.namedWindow('Telestroke Assessment v1.0', cv2.WINDOW_AUTOSIZE)
                        cv2.imshow('Telestroke Assessment v1.0', frame)
                        cv2.waitKey(1)

                cap.release()
                cv2.destroyAllWindows()

            except Exception as e:
                print e

        self.capture_thread = thread.start_new_thread(run,())
        self.sendMessage(json.dumps({"type": "init", "mode": "identify"}))

    def transmit(self, mode):

        try:
            ret, frame = self.cap.read()
            cv2.imencode('.jpg', frame, self.encode_param)
        except Exception as e:
            print e

        try:
            self.sendMessage(json.dumps({"type": "image", "payload": cPickle.dumps(frame), "mode": mode}))
        except Exception as e:
            print e

        self.cam.release()

    def onMessage(self, payload, isBinary):

        try:
            data = json.loads(payload)

            if data["mode"] == "identify":

                if data.has_key("ERROR"):
                    print data["ERROR"]

                if data["type"] == "patient":
                    print data
                    self.sendMessage(json.dumps({"type": "init", "mode": "diagnostic"}))

                elif data["type"] == "get_image":
                    self.transmit(data["mode"])

            elif data["mode"] == "diagnostic":

                if data["type"] == "get_image":
                    self.transmit(data["mode"])

                if data["type"] == "receive_image":

                    cv_image = np.asanyarray(cPickle.loads(str(data["payload"])))

                    cv2.namedWindow('Diagnostics', cv2.WINDOW_AUTOSIZE)
                    cv2.imshow('Diagnostics', cv_image)
                    cv2.waitKey(1)

                    self.transmit(data["mode"])
        except:
            pass

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        exit(0)


if __name__ == '__main__':

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    root.addHandler(ch)

    factory = WebSocketClientFactory(u"ws://127.0.0.1:8888/get")
    factory.protocol = MyClientProtocol
    factory.setProtocolOptions(autoPingInterval=1, autoPingTimeout=10, openHandshakeTimeout=30)

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 8888)
    loop.run_until_complete(coro)
    loop.run_forever()
