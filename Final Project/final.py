import tkinter as tk
from tkinter import ttk
import socket
import json
import struct
import threading
import time
from relationship_handler import *
from app_manager import *
import config

service_list = []
relationship_list = []

def serviceScan(): #gets all the available things, services, and relationships
    global service_list
    global relationship_list
    ThingsListbox.delete(0,tk.END)
    ServicesListbox.delete(0,tk.END)
    RelationshipsListBox.delete(0,tk.END)
    ServListbox.delete(0,tk.END)
    RelListbox.delete(0,tk.END)
    ArrListbox.delete(0,tk.END)
    AppNameBox.delete(0,tk.END)
    AppsListbox.delete(0,tk.END)
    service_jsons = []
    # these are the ip and ports we need for the atlas multicast
    multicast_group = '232.1.1.1'
    server_address = ('', 1235)

    # create and bind socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(server_address)

    # assign and set up group
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # scan for services for 60 seconds
    start = time.time()
    while time.time() - start < 60:
        print('\nwaiting to receive message')
        data, address = s.recvfrom(1024)
        print('received %s bytes from %s' % (len(data), address))
        #append address to data string in JSON format
        data = data.decode("utf-8")
        print(data)
        data = data[:2] + "\"IP Address\" : \"" + str(address[0]) + "\"," + data[2:]
        print(data)
        if data not in service_jsons:
            service_jsons.append(data)
    print("\n\nThis is the list of JSON data:\n")
    service_list = []
    relationship_list = []
    for j in service_jsons:
        index = j.rfind("Vendor")
        if index != -1:
            front = j[:index]
            end = j[index+1:]
            index = end.find(",")
            if index != -1:
                rear = end[:index]
            j = front + rear + "}"
        x = json.loads(j)
        if x["Tweet Type"] == "Service":
            service_list.append(x)
        if x["Tweet Type"] == "Relationship":
            relationship_list.append(x)

    # print service names
    print("\nService API Call: ")
    services = []
    for j in service_list:
        new_json = {
                    "Tweet Type" : "Service call",
                    "Thing ID" : j["Thing ID"],
                    "Entity ID" : j["Entity ID"],
                    "Space ID" : j["Space ID"],
                    "Service Name" : j["Name"],
                    "Service Inputs" : "placeholder"
        }
        services.append(new_json)
    print(services)
    print("\n\nServices: ")
    for k in service_list:
        print(k)
    print("\n\nRelationships: ")
    for k in relationship_list:
        print(k)

    for j in service_list:
        combo = "Thing ID: " + str(j["Thing ID"]) + "   Space ID: " + str(j["Space ID"])
        temp = ThingsListbox.get(0,tk.END)
        test = 0
        for i in temp:
            if(i == combo):
                test = 1
        if(test == 0):
            ThingsListbox.insert(tk.END,combo)
        
    for j in relationship_list:
        combo = "Thing ID: " + str(j["Thing ID"]) + "   Space ID: " + str(j["Space ID"])
        temp = ThingsListbox.get(0,tk.END)
        test = 0
        for i in temp:
            if(i == combo):
                test = 1
        if(test == 0):
            ThingsListbox.insert(tk.END,combo)
    s.close()
    
    ServicesListbox.delete(0,tk.END)
    temp = ThingsListbox.get(0,tk.END)
    for i in temp:
        thing_id = i.split(' ')[2]
        ServicesListbox.insert(tk.END,"Thing ID: " + thing_id)
        ServListbox.insert(tk.END,"Thing ID: " + thing_id)
        RelationshipsListBox.insert(tk.END,"Thing ID: " + thing_id)
        RelListbox.insert(tk.END,"Thing ID: " + thing_id)
        for j in service_list:
            if(j["Thing ID"] == thing_id):
                ServicesListbox.insert(tk.END,"                " + j["Name"])
                ServListbox.insert(tk.END,"                " + j["Name"])
        for k in relationship_list:
            if(k["Thing ID"] == thing_id):
                RelationshipsListBox.insert(tk.END,"                " + k["Name"])
                RelListbox.insert(tk.END,"                " + k["Name"])

def ServListboxClick(evt): #check if service listbox pressed
    w = evt.widget.curselection()
    if w:
        index = w[0]
        value = evt.widget.get(index).strip()
        tempstr = ""
        for k in service_list:
            if(k["Name"] == value):
                tempstr = k["Thing ID"]
        servstr = "S: " + value + "        Thing ID: " + tempstr
        ArrListbox.insert(tk.END, servstr)

def RelListboxClick(evt): #check if relationship listbox pressed
    w = evt.widget.curselection()
    if w:
        index = w[0]
        value = evt.widget.get(index).strip()
        tempstr = ""
        for k in relationship_list:
            if(k["Name"] == value):
                tempstr = k["Thing ID"]
        relstr = "R: " + value + "        Thing ID: " + tempstr
        ArrListbox.insert(tk.END, relstr)

def ClearListBox(): #clear recipe listbox
    ArrListbox.delete(0,tk.END)

def FinalizeApp(): #save app
    temp = ArrListbox.get(0,tk.END)
    appdata = []
    for k in temp:
        strsplit = k.split(' ')
        servName = strsplit[1]
        thingID = strsplit[len(strsplit)-1]
        apptuple = (servName, thingID)
        appdata.append(apptuple)
    appName = AppNameBox.get()
    print(appdata)
    print(appName)
    save_app(appName, appdata)
    
def get_apps(): #returns all available apps
    # read in files
    AppsListbox.delete(0,tk.END)
    files = [f for f in listdir('./apps/') if isfile(join('./apps/', f))]
    # return
    for k in files:
        AppsListbox.insert(tk.END,k)

def UploadToBox(): #upload app
    val = AppsListbox.get(tk.ACTIVE)
    filename = './apps/' + val
    file = open(filename, 'r')
    text = file.readlines()
    UploadText.delete('1.0',tk.END)
    for t in text:
        UploadText.insert(tk.END,t)

def SaveClick(): #save app with editor
    app_name = AppsListbox.get(tk.ACTIVE)
    app_data = UploadText.get("1.0", "end")
    savenontuple_app(app_name,app_data)
    print("Saved successfully")

def delApp(): #delete app
    val = AppsListbox.get(tk.ACTIVE)
    delete_app(val)
    
def activateApp(): #deploy app
    val = AppsListbox.get(tk.ACTIVE)
    x = threading.Thread(target=load_app, args=(relationship_list, service_list, val))
    x.start()

def sendStopVariable(): #stop app
    config.stop_var = True
    
def RelationshipTypeServ(evt): #change relationship
    w = evt.widget.curselection()
    if w:
        index = w[0]
        value = evt.widget.get(index).strip()
        TypeEntry.delete(0, 'end')
        FSEntry.delete(0, 'end')
        SSEntry.delete(0, 'end')
        for i in relationship_list:
            if(i["Name"] == value):
                TypeEntry.insert(tk.END,i["Type"])
                FSEntry.insert(tk.END,i["FS name"])
                SSEntry.insert(tk.END,i["SS name"])

def SaveRelationship(): #save relationship
    relType = TypeEntry.get()
    FirstServ = FSEntry.get()
    SecondServ = SSEntry.get()
    relName = RelationshipsListBox.get(tk.ACTIVE).strip()
    for j in relationship_list:
        if j["Name"] == relName:
            j["FS name"] = FirstServ
            j["SS name"] = SecondServ
            j["Type"] = relType
            print(j)

def center(win): #centers a tkinter window with parameter of the main window
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()
    
#makes a tkinter gui
mainWindow = tk.Tk()
mainWindow.title("IoT Final Project")
mainWindow.geometry("900x700")
center(mainWindow)
notebook = ttk.Notebook(mainWindow) #tab view
notebook.pack(pady=5, expand=True)

frameThings = ttk.Frame(notebook, width=870, height=670)
frameServices = ttk.Frame(notebook, width=870, height=670)
frameRelationships = ttk.Frame(notebook, width=870, height=670)
frameApps = ttk.Frame(notebook, width=870, height=670)
frameRecipe = ttk.Frame(notebook, width=870, height=670)

frameThings.pack(fill='both', expand=True)
frameServices.pack(fill='both', expand=True)
frameRelationships.pack(fill='both', expand=True)
frameApps.pack(fill='both', expand=True)
frameRecipe.pack(fill='both', expand=True)

#Things
notebook.add(frameThings, text='Things')
ThingsLabel = tk.Label(frameThings, text = "Things", font=("Helvetica", 18, 'bold'))
ThingsLabel.place(x = 380, y = 10)
ThingsButton = tk.Button(frameThings, text = "Receive", font=("Helvetica", 18, 'bold'), command = serviceScan, bg='#00a2ff', activebackground='#00a2ff')
ThingsButton.place(x = 360, y = 500)
ThingsListbox = tk.Listbox(frameThings, activestyle = "none", height = 20, width = 50, font=("Helvetica", 12))
ThingsListbox.place(x = 200, y = 70)

#Services
notebook.add(frameServices, text='Services')
ServicesLabel = tk.Label(frameServices, text = "Services", font=("Helvetica", 18, 'bold'))
ServicesLabel.place(x = 370, y = 10)
ServicesListbox = tk.Listbox(frameServices, activestyle = "none", height = 25, width = 40, font=("Helvetica", 12))
ServicesListbox.place(x = 250, y = 70)

#Relationships
notebook.add(frameRelationships, text='Relationships')
RelationshipsLabel = tk.Label(frameRelationships, text = "Relationships", font=("Helvetica", 18, 'bold'))
RelationshipsLabel.place(x = 360, y = 10)
RelationshipsListBox = tk.Listbox(frameRelationships, activestyle = "none", height = 25, width = 40, font=("Helvetica", 12))
RelationshipsListBox.bind('<<ListboxSelect>>', RelationshipTypeServ)
RelationshipsListBox.place(x = 100, y = 70)
TypeLabel = tk.Label(frameRelationships, text = "Type", font=("Helvetica", 16, 'bold'))
TypeLabel.place(x = 630, y = 120)
TypeEntry = tk.Entry(frameRelationships, justify='center', font=("Helvetica", 16), width = 18)
TypeEntry.place(x = 550, y = 155)
FSLabel = tk.Label(frameRelationships, text = "First Service", font=("Helvetica", 16, 'bold'))
FSLabel.place(x = 600, y = 230)
FSEntry = tk.Entry(frameRelationships, justify='center', font=("Helvetica", 16), width = 18)
FSEntry.place(x = 550, y = 265)
SSLabel = tk.Label(frameRelationships, text = "Second Service", font=("Helvetica", 16, 'bold'))
SSLabel.place(x = 585, y = 345)
SSEntry = tk.Entry(frameRelationships, justify='center', font=("Helvetica", 16), width = 18)
SSEntry.place(x = 550, y = 380)
SaveRelButton = tk.Button(frameRelationships, text = "Save", font=("Helvetica", 18, 'bold'), width = 7, command = SaveRelationship, bg='#00a2ff', activebackground='#00a2ff')
SaveRelButton.place(x = 600, y = 450)

#Apps
notebook.add(frameApps, text='Apps')
AppsLabel = tk.Label(frameApps, text = "Apps", font=("Helvetica", 18, 'bold'))
AppsLabel.place(x = 390, y = 10)
AppsListbox = tk.Listbox(frameApps, activestyle = "none", height = 20, width = 20, font=("Helvetica", 12))
AppsListbox.place(x = 70, y = 115)
ActivateButton = tk.Button(frameApps, text = "Activate", font=("Helvetica", 18, 'bold'), width = 7, command = activateApp, bg='#00a2ff', activebackground='#00a2ff')
ActivateButton.place(x = 30, y = 520)
StopButton = tk.Button(frameApps, text = "Stop", font=("Helvetica", 18, 'bold'), width = 7, command = sendStopVariable, bg='#00a2ff', activebackground='#00a2ff')
StopButton.place(x = 180, y = 520)
UploadButton = tk.Button(frameApps, text = "Upload", font=("Helvetica", 18, 'bold'), width = 7, command = UploadToBox, bg='#00a2ff', activebackground='#00a2ff')
UploadButton.place(x = 30, y = 600)
DeleteButton = tk.Button(frameApps, text = "Delete", font=("Helvetica", 18, 'bold'), width = 7, command = delApp, bg='#00a2ff', activebackground='#00a2ff')
DeleteButton.place(x = 180, y = 600)
RefreshButton = tk.Button(frameApps, text = "Refresh", font=("Helvetica", 18, 'bold'), width = 7, command = get_apps, bg='#00a2ff', activebackground='#00a2ff')
RefreshButton.place(x = 105, y = 50)
UploadText = tk.Text(frameApps,width = 60, height = 30)
UploadText.place(x = 350, y = 70)
SaveButton = tk.Button(frameApps, text = "Save", font=("Helvetica", 18, 'bold'), width = 7, command = SaveClick, bg='#00a2ff', activebackground='#00a2ff')
SaveButton.place(x = 550, y = 570)

#Recipe
notebook.add(frameRecipe, text='Recipe')
RecipeLabel = tk.Label(frameRecipe, text = "Recipe", font=("Helvetica", 18, 'bold'))
RecipeLabel.place(x = 390, y = 10)
RecipeFinalizedButton = tk.Button(frameRecipe, text = "Finalize", font=("Helvetica", 18, 'bold'), command = FinalizeApp, bg='#00a2ff', activebackground='#00a2ff')
RecipeFinalizedButton.place(x = 720, y = 460)
RecipeClearButton = tk.Button(frameRecipe, text = "Clear", font=("Helvetica", 18, 'bold'), command = ClearListBox, bg='#00a2ff', activebackground='#00a2ff')
RecipeClearButton.place(x = 50, y = 460)
ServLabel = tk.Label(frameRecipe, text = "Services", font=("Helvetica", 16, 'bold'))
ServLabel.place(x = 190, y = 50)
ServListbox = tk.Listbox(frameRecipe, activestyle = "none", height = 15, width = 35, font=("Helvetica", 12))
ServListbox.bind('<<ListboxSelect>>', ServListboxClick)
ServListbox.place(x = 80, y = 80)
RelLabel = tk.Label(frameRecipe, text = "Relationships", font=("Helvetica", 16, 'bold'))
RelLabel.place(x = 560, y = 50)
RelListbox = tk.Listbox(frameRecipe, activestyle = "none", height = 15, width = 35, font=("Helvetica", 12))
RelListbox.bind('<<ListboxSelect>>', RelListboxClick)
RelListbox.place(x = 470, y = 80)
ArrListbox = tk.Listbox(frameRecipe, activestyle = "none", height = 10, width = 50, font=("Helvetica", 12))
ArrListbox.place(x = 205, y = 390)
AppNameLabel = tk.Label(frameRecipe, text = "App Name", font=("Helvetica", 16, 'bold'))
AppNameLabel.place(x = 280, y = 600)
AppNameBox = tk.Entry(frameRecipe, justify='center', font=("Helvetica", 16), width = 12)
AppNameBox.place(x = 410, y = 600)

#displays the tkinter gui
mainWindow.mainloop()