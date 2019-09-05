from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter.simpledialog
import numpy as np
import glob
import re
import csv
from Homography import Homography
import CSVManager




class FieldWindow(Frame):
    field_points = []
    image_points = []
    bboxes = []
    bboxesFrames = []
    idsFrames = []
    ids = []
    can = None
    btnCan = None
    nrPoints = None
    H = None
    image_list = []
    image_counter = 0
    bb_start = []
    bb_intermediate = []
    bb_end = []
    #sindys
    BBcounter = 0
    savedBBs=[]
    bbcolor = []
    #
    image = None
    scale = 1.0
    currentImage = None
    textentryid = None
    folder_loaded = False
    detecthomography = False
    bindidimageclick = None
    bindidhomographyclick = None
    isBBox = False
    fps = 25
    homographyPointsIDs = []
    csv = None
    rectangles = []
    currentRectangle = None
    savedRectangle = False
    defaultConfidence = 1.0
    confidences = []
    allConfidences = []
    iddict = {
        'Black-Red':1, 'Black-Green':2, 'Black-Blue':3, 'Black-Yellow':4, 'Black-Pink':5, 'White-Red':6, 'White-Green':7,
        'White-Blue':8, 'White-Yellow':9, 'White-Pink':0, 'Ball':10, 'Unknown':None
    }
    iddictreverse = {
        1:'Black-Red', 2:'Black-Green', 3:'Black-Blue', 4:'Black-Yellow', 5:'Black-Pink', 6:'White-Red', 7:'White-Green',
        8:'White-Blue', 9:'White-Yellow', 0:'White-Pink', 10:'Ball', 11:'Unknown'
    }

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        # variables
        self.field_points = []
        self.image_points = []
        self.can = None
        self.image_can = None
        self.nrPoints = None
        self.H = None
        #colors for bbs
        self.bbcolor = ['snow',\
            'red3','green3','blue2','gold2','DeepPink3',\
            'tomato','green yellow','deep sky blue','yellow','hot pink',\
            'gray20']
        #self.bbcolor = ['#003FFF','#0000FF','#5F00FF','#BF00FF','#FF00FE','#FF00BF','#FF007F','#FF003F','#FF0000','#FF3F00','#FF9F00','#DFFF00']
        #003FFF#001FFF#0000FF#3F00FF#5F00FF#7F00FF #BF00FF#DF00FF#FF00FE#FF00DF#FF00BF#FF009F#FF007F#FF005F#FF003F#FF001F
        #FF0000#FF1F00 #FF3F00#FF7F00 #FF9F00#FFBF00 #FFDF00#DFFF00
        self.BBcounter = 0
        self.savedBBs=[]
        # size of the window
        self.master.geometry("1400x750")
        self.init_window()
        self.centerWindow()
        # init point lists

    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("Frame processing")
        # set key listener
        self.master.bind('<Left>', self.leftKey)
        self.master.bind('<Right>', self.rightKey)
        for i in range(10):
            self.master.bind(str(i), self.numberKey)
        self.master.bind('<b>', self.bKey)
        self.master.bind('<s>', self.saveBBox)
        self.master.bind('+', self.__next_BB)
        self.master.bind('-', self.__BB_before)
        self.master.bind('<Key>', self.__set_Lbl)
        self.pack(fill=BOTH, expand=1)
        # button canvas
        self.btnCan = Canvas(self, height=20, width=1400)
        lbl = Label(self.btnCan, text="Number of matched points:")
        lbl.pack(side=LEFT, padx=40)
        self.nrPoints = Label(self.btnCan, text="0", width=20)
        self.nrPoints.pack(side=LEFT)
        startCalc = Button(self.btnCan, text="Start Homography Calculation", command=self.startCalculation)
        startCalc.pack(side=RIGHT, padx=40)
        buttonsaveid=Button(self.btnCan, text="Save", command=self.saveBoundingBoxID)
        buttonsaveid.pack(side=RIGHT, padx=5)
        self.bbs=[]
        #self.textentryid = Entry(btnCan)
        #self.textentryid.pack(side=RIGHT, padx=5)

        # Create a Tkinter variable
        self.textentryid = StringVar(self.btnCan)

        # Dictionary with options
        choices = {'Black-Red', 'Black-Green', 'Black-Blue', 'Black-Yellow', 'Black-Pink','White-Red','White-Green','White-Blue', 'White-Yellow', 'White-Pink', 'Ball', 'Unknown'}
        self.textentryid.set('None')  # set the default option

        popupMenu = OptionMenu(self.btnCan, self.textentryid, *choices)
        popupMenu.pack(side=RIGHT, padx=5)
        id = Label(self.btnCan, text="ID")
        id.pack(side=RIGHT, padx=5)
        self.btnCan.pack(fill=BOTH)

        # canvas for image
        imageCan = Canvas(self, height=700, width=1000)
        imageCan.pack(fill=BOTH, expand=1, side=LEFT)
        self.image_can = imageCan

        # canvas for field
        fieldCan = Canvas(self, bg="white", height=700, width=400)
        fieldCan.place(relx=1.0, rely=1.0)
        fieldCan.pack(fill=BOTH, expand=1, side=RIGHT)
        self.can = fieldCan

        # load field
        self.load_field(fieldCan)
        self.mark_points(fieldCan)

        self.init_menu(imageCan, fieldCan)


    def init_menu(self, imageCan, fieldCan):
        # creating a menu instance
        menu = Menu(self.master)
        self.master.config(menu=menu)

        # file menue entry
        folder = Menu(menu)
        folder.add_command(label="Open Folder", command=lambda: self.load_folder(imageCan))
        #folder.add_command(label="Load Bounding Boxes File", command=lambda: self.load_BBs(imageCan))
        folder.add_separator()
        folder.add_command(label="Next image", command=lambda: self.load_next_image(imageCan))
        folder.add_command(label="Save results", command=lambda: self.save_results())
        menu.add_cascade(label="Folder", menu=folder)

        homographymenu = Menu(menu)
        homographymenu.add_command(label="Insert points",command=lambda: self.enterHPoints())
        homographymenu.add_command(label="Stop inserting points", command=lambda: self.processFrames())
        menu.add_cascade(label="Homography", menu=homographymenu)

    def centerWindow(self):
        # Gets the requested values of the height and width.
        windowWidth = 1400  # self.master.winfo_reqwidth()
        windowHeight = 800  # self.master.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        positionRight = int(self.master.winfo_screenwidth() / 2 - windowWidth / 2)
        positionDown = int(self.master.winfo_screenheight() / 2 - windowHeight / 2)

        # Positions the window in the center of the page.
        self.master.geometry("+{}+{}".format(positionRight, positionDown))

    def load_image(self, can):
        self.reset()
        # adding the image

    def load_folder(self, can):
        self.reset()
        self.folder_loaded = True
        # adding the image
        folder = askdirectory(parent=self, initialdir="./", title='Select a folder')
        files = glob.glob(folder + '/*')
        # search for BB File
        bbFile = [f for f in files if f.endswith("csv")]
        if len(bbFile)>0:
            bbFile = bbFile[0]
            print("CSV: "+bbFile)
            files = [f for f in files if not f.endswith("csv")]
        elif folder is not None:
            if messagebox.askokcancel(title="No bounding box file found", message="Do you want to choose a bounding box file on an other location?"):
                bbFile = askopenfilename(parent=self, initialdir="./", title="Choose a bounding box file")
        if bbFile is not None:
            self.__load_BBs(bbFile)

        self.image_list = files
        self.csv = CSVManager.CSV(folder)
        # sort images by number in name
        files = sorted(files, key=lambda x: float(re.findall("(\d+)", x)[-1]))
        print(files[0])
        if len(files) > 0:
            self.load_next_image(can)
        
    def __load_BBs(self, bbFile):
        # load file
        reader = csv.reader(open(bbFile, "r"), delimiter=",")
        x = list(reader)
        self.bbs = np.array(x)
        print("BBs: "+str(self.bbs.shape))

    def __draw_BBs(self, bbs):
        print("__draw_BBs")
        self.savedBBs = []
        for i in range(0,len(bbs),6):
            lbl = int(bbs[i])
            x = float(bbs[i+1])
            y = float(bbs[i+2])
            width = float(bbs[i+3])
            height = float(bbs[i+4])
            conf = int(float(bbs[i+5])*10)
            bbid = self.image_can.create_rectangle(x,y,x+width,y+height,outline=self.bbcolor[lbl],width=3)
            if lbl is not None and lbl!="":
                bblblid = self.image_can.create_text(x+15,y-15,text=lbl,fill=self.bbcolor[lbl],font='bold')
            else:
                bblblid = self.image_can.create_text(x+15,y-15,text="",fill=self.bbcolor[lbl],font='bold')
            
            # save bb for labeling 
            self.savedBBs.append([bbid,bblblid,[lbl,x,y,conf]])
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][0],outline='lightgreen')
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][1],fill='lightgreen')

    def __next_BB(self,event):
        lbl = self.savedBBs[self.BBcounter][2][0]
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][0],outline=self.bbcolor[lbl])
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][1],fill=self.bbcolor[lbl])
        self.BBcounter = (self.BBcounter+1)%len(self.savedBBs)
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][0],outline='lightgreen')
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][1],fill='lightgreen')
        
    def __BB_before(self,event):
        lbl = self.savedBBs[self.BBcounter][2][-1]
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][0],outline=self.bbcolor[lbl])
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][1],fill=self.bbcolor[lbl])
        self.BBcounter = (self.BBcounter-1)%len(self.savedBBs)
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][0],outline='lightgreen')
        self.image_can.itemconfig(self.savedBBs[self.BBcounter][1],fill='lightgreen')

    def __set_Lbl(self,event):
        if (event.keycode>=48 and event.keycode<=57):
            newText = self.savedBBs[self.BBcounter][2][0]+event.char
            self.savedBBs[self.BBcounter][2][0] = newText
            self.image_can.itemconfig(self.savedBBs[self.BBcounter][1],text=newText)
            if int(newText)>10:
                self.image_can.itemconfig(self.savedBBs[self.BBcounter][1],fill='red')  
            else:      
                self.image_can.itemconfig(self.savedBBs[self.BBcounter][1],fill='lightgreen')

        if event.keycode==8:
            newText = self.savedBBs[self.BBcounter][2][0][:-1]
            self.savedBBs[self.BBcounter][2][0] = newText
            self.image_can.itemconfig(self.savedBBs[self.BBcounter][1],text=newText)
        print(event.keycode)

    def load_next_image(self, can):
        if len(self.image_list) > 0 and self.image_counter < len(self.image_list):
            #self.reset()
            # adding the image
            if self.image_counter>0:
                self.bboxesFrames.append(self.bboxes)
                self.bboxes = []
                self.idsFrames.append(self.ids)
                self.ids = []
                self.allConfidences.append(self.confidences)
                self.confidences = []
            load = Image.open(self.image_list[self.image_counter])
            bb = self.bbs[self.image_counter][1:]
            self.image_counter +=1
            scale = 1.01
            #print(load.width)
            while load.width > 950 and load.height > 650:
                scale = scale - 0.01
                load = load.resize((int(load.width * scale), int(load.height * scale)))
            self.scale = scale
            render = ImageTk.PhotoImage(load)#tkinter.PhotoImage(load)
            #print(render.width())
            # labels can be text or images
            self.currentImage = load
            self.image_can.create_image(20,20, anchor=NW, image=render)
            self.__draw_BBs(bb)
            self.image_can.bind("<Button-1>", self.image_click_handler)
            self.image_can.bind("<B1-Motion>", self.image_drag_handler)
            self.image_can.bind("<ButtonRelease-1>", self.image_release_handler)
            self.image_can.imageList.append(render)

        elif self.image_counter >= len(self.image_list):
            tkinter.messagebox.showinfo("Last frame", "This was the last frame")



    def load_field(self, bg):
        # side lines
        bg.create_line(30, 30, 30, 680, width=5)
        bg.create_line(30, 30, 355, 30, width=5)
        bg.create_line(30, 680, 355, 680, width=5)
        bg.create_line(355, 30, 355, 680, width=5)
        # middle line
        bg.create_line(30, 355, 355, 355, width=2.5)
        # goal lines
        # up
        bg.create_line(131.5625, 30, 131.5625, 25, width=2.5)
        bg.create_line(131.5625, 25, 253.4375, 25, width=2.5)
        bg.create_line(253.4375, 25, 253.4375, 30, width=2.5)
        # down
        bg.create_line(131.5625, 680, 131.5625, 685, width=2.5)
        bg.create_line(131.5625, 685, 253.4375, 685, width=2.5)
        bg.create_line(253.4375, 685, 253.4375, 680, width=2.5)

    def mark_points(self, can):
        r = 5
        # upper line
        can.create_oval(30 - r, 30 - r, 30 + r, 30 + r, fill="red", activefill="yellow")
        #can.create_oval(131.5625 - r, 30 - r, 131.5625 + r, 30 + r, fill="red", activefill="yellow")
        #can.create_oval(253.4375 - r, 30 - r, 253.4375 + r, 30 + r, fill="red", activefill="yellow")
        can.create_oval(355 - r, 30 - r, 355 + r, 30 + r, fill="red", activefill="yellow")
        # bottom line
        can.create_oval(30 - r, 680 - r, 30 + r, 680 + r, fill="red", activefill="yellow")
        #can.create_oval(131.5625 - r, 680 - r, 131.5625 + r, 680 + r, fill="red", activefill="yellow")
        #can.create_oval(253.4375 - r, 680 - r, 253.4375 + r, 680 + r, fill="red", activefill="yellow")
        can.create_oval(355 - r, 680 - r, 355 + r, 680 + r, fill="red", activefill="yellow")
        # middle line
        can.create_oval(30 - r, 355 - r, 30 + r, 355 + r, fill="red", activefill="yellow")
        can.create_oval(355 - r, 355 - r, 355 + r, 355 + r, fill="red", activefill="yellow")

        can.bind("<Button-1>", self.point_handler)

    def reset(self):
        # variables
        self.field_points = []
        self.image_points = []
        # field
        self.load_field(self.can)
        self.mark_points(self.can)

    def near(self, p, o):
        if p > (o - 5) and p < (o + 5):
            return True

    def recolor_marker(self, x, y):
        r = 5
        # upper line
        if self.near(x, 30) and self.near(y, 30):
            self.can.create_oval(30 - r, 30 - r, 30 + r, 30 + r, fill="lightgreen")
            self.homographyPointsIDs.append(3)
        #if self.near(x, 131.5625) and self.near(y, 30):
        #    self.can.create_oval(131.5625 - r, 30 - r, 131.5625 + r, 30 + r, fill="lightgreen")
         #   self.homographyPointsIDs.append(1)
        #if self.near(x, 253.4375) and self.near(y, 30):
        #    self.can.create_oval(253.4375 - r, 30 - r, 253.4375 + r, 30 + r, fill="lightgreen")
         #   self.homographyPointsIDs.append(2)
        if self.near(x, 355) and self.near(y, 30):
            self.can.create_oval(355 - r, 30 - r, 355 + r, 30 + r, fill="lightgreen")
            self.homographyPointsIDs.append(0)
        # bottom line
        if self.near(x, 30) and self.near(y, 680):
            self.can.create_oval(30 - r, 680 - r, 30 + r, 680 + r, fill="lightgreen")
            self.homographyPointsIDs.append(5)
        #if self.near(x, 131.5625) and self.near(y, 680):
        #    self.can.create_oval(131.5625 - r, 680 - r, 131.5625 + r, 680 + r, fill="lightgreen")
         #   self.homographyPointsIDs.append(5)
        #if self.near(x, 253.4375) and self.near(y, 680):
        #    self.can.create_oval(253.4375 - r, 680 - r, 253.4375 + r, 680 + r, fill="lightgreen")
        #    self.homographyPointsIDs.append(6)
        if self.near(x, 355) and self.near(y, 680):
            self.can.create_oval(355 - r, 680 - r, 355 + r, 680 + r, fill="lightgreen")
            self.homographyPointsIDs.append(4)
        # bottom line
        if self.near(x, 30) and self.near(y, 355):
            self.can.create_oval(30 - r, 355 - r, 30 + r, 355 + r, fill="lightgreen")
            self.homographyPointsIDs.append(2)
        if self.near(x, 355) and self.near(y, 355):
            self.can.create_oval(355 - r, 355 - r, 355 + r, 355 + r, fill="lightgreen")
            self.homographyPointsIDs.append(1)
        print(self.homographyPointsIDs)

    def startCalculation(self):
        if len(self.image_points) == len(self.field_points) and len(self.image_points) >= 3:
            print("START CALCULATION")
            calc = Homography()#HomographyCalculation(self.image_points, self.field_points)
            homographyRet = calc.calcHomography(self.image_points, self.homographyPointsIDs)
            if homographyRet == -1:
                tkinter.messagebox.showinfo("Homography error", "Less than 3 points chosen for homography. Please add more")
            if homographyRet == -2:
                tkinter.messagebox.showinfo("Homography error", "Chosen points are on one line. Please add perpendicular point")
            #calc.startCalculation()

            self.H = calc
            self.testHomography()
            #self.save_H()
            tkinter.messagebox.showinfo("Calculation finished.",
                                        "Calculated Homography")
        else:
            tkinter.messagebox.showinfo("Calculation not possible", "Not enough points marked for calculation.")
        if len(self.savedBBs)>0 and self.H is not None and self.H.homography is not None:
            points = []
            for bbs in self.savedBBs:
                lbl = int(bbs[-1][0])
                x = bbs[-1][1]
                y = bbs[-1][2]
                points.append([x,y])
                p = self.H.transformPoint(np.array([[x,y]],dtype=float).reshape((-1, 1, 2)))
                x_ = 355-(p[0,0,0]*355/2000)+30
                y_ = (p[0,0,1]*355/2000)+30
                self.can.create_text(x_,y_,text=lbl,fill=self.bbcolor[lbl])

    def homography_click_handler(self, event):
        # print('position: x='+str(event.x)+", y="+str(event.y))
        x, y= event.x, event.y
        self.image_points.append([event.x, event.y])
        self.image_can.create_oval(x-3 , y-3, x+3, y+3, fill="lightgreen")
        # set number of matched points in frame
        self.nrPoints['text'] = str(min(len(self.image_points), len(self.field_points)))

    def image_click_handler(self, event):
        self.isBBox = False
        if not self.savedRectangle:
            self.image_can.delete(self.currentRectangle)
            self.currentRectangle = None
        self.savedRectangle = False
        # print('position: x='+str(event.x)+", y="+str(event.y))
        self.bb_start = [event.x, event.y]
        self.image_points.append([event.x, event.y])
        self.createBBox([self.bb_start[0], self.bb_start[1], self.bb_start[0], self.bb_start[1]])
        # set number of matched points in frame
        self.nrPoints['text'] = str(min(len(self.image_points), len(self.field_points)))

    def image_drag_handler(self, event):
        #print('drag position: x='+str(event.x)+", y="+str(event.y))
        #print(self.isBBox)
        self.bb_intermediate = [event.x, event.y]
        self.updateBBox([self.bb_start[0], self.bb_start[1], self.bb_intermediate[0], self.bb_intermediate[1]])
        #self.draw_bb()


    def image_release_handler(self, event):
        self.isBBox = True
        print('release position: x='+str(event.x)+", y="+str(event.y))
        self.bb_end = [event.x, event.y]
        self.updateBBox([self.bb_start[0],self.bb_start[1], self.bb_end[0], self.bb_end[1]])

    def createBBox(self, bb):
        self.currentRectangle = self.image_can.create_rectangle(bb[0], bb[1], bb[2], bb[3])

    def updateBBox(self, bb):
        if self.currentRectangle is not None:
            self.image_can.coords(self.currentRectangle, bb[0], bb[1], bb[2], bb[3])
    def draw_bb(self):
        self.image_can.create_image(20,20, anchor=NW, image=ImageTk.PhotoImage(self.currentImage))
        print(self.bboxes)
        for bb in self.bboxes:
            self.image_can.create_rectangle(bb[0], bb[1], bb[2], bb[3])
        self.image_can.create_rectangle(self.bb_start[0], self.bb_start[1], self.bb_intermediate[0], self.bb_intermediate[1])
    def saveBoundingBoxID(self):
        if self.isBBox:
            self.bboxes.append([self.bb_start[0],self.bb_start[1],self.bb_end[0],self.bb_end[1]])
            self.rectangles.append(self.currentRectangle)
            self.savedRectangle = True
            self.ids.append(self.iddict[self.textentryid.get()])
            print(self.ids)
            print(self.textentryid.get())
            self.textentryid.set('None')
            self.isBBox = False
            self.confidences.append(self.defaultConfidence)
        else:
            tkinter.messagebox.showinfo("No Bounding Box", "There is no bounding box to be saved")

    def testHomography(self):
        if self.H is not None:
            imageTransformed = self.H.transformImage(self.currentImage.transpose(Image.FLIP_LEFT_RIGHT))
            print(self.currentImage.size)
            print(imageTransformed.size)
            self.image_can.create_image(20,20, anchor=NW, image=ImageTk.PhotoImage(imageTransformed))
            imageTransformed.save("img2.png")
            #print(np.asarray(imageTransformed))


    def point_handler(self, event):
        x = round((event.x - 30) / 16.25, 2)
        y = round((event.y - 30) / 16.25, 2)
        # print('point: x='+str(x)+", y="+str(y))
        self.field_points.append([x, y])

        # set number of matched points in frame
        self.nrPoints['text'] = str(min(len(self.image_points), len(self.field_points)))

        # recolor circle
        self.recolor_marker(round(event.x, 1), round(event.y, 1))

    def enterHPoints(self):
        if self.folder_loaded:
            if self.bindidimageclick != None:
                self.image_can.unbind(self.bindidimageclick)
                self.bindidimageclick = None
            self.bindidhomographyclick = self.image_can.bind("<Button-1>", self.homography_click_handler)
            self.detecthomography = True
        else:
            tkinter.messagebox.showinfo("No folder", "No images available. Please load folder.")

    def processFrames(self):
        if self.folder_loaded:
            if self.bindidhomographyclick != None:
                self.image_can.undbind(self.bindidhomographyclick)
                self.bindidhomographyclick = None
            self.bindidimageclick = self.image_can.bind("<Button-1>", self.image_click_handler)

    def leftKey(self,event):
        print("Left key pressed")

    def rightKey(self, event):
        print("Right key pressed")
        if self.folder_loaded:
            self.saveFrame()
            self.load_next_image(self.image_can)

    def numberKey(self, event):
        print("pressed "+event.char)
        self.textentryid.set(self.iddictreverse[int(event.char)])

    def bKey(self, event):
        print("pressed b")
        self.textentryid.set(self.iddictreverse[10])

    def nKey(self, event):
        print("pressed n")
        self.textentryid.set(self.iddictreverse[11])

    def saveBBox(self):
        print("pressed s")
        self.saveBBox()

    def saveFrame(self):
        if self.csv is not None:
            self.csv.writeFrame(self.getTime(), self.ids, self.bboxes, self.confidences)

    def get_H(self):
        return self.H

    def get_image_points(self):
        return self.image_points

    def get_field_points(self):
        return self.field_points

    def save_H(self):
        f = open("Homography.txt", "w+")
        np.save("Homography.txt", self.H)

    def __client_exit(self):
        exit()

    def getTime(self):
        return float(self.image_counter)/float(self.fps)

    #def writeCSV(self, filename):


