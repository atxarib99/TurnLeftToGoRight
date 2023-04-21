import sys
import ac
import acsys
import os
import json
import re

fr_series = []
fl_series = []
rr_series = []
rl_series = []

friction_limit_rear = 0
friction_limit_front = 0

window_width = 600
window_height = 300

tyreData = {}

def log_to_file(msg):
    ac.log("scrubometer: " + str(msg))

def log_to_console(msg):
    ac.console("scrubometer: " + str(msg))

def log(msg):
    ac.log("scrubometer: " + str(msg))
    ac.console("scrubometer: " + str(msg))

def acMain(ac_version):
    appWindow = ac.newApp("scrubometer")
    ac.setSize(appWindow, window_width, window_height)
    log("SEM SEM SEM SEM")

    # ac.setPosition(l_current_slip_angle, 3, 30)
    ac.addRenderCallback(appWindow, onFormRender)

    loadMyTireData()

    return "scrubometer"


def loadMyTireData():
    global tyreData
    carName = ac.getCarName(0)
    tyreCompound = ac.getCarTyreCompound(0)
    tyreDataPath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\assettocorsa\\content\\cars\\" + carName + "\\data\\tyres.ini"
    tyreData = {}
    try:
        f = open(tyreDataPath, 'r')
        #find [*Front*]
        tyreType = "NONE"
        compoundType = "NONE"
        for line in f.readlines():
            if tyreType not in tyreData:
                tyreData[tyreType] = {}
            if compoundType not in tyreData[tyreType]:
                tyreData[tyreType][compoundType] = {}
            if len(line) == 0:
                continue
            #handle types
            pattern = "\[FRONT_\d*\]"
            if line == "[FRONT]\n" or re.match(pattern, line):
                tyreType = "FRONT"
                continue
                
            pattern = "\[REAR_\d*\]"
            if line == "[REAR]\n" or re.match(pattern, line):
                tyreType = "REAR"
                continue
            
            if "SHORT_NAME" in line:
                compoundType = line.split('=')[1]
                compoundType = compoundType.replace('\n', '')
                continue
            
            myline = line.replace("\t", "").replace("\n", "").replace(" ", "")
            myline = myline.split(';')[0]
            
            if '=' in myline:
                tyreData[tyreType][compoundType][myline.split('=')[0]] = myline.split('=')[1].replace('\n','')
        log("Loaded tyre data!")
    except RuntimeError as e:
        log("Can't load tyre data. Try unpacking data.")
        log(e)

        

def acUpdate(deltaT):
    global friction_limit_front
    global friction_limit_rear

    tyreCompound = ac.getCarTyreCompound(0)
    friction_limit_front = float(tyreData['FRONT'][tyreCompound]['FRICTION_LIMIT_ANGLE'])
    friction_limit_rear = float(tyreData['REAR'][tyreCompound]['FRICTION_LIMIT_ANGLE'])

def draw_box(x, y, width, height):
    """
    Draws a box using the draw() function with the given x, y coordinates,
    width, and height.
    """
    ac.glColor3f(0,1,0)
    ac.glQuad(x, y, width, 1)  # Top edge
    ac.glQuad(x, y + height - 1, width, 1)  # Bottom edge
    ac.glQuad(x, y, 1, height)  # Left edge
    ac.glQuad(x + width - 1, y, 1, height)  # Right edge
    ac.glColor3f(1,0,0)
    ac.glQuad(x, y + height // 2, width, 1)  # Horizontal line
    ac.glColor3f(0,0,1)
    ac.glQuad(x, y + height // 4, width, 1)  # Horizontal line
    ac.glQuad(x, y + height // 4 * 3, width, 1)  # Horizontal line


def onFormRender(deltaT):
    global fr_series
    global fl_series
    global rl_series
    global rr_series
    
    box_width = 250
    box_height = 125

    # Calculate box coordinates
    box1_x = window_width // 4 - box_width // 2
    box1_y = window_height // 4 - box_height // 2
    box2_x = 3 * window_width // 4 - box_width // 2
    box2_y = window_height // 4 - box_height // 2
    box3_x = window_width // 4 - box_width // 2
    box3_y = 3 * window_height // 4 - box_height // 2
    box4_x = 3 * window_width // 4 - box_width // 2
    box4_y = 3 * window_height // 4 - box_height // 2

    box1_y += 10
    box2_y += 10
    box3_y += 10
    box4_y += 10
    

    draw_box(box1_x, box1_y, box_width, box_height)
    draw_box(box2_x, box2_y, box_width, box_height)
    draw_box(box3_x, box3_y, box_width, box_height)
    draw_box(box4_x, box4_y, box_width, box_height)
    
    # #draw 0 line
    ac.glColor3f(1,0,0)
    # ac.glQuad(3,180,600,1)
    
    fl_slip, fr_slip, rl_slip, rr_slip = ac.getCarState(0, acsys.CS.SlipAngle)

    fr_series.append(fr_slip)
    fl_series.append(fl_slip)
    rr_series.append(rr_slip)
    rl_series.append(rl_slip)
    
    # log_to_console(len(fr_series))
    if len(fr_series) > box_width:
        #drop first element
        # 0,1,3,2,1
        fr_series.pop(0)
        fl_series.pop(0)
        rr_series.pop(0)
        rl_series.pop(0)

        #for some reason i have to use a copy
        fr_seriescp = fr_series.copy()
        fl_seriescp = fl_series.copy()
        rr_seriescp = rr_series.copy()
        rl_seriescp = rl_series.copy()
        
        # r_series.reverse()
        for i in range(0, box_width):
            #convert slip angle to height
            slip_angle = fl_seriescp.pop(-1)
            height = slip_angle / (friction_limit_front * 2) * box_height/2
            # height = (0,1)
            # height = slip_angle / (friction_limit_front * 2)
            if height > box_height/2:
                height = box_height/2
            elif height < -box_height/2:
                height = -box_height/2
            height = int(height)
            ac.glQuad((box_width-i)+box1_x, box1_y+box_height//2, 1, height)

            #convert slip angle to height
            slip_angle = fr_seriescp.pop(-1)
            height = slip_angle / (friction_limit_front * 2) * box_height/2
            if height > box_height/2:
                height = box_height/2
            elif height < -box_height/2:
                height = -box_height/2
            height = int(height)
            ac.glQuad((box_width-i)+box2_x, box2_y+box_height//2, 1, height)

            #convert slip angle to height
            slip_angle = rl_seriescp.pop(-1)
            height = slip_angle / (friction_limit_rear * 2) * box_height/2
            if height > box_height/2:
                height = box_height/2
            elif height < -box_height/2:
                height = -box_height/2
            height = int(height)
            ac.glQuad((box_width-i)+box3_x, box3_y+box_height//2, 1, height)

            #convert slip angle to height
            slip_angle = rr_seriescp.pop(-1)
            height = slip_angle / (friction_limit_rear * 2) * box_height/2
            if height > box_height/2:
                height = box_height/2
            elif height < -box_height/2:
                height = -box_height/2
            height = int(height)
            ac.glQuad((box_width-i)+box4_x, box4_y+box_height//2, 1, height)
