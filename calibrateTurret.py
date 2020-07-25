# Turret Calibration

from PIL import Image, ImageTk
import tkinter as tk
import argparse
import time
import datetime
import cv2
import os
import re
import subprocess
import urllib
import RPi.GPIO as GPIO
import threading
import picamera
import copy
import math
import signal
from functools import partial
from WaterTurret import WaterTurret
from plane3Points import plane3Points
from Point import Point
from turretPoint import turretPoint


info = '''\n- Press Left Mouse key to set a new Point.\n
- Press Right Mouse key to toggle the Pump.\n
- keyboard key\n
    <left>,<right>,<up>,<down> Move turret.
    <enter> Validate Point.
    <del>   Clear all points.
    <F1>    Reload points from 'turretTabe.cfg'.\n
- All turret points are store in turretTable.cfg file.\n
- After three points the turret will try to move itself.\n
- Add points to increase the resolution.\n
- Any new point near 10 pixels removes old one.\n

© D.J.Perron July,2020   GNU GPL 2.0'''


def do_picamera(app):
    camera = picamera.PiCamera()
    camera.brightness = 50
    camera.resolution = (1280, 720)
    data = time.strftime("%Y-%b-%d_(%H%M%S)")
    texte = "picture take:" + data
    camera.start_preview()
    camera.capture('%s.jpg' % data)
    camera.stop_preview()


class Application:
    def __init__(self, output_path="./"):
        """ Initialize application which uses OpenCV + Tkinter.
            It displays a video stream in a Tkinter window and
            stores current snapshot on disk """
        # capture video frames, 0 is your default video camera
        self.vs = cv2.VideoCapture(0)
        self.vs.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
        self.vs.set(cv2.CAP_PROP_FRAME_HEIGHT, 576)
        # current image from the camera
        self.current_image = None
        # initialize root window
        self.root = tk.Tk()
        # set de default grey color to use in labels background
        defaultbg = self.root.cget('bg')
        w = 1400  # width for the Tk root
        h = 600  # height for the Tk root
        self.root .resizable(0, 0)
        ws = self.root .winfo_screenwidth()  # width of the screen
        hs = self.root .winfo_screenheight()  # height of the screen
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.root.title(" Turret Adjustment  ")  # set window title
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.bind('<Up>', partial(self.MoveTurretEvent, x=0, y=1))
        self.root.bind('<Down>', partial(self.MoveTurretEvent, x=0, y=-1))
        self.root.bind('<Left>', partial(self.MoveTurretEvent, x=-1, y=0))
        self.root.bind('<Right>', partial(self.MoveTurretEvent, x=1, y=0))
        self.root.bind('<Return>', self.AddTurretPoint)
        self.root.bind('<Delete>', self.RemoveTurretPoints)
        self.root.bind('<F1>', self.ReloadTurretPoints)

        self.Pump = False
        self.Target = None
        self.CurrentTurret = Point(90, 90)
        self.ActualTurret = None
        self.MousePosition = None

        # panel is the image view
        # assuming 1024x576   16:9 ratio

        self.turretpoint = turretPoint(1024, 576, 10)
        self.turretpoint.Load()
        self.turretpoint.Save(filename="turret_old_Table.cfg")
        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.grid(row=0, rowspan=3, column=0,
                        columnspan=1, padx=0, pady=0)
        self.panel.bind('<Button-1>', self.MouseLeftPress)
        self.panel.bind('<Button-3>', self.MouseRightPress)

        self.panelInfo = tk.Label(self.root, text=info, anchor="w",
                                  justify='left',
                                  font=('arial narrow', 14, 'normal'))
        self.panelInfo.grid(row=2, column=1)

        self.TurretLabel = tk.Label(self.root,
                                    text="Turret (     ,     )", anchor="w",
                                    font=('arial narrow', 16, 'bold'))
        self.TurretLabel.grid(row=0, column=1)

        self.MouseLabel = tk.Label(self.root,
                                   text="Point  (     ,     )", anchor="w",
                                   font=('arial narrow', 16, 'bold'))
        self.MouseLabel.grid(row=1, column=1)

        self.video_loop()

        self.TurretCtrl = WaterTurret(Port='/dev/rfcomm1')
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):
        # print("got signal handler")
        self.root.quit()

    def RemoveTurretPoints(self, event):
        self.turretpoint.Table = []

    def ReloadTurretPoints(self, event):
        self.Target=  None
        self.turretpoint.Load()

    def MoveTurretEvent(self, event, x, y):
        if self.ActualTurret is None:
           self.ActualTurret = Point(80, 80)
        self.ActualTurret.x = self.ActualTurret.x + x
        self.ActualTurret.y = self.ActualTurret.y + y
        self.MoveTurret(self.ActualTurret.x, self.ActualTurret.y)

    def MoveTurret(self, x, y):
        if self.ActualTurret is None:
            self.ActualTurret = Point(90, 90)
        if self.ActualTurret.x < 0:
            self.ActualTurret.x = 0
        if self.ActualTurret.y < 0:
            self.ActualTurret.y = 0
        if self.ActualTurret.x > 180:
            self.ActualTurret.x = 180
        if self.ActualTurret.y > 180:
            self.ActualTurret.y = 180
        self.TurretCtrl.xy(self.ActualTurret.x, self.ActualTurret.y)
        self.TurretLabel.configure(text="Turret ({:4d},{:4d})".format(
                                   self.ActualTurret.x,
                                   self.ActualTurret.y))

    def DrawRectangle(self, img, xy, col):
        img = cv2.rectangle(img, (xy.x-5, xy.y-5), (xy.x+5, xy.y+5), col, 1)
        return img

    def DrawTarget(self, img):
        if self.Target:
            img = self.DrawRectangle(img, self.Target, (0, 0, 255))
        for i in self.turretpoint.Table:
            p = Point(i[0], i[1])
            img = self.DrawRectangle(img, p, (255, 0, 0))
        return img

    def MouseRightPress(self, event):
        self.Pump = not self.Pump
        self.TurretCtrl.pump(self.Pump)

    def MouseLeftPress(self, event):
        self.Target = Point(event.x, event.y)
        self.MouseLabel.configure(text="Point ({:4d},{:4d})".format(
                                  self.Target.x, self.Target.y))
        BestPoint = self.turretpoint.Find(self.Target)
        if BestPoint is None:
            return
        if self.ActualTurret is None:
            self.ActualTurret = Point(90, 90)
        # print("Best Point from ({},{}) is ({},{})".format(
        #                        self.Target.x, self.Target.y,
        #                        BestPoint.x, BestPoint.y))
        self.ActualTurret.x = BestPoint.x
        self.ActualTurret.y = BestPoint.y
        self.MoveTurret(self.ActualTurret.x, self.ActualTurret.y)

    def AddTurretPoint(self, event):
        if self.ActualTurret is None:
            return
        if self.Target is None:
            return
        self.CurrentTurret = copy.deepcopy(self.ActualTurret)
        self.turretpoint.Add(self.Target, self.CurrentTurret)
        self.Target = None

    def video_loop(self):
        global test
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            frame = self.DrawTarget(frame)
            # convert colors from BGR to RGBA
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            # convert image for PIL
            self.current_image = Image.fromarray(cv2image)
            # convert image for tkinter
            imgtk = ImageTk.PhotoImage(image=self.current_image)
            test = cv2image
            # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.imgtk = imgtk
            # show the image
            self.panel.config(image=imgtk)
        # call the same function after 30 milliseconds
        self.root.after(30, self.video_loop)

    def destructor(self):
        self.turretpoint.Save()
        self.root.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application
        self.TurretCtrl.off()
        self.TurretCtrl.pump(False)


# start the app
Calib_app = Application()

Calib_app.root.mainloop()

