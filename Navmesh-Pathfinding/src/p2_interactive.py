import sys
import random
import pickle
import traceback
import tkinter

import p2_pathfinder

if len(sys.argv) != 4:
    print("usage: %s map.gif map.mesh.pickle subsample_factor" % sys.argv[0])
    sys.exit(-1)

_, MAP_FILENAME, MESH_FILENAME, SUBSAMPLE = sys.argv
SUBSAMPLE = int(SUBSAMPLE)

with open(MESH_FILENAME, 'rb') as f:
  mesh = pickle.load(f)

master = tkinter.Tk()

big_image = tkinter.PhotoImage(file=MAP_FILENAME)
small_image = big_image.subsample(SUBSAMPLE,SUBSAMPLE)
BIG_WIDTH, BIG_HEIGHT = big_image.width(), big_image.height()
SMALL_WIDTH, SMALL_HEIGHT = small_image.width(), small_image.height()

canvas = tkinter.Canvas(master, width=SMALL_WIDTH, height=SMALL_HEIGHT)
canvas.pack()


def shrink(values):
    return [v/SUBSAMPLE for v in values]

source_point = None
destination_point = None
visited_boxes = []
path = []


def redraw():

    canvas.delete(tkinter.ALL)
    canvas.create_image((0,0), anchor=tkinter.NW, image=small_image)

    for box in visited_boxes:
        x1,x2,y1,y2 = shrink(box)
        canvas.create_rectangle(y1,x1,y2,x2,outline='pink')

    for i in range(len(path) - 1):
        x1, y1 = shrink(path[i])
        x2, y2 = shrink(path[i + 1])
        canvas.create_line(y1,x1,y2,x2,width=2.0,fill='red')

    if source_point:
        x,y = shrink(source_point)
        canvas.create_oval(y-5,x-5,y+5,x+5,width=2,outline='red')

    if destination_point:
        x,y = shrink(destination_point)
        canvas.create_oval(y-5,x-5,y+5,x+5,width=2,outline='red')


def on_click(event):

    global source_point, destination_point, visited_boxes, path

    if source_point and destination_point:
        source_point = None
        destination_point = None
        visited_boxes = []
        path = []

    elif not source_point:
        source_point = event.y*SUBSAMPLE, event.x*SUBSAMPLE

    else:
        destination_point = event.y*SUBSAMPLE, event.x*SUBSAMPLE
        try:
            path, visited_boxes = p2_pathfinder.find_path(source_point, destination_point, mesh)

        except:
            destination_point = None
            traceback.print_exc()

    redraw()

canvas.bind('<Button-1>', on_click)

redraw()
master.mainloop()
