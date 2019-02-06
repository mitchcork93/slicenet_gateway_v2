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
import Tkinter as tk
import PIL.Image, PIL.ImageTk
import tkMessageBox
import random


class MyClientProtocol(WebSocketClientProtocol):

    def __init__(self):
        WebSocketClientProtocol.__init__(self)
        self.capture_thread = None
        self.isComplete = False
        self.isCapturing = True
        self.mode = "IDENT"
        self.cam1 = None
        self.cam2 = None

        self.cap = cv2.VideoCapture(1)
        self.window = tk.Tk()
        self.window.title("SliceNet Diagnostic v1.0")
        self.window.configure(bg="white")
        self.window.resizable(0,0)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):

        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            self.window.destroy()
            if self.cap.isOpened():
                self.cap.release()
            self.sendClose()

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        ret, first_frame = self.cap.read()
        self.height, self.width, channels = first_frame.shape
        self.baseframe = tk.Frame(self.window,bg="white")
        self.baseframe.pack()
        self.firstscreen = tk.Frame(self.baseframe,bg="white")
        self.firstscreen.pack()
        self.secondscreen = tk.Frame(self.baseframe,bg="white")

        m1 = tk.PanedWindow(self.firstscreen,bg="white")
        self.m2 = tk.PanedWindow(m1, orient=tk.VERTICAL,bg="white")
        m1.pack(fill=tk.BOTH, expand=0)
        m1.add(self.m2)

        windowwidth = self.width
        windowheigh = self.height * 1.3
        self.center_window(self.window, windowwidth, windowheigh)

        self.camera_area = tk.PanedWindow(self.m2, orient=tk.HORIZONTAL,bg="white")
        self.m2.add(self.camera_area)
        self.camera0_area = tk.Frame(self.camera_area,bg="white")
        self.camera0_area.pack(side="left")
        self.camera = tk.Canvas(self.camera0_area, width=self.width, height=self.height,bg="white")
        self.camera.pack()

        # this is the right side of the box
        self.camera1_area = tk.Frame(self.camera_area,bg="white")
        self.camera1_area.pack()
        self.camera1 = tk.Canvas(self.camera1_area, width=self.width, height=self.height,bg="white")
        self.camera1.pack()
        self.baseline = tk.PanedWindow(self.secondscreen, orient=tk.HORIZONTAL,bg="white")
        self.baseline.pack()

        PRframe = tk.PanedWindow(self.baseline,bg="white",orient=tk.VERTICAL)
        self.baseline.add(PRframe)
        namezone= tk.PanedWindow(PRframe, orient=tk.HORIZONTAL,bg="white")
        PRframe.add(namezone)
        name = tk.Label(namezone, text="Patient detected :", bg="white", font=('Arial', 20, 'bold'))
        namezone.add(name)
        self.name1 = tk.Label(namezone, text="Name", bg="white", anchor="w", font=('Arial', 20))
        namezone.add(self.name1)

        recordzone= tk.PanedWindow(PRframe, orient=tk.HORIZONTAL,bg="white")
        PRframe.add(recordzone)
        self.PR = tk.PanedWindow(recordzone, orient=tk.VERTICAL,bg="white")
        recordzone.add(self.PR)
        self.pr = tk.PanedWindow(self.PR, orient=tk.VERTICAL, bg="white")
        self.PR.add(self.pr)
        pr2 = tk.PanedWindow(self.pr, orient=tk.HORIZONTAL, bg="white")
        self.pr.add(pr2)
        age = tk.Label(pr2, text="Age :", bg="white", font=('Arial', 11,'bold'))
        pr2.add(age)
        self.age1 = tk.Label(pr2, text="Age", bg="white",anchor="w",font=('Arial', 11))
        pr2.add(self.age1)
        pr3 = tk.PanedWindow(self.pr, orient=tk.HORIZONTAL, bg="white")
        self.pr.add(pr3)
        sex = tk.Label(pr3, text="Gender :", bg="white", font=('Arial', 11,'bold'))
        pr3.add(sex)
        self.sex1 = tk.Label(pr3, text="Gender", bg="white",anchor="w",font=('Arial', 11))
        pr3.add(self.sex1)

        pr_2 = tk.PanedWindow(self.PR, orient=tk.VERTICAL,bg="white")
        self.PR.add(pr_2)
        pr_21 = tk.PanedWindow(pr_2, orient=tk.HORIZONTAL,bg="white")
        pr_2.add(pr_21)
        dob = tk.Label(pr_21, text="Date :",bg="white",font=('Arial', 11,'bold'))
        pr_21.add(dob)
        dob1 = tk.Label(pr_21, text="1.17.2019",bg="white",anchor="w",font=('Arial', 11))
        pr_21.add(dob1)
        pr_22 = tk.PanedWindow(pr_2, orient=tk.HORIZONTAL,bg="white")
        pr_2.add(pr_22)
        reg = tk.Label(pr_22, text="Reg. No :",bg="white",font=('Arial', 11,'bold'))
        pr_22.add(reg)
        reg1 = tk.Label(pr_22, text="123456789",bg="white",anchor="w",font=('Arial', 11))
        pr_22.add(reg1)
        pr_23 = tk.PanedWindow(pr_2, orient=tk.HORIZONTAL,bg="white")
        pr_2.add(pr_23)
        status = tk.Label(pr_23, text="Health Status :",bg="white",font=('Arial', 11,'bold'))
        pr_23.add(status)
        status1 = tk.Label(pr_23, text="stable",bg="white",anchor="w",font=('Arial', 11))
        pr_23.add(status1)
        pr_3 = tk.PanedWindow(self.PR, orient=tk.VERTICAL,bg="white")
        self.PR.add(pr_3)

        def swich():
            swith=str(var.get())
            if swith=="1":
                self.camera.pack()
                self.camera1.pack()
            elif swith=="2":
                self.camera1.forget()
                self.camera.pack()
            elif swith == "3":
                self.camera.forget()
                self.camera1.pack()

        var = tk.IntVar()
        R1 = tk.Radiobutton(pr_3, text="Show both screens", variable=var, value=1, command=swich,bg="white",font=('Arial', 12))
        R1.pack(anchor="w")
        R1.select()
        R2 = tk.Radiobutton(pr_3, text="Show only live stream", variable=var, value=2,command=swich,bg="white",font=('Arial', 12))
        R2.pack(anchor="w")
        R3 = tk.Radiobutton(pr_3, text="Show only ML processed stream", variable=var, value=3,command=swich,bg="white",font=('Arial', 12))
        R3.pack(anchor="w")

        PR1 = tk.PanedWindow(recordzone, orient=tk.VERTICAL,bg="white")
        # PR1.pack(side="top")
        recordzone.add(PR1)
        weightzone = tk.PanedWindow(PR1, orient=tk.HORIZONTAL, bg="white")
        PR1.add(weightzone)
        weight = tk.Label(weightzone, text="Weight :", bg="white", font=('Arial', 11, 'bold'))
        weightzone.add(weight)
        self.weight1 = tk.Label(weightzone, text="Weight", bg="white",anchor="w",font=('Arial', 11))
        weightzone.add(self.weight1)

        heightzone = tk.PanedWindow(PR1, orient=tk.HORIZONTAL, bg="white")
        PR1.add(heightzone)
        height = tk.Label(heightzone, text="Height :", bg="white", font=('Arial', 11, 'bold'))
        heightzone.add(height)
        self.height1 = tk.Label(heightzone, text="Weight", bg="white",anchor="w",font=('Arial', 11))
        heightzone.add(self.height1)

        bmizone = tk.PanedWindow(PR1, orient=tk.HORIZONTAL, bg="white")
        PR1.add(bmizone)
        bmi = tk.Label(bmizone, text="BMI :", bg="white", font=('Arial', 11, 'bold'))
        bmizone.add(bmi)
        self.bmi1 = tk.Label(bmizone, text="BMI", bg="white",anchor="w",font=('Arial', 11))
        bmizone.add(self.bmi1)

        temperaturezone = tk.PanedWindow(PR1, orient=tk.HORIZONTAL, bg="white")
        PR1.add(temperaturezone)
        temperature = tk.Label(temperaturezone, text="Temperature :", bg="white", font=('Arial', 11, 'bold'))
        temperaturezone.add(temperature)
        self.temperature1 = tk.Label(temperaturezone, text="Temperature", bg="white",anchor="w",font=('Arial', 11))
        temperaturezone.add(self.temperature1)

        heartratezone = tk.PanedWindow(PR1, orient=tk.HORIZONTAL, bg="white")
        PR1.add(heartratezone)
        heartrate = tk.Label(heartratezone, text="Heart Rate :", bg="white", font=('Arial', 11, 'bold'))
        heartratezone.add(heartrate)
        self.heartrate1 = tk.Label(heartratezone, text="Heart Rate", bg="white",anchor="w",font=('Arial', 11))
        heartratezone.add(self.heartrate1)

        block = tk.PanedWindow(PR1, orient=tk.HORIZONTAL, bg="white",height=50)
        PR1.add(block)

        imageblock=tk.PanedWindow(self.baseline,orient=tk.VERTICAL,bg="white",width=20)
        self.baseline.add(imageblock)

        self.patientID=tk.PanedWindow(self.baseline,orient=tk.VERTICAL,bg="white")
        self.baseline.add(self.patientID)
        idLabel = tk.Label(self.patientID, text="Patient Photo ID", font=('Arial', 10, 'bold'),bg="white",anchor="w")
        self.patientID.add(idLabel)

        imageblock1=tk.PanedWindow(self.baseline,orient=tk.VERTICAL,bg="white",width=20)
        self.baseline.add(imageblock1)

        showdata=tk.PanedWindow(self.baseline,orient=tk.VERTICAL,bg="white")
        self.baseline.add(showdata)
        title = tk.Label(text="Patient Charts", font=('Arial', 10, 'bold'),bg="white" )
        showdata.add(title)

        charts = tk.PanedWindow(showdata, orient=tk.HORIZONTAL,bg="white")
        showdata.add(charts)

        neck = tk.PhotoImage(file="images/neck250.gif")
        neckxray = tk.Label(image=neck,bg="white")
        neckxray.photo=neck
        charts.add(neckxray)

        mri = tk.PhotoImage(file="images/mri.gif")
        mriscan = tk.Label(image=mri,bg="white")
        mriscan.photo=mri
        charts.add(mriscan)

        def run():
            try:
                while self.isCapturing:

                    ret, frame = self.cap.read()

                    if frame is not None:
                        frame1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        self.cam1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame1))
                        self.update()
                        self.window.iconbitmap("images/favicon.ico")

                sys.exit()

            except Exception as e:
                print e

        self.capture_thread = thread.start_new_thread(run, ())
        self.sendMessage(json.dumps({"type": "init", "mode": "identify"}))

    def transmit(self, mode):

        try:
            ret, frame = self.cap.read()

            if frame is not None:
                cv2.imencode('.jpg', frame, self.encode_param)

                try:
                    self.sendMessage(json.dumps({"type": "image", "payload": cPickle.dumps(frame), "mode": mode}))
                except Exception as e:
                    print e

            else:
                print 'ERROR: encoding image'
                self.transmit(mode)

        except Exception as e:
            print e

    def onMessage(self, payload, isBinary):

        try:
            data = json.loads(payload)

            if data["mode"] == "identify":

                if data.has_key("ERROR"):
                    print data["ERROR"]

                if data["type"] == "patient":

                    self.name1.configure(text=data["name"])
                    self.age1.configure(text=data["age"])
                    self.sex1.configure(text=data["sex"])
                    self.weight1.configure(text=data["weight"])
                    self.height1.configure(text=data["height"])
                    self.bmi1.configure(text=data["bmi"])

                    try:
                        cv_image = np.asanyarray(cPickle.loads(str(data["image"])))
                        frame = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
                        resized = cv2.resize(frame, (120, 160), interpolation=cv2.INTER_LINEAR)
                        idimage = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(resized))

                    except Exception as e:
                        print 'ERROR WITH PATIENT IMAGE - {}'.format(e)
                        image = PIL.Image.open("images/obama.jpg")
                        idimage = PIL.ImageTk.PhotoImage(image)

                    patientid = tk.Label(image=idimage, bg="white")
                    patientid.photo = idimage
                    self.patientID.add(patientid)

                    self.center_window(self.window, self.width * 2, self.height * 1.6)
                    self.secondscreen.pack()

                    self.mode = "DIAG"
                    self.sendMessage(json.dumps({"type": "init", "mode": "diagnostic"}))

                elif data["type"] == "get_image":
                    self.transmit(data["mode"])

            elif data["mode"] == "diagnostic":

                if data["type"] == "get_image":
                    self.transmit(data["mode"])

                if data["type"] == "receive_image":

                    cv_image = np.asanyarray(cPickle.loads(str(data["payload"])))
                    frame1 = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
                    self.cam2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame1))
                    self.transmit(data["mode"])

        except Exception as e:
            print e

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        exit(0)

    def center_window(self, root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(size)

    def update(self):

        if self.mode == "IDENT":
            try:
                self.camera.create_image(0, 0, image=self.cam1, anchor=tk.NW)
            except Exception as e:
                print e

        else:
            try:
                self.camera.create_image(0, 0, image=self.cam1, anchor=tk.NW)
                self.camera1.create_image(0, 0, image=self.cam2, anchor=tk.NW)

                """
                    Used to update the temperature / heart rate readings every now and again. Looks a bit jumpy
                    to update them constantly. Can be customized by removing the condition or expanding range
                """

                randNum1 = random.randint(1, 10)
                randNum2 = random.randint(1, 10)

                if randNum1 == 1:
                    self.temperature1.configure(text=str(random.randint(36, 38)))
                if randNum2 == 1:
                    self.heartrate1.configure(text=str(random.randint(60, 63)))

            except Exception as e:
                print e

        self.window.update()


if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    root.addHandler(ch)

    factory = WebSocketClientFactory(u"ws://127.0.0.1:8888/get")
    proto = MyClientProtocol
    factory.protocol = proto
    factory.setProtocolOptions(autoPingInterval=10, autoPingTimeout=60, openHandshakeTimeout=30)

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 8888)

    loop.run_until_complete(coro)
    loop.run_forever()
