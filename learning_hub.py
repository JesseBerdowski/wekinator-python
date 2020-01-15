from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from ThreadingServer_test import *
import threading
from sklearn.linear_model import LinearRegression
import numpy as np
from tkinter import *



#Object Declaration
#####################################################



#create ip and ports
ip = "127.0.0.1"
port = 8339
port_client = 8609
#create gate which controls slider output
gate_slider = True
#client
client = SimpleUDPClient(ip, port_client)
#two lists used for learning
i_lst = []
o_lst = []
#linear regression
linear_regressor = LinearRegression() 



#Handler Methods
#####################################################



#activated when the learn button is pressed, blocks the message from slider to client 
def GateHandler(address, *args):
	global gate_slider
	gate_slider = False

#sends message from slider to client, only when not learning
def SliderHandler(address, *args):
	if gate_slider :
		client.send_message("jemoerke", args)

#inputs the input stream
def InputHandler(address, *args) :
	global gate_slider
	gate_slider = True
	for value in args :
		i_lst.append(value)

#input the learned output stream
def OutputHandler(address, *args) :
	for value in args :
		o_lst.append(value)

#convert lists to arrays and train model
def TrainingHandler(address, *args) :
	i_array = np.asarray(i_lst)
	o_array = np.asarray(o_lst) 
	linear_regressor.fit(o_array.reshape(-1, 1), i_array) 

#livetime predict outputs 
def RunHandler(address, *args) :
	run_array = np.asarray(args)
	Y_pred = linear_regressor.predict(run_array.reshape(-1, 1))
	global gate_slider
	gate_slider = False
	client.send_message("prediction/address", Y_pred)



#Dispatcher Declarations and Mapping, Server
#####################################################



#creates and maps the dispatchers
dispatcher = Dispatcher() 
dispatcher.map("/gate/address", GateHandler)
dispatcher.map("/slider/address", SliderHandler)
dispatcher.map("/output/address", InputHandler)
dispatcher.map("/input/address", OutputHandler)
dispatcher.map("/train/address", TrainingHandler)
dispatcher.map("/run/address", RunHandler)

#creates a server
server = BlockingOSCUDPServer((ip, port), dispatcher)
while True :
	server.handle_request()
