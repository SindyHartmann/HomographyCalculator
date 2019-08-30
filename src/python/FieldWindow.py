from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
import tkinter.simpledialog

from . import HomographyCalculation

class FieldWindow(Frame):

    field_points=[]
    image_points=[]
    can = None
    nrPoints = None

    def __init__(self, master=None):
        Frame.__init__(self, master)               
        self.master = master
        # variables
        self.field_points=[]
        self.image_points=[]
        self.can = None   
        self.nrPoints = None     
        # size of the window
        self.master.geometry("1400x750")
        self.init_window()
        self.centerWindow()
        # init point lists

    #Creation of init_window
    def init_window(self):
        # changing the title of our master widget      
        self.master.title("Homography Calculator")
        self.pack(fill=BOTH, expand=1)

        # button canvas
        btnCan = Canvas(self,height=20, width=1400)
        lbl = Label(btnCan, text="Number of matched points:")
        lbl.pack(side=LEFT,padx=40)
        self.nrPoints = Label(btnCan, text="0", width=20)
        self.nrPoints.pack( side=LEFT)
        startCalc = Button(btnCan, text="Start Homography Calculation", command=self.startCalculation)
        startCalc.pack(side=RIGHT,padx=40)
        btnCan.pack(fill=BOTH)

        # canvas for image
        imageCan = Canvas(self, height=700, width=1000)
        imageCan.place(relx=1.0,rely=1.0)
        imageCan.pack(fill=BOTH, expand=1, side=LEFT)

        # canvas for field
        fieldCan = Canvas(self, bg="white", height=700, width=400)
        fieldCan.place(relx=1.0,rely=1.0)
        fieldCan.pack(fill=BOTH, expand=1, side=RIGHT)
        self.can = fieldCan

        # load field
        self.load_field(fieldCan)
        self.mark_points(fieldCan)

        self.init_menu(imageCan,fieldCan)
    
        
    def init_menu(self,imageCan,fieldCan):
        # creating a menu instance
        menu = Menu(self.master)
        self.master.config(menu=menu)

        # file menue entry
        file = Menu(menu)
        file.add_command(label="Open Image", command=lambda: self.load_image(imageCan))
        file.add_separator()
        file.add_command(label="Exit", command=self.client_exit)
        menu.add_cascade(label="File", menu=file)

        # edit menu entry
        #edit = Menu(menu)
        #edit.add_command(label="Undo")
        #menu.add_cascade(label="Edit", menu=edit)

    def centerWindow(self):
        # Gets the requested values of the height and widht.
        windowWidth = 1400#self.master.winfo_reqwidth()
        windowHeight = 800#self.master.winfo_reqheight()
        
        # Gets both half the screen width/height and window width/height
        positionRight = int(self.master.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(self.master.winfo_screenheight()/2 - windowHeight/2)
        
        # Positions the window in the center of the page.
        self.master.geometry("+{}+{}".format(positionRight, positionDown))

    def load_image(self,can):
        self.reset()
        #adding the image
        File = askopenfilename(parent=can, initialdir="./",title='Select an image')
        load = Image.open(File)
        load = load.resize((950,650)) #TODO nicht sinnvoll? oder Prozentual?
        render = ImageTk.PhotoImage(load)
        # labels can be text or images
        img = Label(self, image=render)
        img.image = render
        img.place(x=30, y=30)
        img.bind("<Button-1>",self.image_click_handler)

    def load_field(self,bg):
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
        can.create_oval(30-r, 30-r, 30+r, 30+r, fill="red", activefill="yellow")
        can.create_oval(131.5625-r, 30-r, 131.5625+r, 30+r, fill="red", activefill="yellow")
        can.create_oval(253.4375-r, 30-r, 253.4375+r, 30+r, fill="red", activefill="yellow")
        can.create_oval(355-r, 30-r, 355+r, 30+r, fill="red", activefill="yellow")
        # bottom line
        can.create_oval(30-r, 680-r, 30+r, 680+r, fill="red", activefill="yellow")
        can.create_oval(131.5625-r, 680-r, 131.5625+r, 680+r, fill="red", activefill="yellow")
        can.create_oval(253.4375-r, 680-r, 253.4375+r, 680+r, fill="red", activefill="yellow")
        can.create_oval(355-r, 680-r, 355+r, 680+r, fill="red", activefill="yellow")
        # middle line
        can.create_oval(30-r, 355-r, 30+r, 355+r, fill="red", activefill="yellow")
        can.create_oval(355-r, 355-r, 355+r, 355+r, fill="red", activefill="yellow")

        can.bind("<Button-1>", self.point_handler)

    def reset(self):
        # variables
        self.field_points=[]
        self.image_points=[]
        # field
        self.load_field(self.can)
        self.mark_points(self.can)


    def near(self,p,o):
        if p>(o-5) and p<(o+5):
            return True

    def recolor_marker(self, x, y):
        r = 5
        # upper line
        if self.near(x,30) and self.near(y,30):
            self.can.create_oval(30-r, 30-r, 30+r, 30+r, fill="lightgreen")
        if self.near(x,131.5625) and self.near(y,30):
            self.can.create_oval(131.5625-r, 30-r, 131.5625+r, 30+r, fill="lightgreen")
        if self.near(x,253.4375) and self.near(y,30):
            self.can.create_oval(253.4375-r, 30-r, 253.4375+r, 30+r, fill="lightgreen")
        if self.near(x,355) and self.near(y,30):
            self.can.create_oval(355-r, 30-r, 355+r, 30+r, fill="lightgreen")
        # bottom line
        if self.near(x,30) and self.near(y,680):
            self.can.create_oval(308-r, 680-r, 30+r, 680+r, fill="lightgreen")
        if self.near(x,131.5625) and self.near(y,680):
            self.can.create_oval(131.5625-r, 680-r, 131.5625+r, 680+r, fill="lightgreen")
        if self.near(x,253.4375) and self.near(y,680):
            self.can.create_oval(253.4375-r, 680-r, 253.4375+r, 680+r, fill="lightgreen")
        if self.near(x,355) and self.near(y,680):
            self.can.create_oval(355-r, 680-r, 355+r, 680+r, fill="lightgreen")
        # bottom line
        if self.near(x,30) and self.near(y,355):
            self.can.create_oval(30-r, 355-r, 30+r, 355+r, fill="lightgreen")
        if self.near(x,355) and self.near(y,355):
            self.can.create_oval(355-r, 355-r, 355+r, 355+r, fill="lightgreen")


    def startCalculation(self):
        if len(self.image_points)==len(self.field_points) and len(self.image_points)>=4:
            print("START CALCULATION")
            calc = HomographyCalculation(self.image_points, self.field_points)
            

    def image_click_handler(self,event):
        #print('position: x='+str(event.x)+", y="+str(event.y))
        self.image_points.append([event.x,event.y])

        # set number of matched points in frame
        if len(self.image_points)==len(self.field_points):
            self.nrPoints['text']=str(len(self.image_points))

    def point_handler(self, event):
        x=round((event.x-30)/16.25,2)
        y=round((event.y-30)/16.25,2)
        #print('point: x='+str(x)+", y="+str(y))
        self.field_points.append([x,y])

        # set number of matched points in frame
        if len(self.image_points)==len(self.field_points):
            self.nrPoints['text']=str(len(self.image_points))

        # recolor circle
        self.recolor_marker(round(event.x,1), round(event.y,1))

    def client_exit(self):
        exit()