from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
import numpy as np
from tkinter import *



#Object Declaration
#####################################################



#create ip and ports
ip = "127.0.0.1"
port = 8339
port_client = 8609

#gates
gate_slider = True
gate_switch = True

#client
client = SimpleUDPClient(ip, port_client)

#two lists used for learning
i_lst = []
o_lst = []

#learning algorithms
linear_regressor = LinearRegression() 
logistic_regressor = LogisticRegression()



#Handler Methods
#####################################################



#activated when the learn button is pressed, blocks the message from slider to client 
def GateHandler(address, *args):
	global gate_slider
	gate_slider = False

#sends message from slider to client, only when not learning
def SliderHandler(address, *args):
	if gate_slider :
		client.send_message("prediction/address", args)

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

	if gate_switch :
		linear_regressor.fit(o_array.reshape(-1, 1), i_array) 
	else :
		logistic_regressor.fit(o_array.reshape(-1, 1), i_array)

#livetime predict outputs 
def RunHandler(address, *args) :
	run_array = np.asarray(args)

	if gate_switch :
		Y_pred = linear_regressor.predict(run_array.reshape(-1, 1))
	else :
		Y_pred_array = logistic_regressor.predict(run_array.reshape(-1, 1))
		Y_pred = Y_pred_array[()].astype(float)
	global gate_slider

	gate_slider = False
	client.send_message("prediction/address", Y_pred.item(0))

def SwitchHandler(address, *args) :
	global gate_switch
	gate_switch = args[0]



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
dispatcher.map("/switch/address", SwitchHandler)

#creates a server
server = BlockingOSCUDPServer((ip, port), dispatcher)
while True :
	server.handle_request()
