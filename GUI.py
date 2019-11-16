import PySimpleGUI as sg
from PIL import Image, ImageTk
import PIL
import numpy as np
import io
import base64
from io import BytesIO
import csv
## pip install PySimpleGui
## tk only accept image with format of gif or png. 
## using jmp, we need to read jmp and convert to base64
## 
def image_to_base64(image_path):
    img = Image.open(image_path)
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str


## layout of the GUI
layout = [[sg.Text('CSVREAD')],[sg.Input(key='path'), sg.FileBrowse()],[sg.OK("load",key='load'), sg.OK("next",key='next'),sg.OK("save&quit",key='save')],
          [sg.Graph(
            canvas_size=(400, 400),
            graph_bottom_left=(0, 400),
            graph_top_right=(400, 0),
            key="GRAPH",
            enable_events=True,  drag_submits=True),],
            [sg.Text("",key='info', size=(50, 1)),sg.Text(key='save', size=(30, 1))]]
## show the window of GUI          
window = sg.Window("draw rect on image", layout, finalize=True)

graph = window["GRAPH"]        
path = ''          
addrlist = []

while True:
    event,values = window.read()
    print(event)
    if event is None or event == 'Exit':
        break    

    if event == 'load':
        print('now load')
        if path == '':
            try:
                
                path =  values['path']
                print(path)
                csvFile = open(path, "r")
                reader = csv.reader(csvFile)

                for item in reader:
                    # ignore the fisrt line
                    if reader.line_num == 1:
                        continue
                    addrlist.append(item[0])

                    if len(addrlist) == 150:
                        break
                csvFile.close()    
                break     
            except IOError:
                sg.PopupError('Invalid csv path or check the form of csv')  
                
imgaddr = addrlist.pop()
graph.draw_image(data=image_to_base64(r"C:/Users/sunzh/Downloads/CheXpert-v1.0-small/" + imgaddr), location=(0,0))# need to change according to the situation
dragging = False
start_point = end_point = prior_rect = None
csvwriter = []
header = ['Path', 'Start Point', 'End Point']

while len(addrlist) > 0:
    
    
    event,values = window.read()
    print(event, len(addrlist))
    if event is None:
        break  # exit
    
    if event == "GRAPH":                      # if there's a "Graph" event, then it's a mouse
        x, y = values["GRAPH"]
        if not dragging:
            start_point = (x, y)
            dragging = True
        else:
            end_point = (x, y)
        if prior_rect:
            graph.delete_figure(prior_rect)
        if None not in (start_point, end_point):
            prior_rect = graph.draw_rectangle(start_point, end_point, line_color='red')
    
    elif event.endswith('+UP'):                 # The drawing has ended because mouse up
        info = window["info"]
        info.update(value=f"grabbed rectangle from {start_point} to {end_point}")
        # start_point, end_point = None, None     # enable grabbing a new rect
        dragging = False

    if event == "next":
        csvwriter.append([r"C:/Users/sunzh/Downloads/CheXpert-v1.0-small/" + imgaddr, start_point, end_point])
        imgaddr = addrlist.pop()
        graph.draw_image(data=image_to_base64(r"C:/Users/sunzh/Downloads/CheXpert-v1.0-small/" + imgaddr), location=(0,0))# if image_file else Non
        dragging = False
        start_point = end_point = prior_rect = None        
    
    if event == 'save':
        print(csvwriter)

        with open('chestannotation.csv','w',encoding='utf8',newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(header)
            f_csv.writerows(csvwriter)    
        
        window.close()