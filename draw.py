import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import pandas as pd
import math
import numpy as np

def drawStroke():
    stroke = pd.DataFrame(columns=["x", "y"])
    currentStroke = []
    last = None
    xlim = [-.765, .765]
    ylim = [-.765, .765] #lims 
    minDist = 0.015 #stroke length
    inner = 0.243 
    outer = 0.550 #workapce radii

    def click(event):
        nonlocal last
        nonlocal currentStroke
        if fig.canvas.toolbar.mode != "" or event.button != 1 or not event.inaxes: # check if tool is clicked so it doesnt draw a stroke when using zoom or move tool 
            return 
        pos = (event.xdata, event.ydata)
        dist = math.dist((pos[0],pos[1]), (0,0))
        if not (dist < outer and dist > inner):
            return
        if math.dist(last, pos) >= minDist or last is None: # draw point
            currentStroke.append(pos)
            last = pos 
            line.set_data(zip(*currentStroke)) 

            fig.canvas.draw() #draw


    def unclick(event):
        nonlocal stroke 
        nonlocal currentStroke #nested so nonlocal
        nonlocal last
        if event.button == 1 and currentStroke: #finish stroke
            stroke = pd.concat([stroke, pd.DataFrame(currentStroke, columns=["x", "y"])], ignore_index=True) # store for plotting
            currentStroke = []
            last = None
            axis.scatter(stroke["x"], stroke["y"], s = 10, c ='red') #plot
            fig.canvas.draw()

    def clear(event):
        nonlocal stroke
        nonlocal currentStroke 
        nonlocal last
        nonlocal line
        stroke = pd.DataFrame(columns=["x", "y"])
        currentStroke = []
        last = None
        axis.clear()
        axis.set_xlim(xlim)
        axis.set_ylim(ylim)
        axis.set_aspect("equal")
        axis.grid(True)
        innerCirc = plt.Circle((0, 0), inner, color='red', fill = True) # plot the reachable workspace
        outerCirc = plt.Circle((0, 0), outer, color='red', fill = False)
        axis.add_patch(innerCirc)
        axis.add_patch(outerCirc)

        line, = axis.plot([], [], lw=1.5)

        fig.canvas.draw()

    def done(event):
        plt.close(fig)

    fig, axis = plt.subplots()
    axis.set_xlim(xlim)
    axis.set_aspect("equal")
    axis.set_ylim(ylim)
    axis.grid(True)
    axis.set_title("Laser Canvas")
    line, = axis.plot([], [], lw=1.5) # make line
    innerCirc = plt.Circle((0, 0), inner, color='red', fill = True) # plot the reachable workspace
    outerCirc = plt.Circle((0, 0), outer, color='red', fill = False)
    axis.add_patch(innerCirc)
    axis.add_patch(outerCirc)
    fig.canvas.mpl_connect("motion_notify_event", click)
    fig.canvas.mpl_connect("button_release_event", unclick)

    cler = plt.axes([0.8, 0.01, 0.1, 0.075])  #clea button 
    clearButton = Button(cler, 'Clear')
    clearButton.on_clicked(clear)

    doneButton = plt.axes([0.8, 0.09, 0.1, 0.075]) #don buttone
    dne = Button(doneButton, 'Done')
    dne.on_clicked(done)
    plt.show()
    return stroke
