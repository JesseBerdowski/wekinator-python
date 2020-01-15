from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import threading
import time
from tkinter import *   



#Object Declarations
#####################################################



#slider value
s_value = 0

#gates
record_gate = True
tuple_gate = False
run_gate = False

#input- and output list
i_lst = []
o_lst = []

#server_info
ip = "127.0.0.1"
port = 8558
port_client = 8339

#button event
mapping_event = threading.Event()
mapping_event.set()

#create client
client = SimpleUDPClient(ip, port_client)



#Handler Methods
#####################################################



#Learning Handler
def LearnHandler(address, *args):
    #fill list with incoming value and slider value
    i_lst.append(args[0])
    o_lst.append(s_value)

    #clear the lists of possible roaming messages before Start is pressed
    global tuple_gate
    if tuple_gate :
        del o_lst[:]
        del i_lst[:]
        tuple_gate = False

#Send Slider Value to Client to Supervise Desired Outcome
def SliderHandler(address, *args):
    if run_gate :
        client.send_message("/run/address", args)



#Dispatcher Declaration and Mapping
#####################################################



#Create Dispatcher and Handlers
dispatcher = Dispatcher()
dispatcher.map("/mapping_module", LearnHandler)
dispatcher.map("/mapping_module", SliderHandler)



#Button Commands
#####################################################



#Start Button
def StartLearn():
    global record_gate
    global run_gate 
    global tuple_gate

    #clean list, enable transferring list to client, block slider
    tuple_gate = True 
    record_gate = True  
    run_gate = False

    #sends message to block the slider data transfer 
    client.send_message("/gate/address", None) 

#Stop Button    
def StopLearn():
    global record_gate
    #block incoming server message 
    mapping_event.clear()

    #gate that enables transfer of input/ output list 
    if record_gate :
        client.send_message("/output/address", o_lst)  
        client.send_message("/input/address", i_lst)
        record_gate = False

    #again enable incoming server message
    mapping_event.set()

#Initiate Training Models Button
def Train() :
    client.send_message("/train/address", None)

#Initiate Live Predictions Button
def Run() :
    global run_gate
    run_gate = True



#GUI and Slider Output
#####################################################



#GUI
def GUI():
    global s_value

    window = Tk()
    window.title("Wekinator Python")
    window.geometry('350x200')

    btn = Button(window, text="Start", command = StartLearn)
    btn_2 = Button(window, text="Stop", command = StopLearn)
    btn_3 = Button(window, text="Train", command = Train)
    btn_4 = Button(window, text="Run", command = Run)

    btn.grid(column=1,  row = 0)
    btn_2.grid(column=2, row =0)
    btn_3.grid(column=3, row = 0)
    btn_4.grid(column=4, row = 0)

    output = Scale(window, from_=100, to=0)
    output.grid(column=1, row=1)    

    #Infinite Loop which creates Window 
    while True :
        window.update_idletasks()

        #transfer slider value
        s_value = output.get()
        client.send_message("/slider/address", s_value) 

        window.update()
        window.after(1)



#Server 
#####################################################



#Create Server
server = BlockingOSCUDPServer((ip, port), dispatcher)
def server_handler() :
    while True :
        mapping_event.wait()
        #Receive message (one at a time)
        while mapping_event.is_set() :
            server.handle_request() 



#Threads
#####################################################



#Create Threads
t1 = threading.Thread(target = GUI, daemon = False)
t1.start()
t2 = threading.Thread(target = server_handler)
t2.start()
