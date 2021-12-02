import threading
import socket
import json
import config

def set_relationship(relationship_list, services_list, relationship_name, thing_id):
    for j in relationship_list:
        if j["Name"] == relationship_name:
            if j["Thing ID"] == thing_id:
                if j["Type"] == "control":
                   print("control")
                   invoke_service(services_list, j["FS name"], j["Thing ID"])
                   print("first done")
                   invoke_service(services_list, j["SS name"], j["Thing ID"])
                   print("second done")
                if j["Type"] == "support":
                    print("support")
                    invoke_service(services_list, j["SS name"], j["Thing ID"])
                    print("second done")
                    invoke_service(services_list, j["FS name"], j["Thing ID"])
                    print("first done")
                if j["Type"] == "extend":
                    print("extend")
                    x = threading.Thread(target=invoke_service, args=(services_list, j["FS name"], j["Thing ID"]))
                    y = threading.Thread(target=invoke_service, args=(services_list, j["SS name"], j["Thing ID"]))
                    x.start()
                    y.start()
                    print("both done")
                if j["Type"] == "drive":
                    print("drive")
                    invoke_service_relationship_pipe(services_list, j["FS name"], j["SS name"], j["Thing ID"])
                if j["Type"] == "contest":
                    print("contest")
                    invoke_service(services_list, j["FS name"], j["Thing ID"])
                    print("first done")
                if j["Type"] == "interfere":
                    print("interfere")
                    invoke_service(services_list, j["SS name"], j["Thing ID"])
                    print("second done")

def invoke_service(services_list, service_name, thing_id):
    for j in services_list:
        if j["Name"] == service_name:
            if j["Thing ID"] == thing_id:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                json_call = {
                    "Tweet Type" : "Service call",
                    "Thing ID" : j["Thing ID"],
                    "Entity ID" : j["Entity ID"],
                    "Space ID" : j["Space ID"],
                    "Service Name" : j["Name"],
                    "Service Inputs" : "0"
                }
                print(json_call)
                json_call = json.dumps(json_call)
                clientSocket.connect((j["IP Address"],6668))
                print("connected")
                clientSocket.send(json_call.encode("utf-8"))
                print("sent")
                dataFromServer = clientSocket.recv(1024)
                print("service invoked")
                string_data = dataFromServer.decode('utf-8')
                string_data = json.dumps(string_data)
                json_data = json.loads(string_data)
                # this needed to happen twice for it to be a dict
                json_data = json.loads(json_data)
                # this is the service result (has "No Output" if it returned nothing)
                return_data = json_data["Service Result"]
                print(return_data)
                clientSocket.close()


def invoke_service_relationship_pipe(services_list, service_name, second_name, thing_id):
    return_data = 0
    for j in services_list:
        if j["Name"] == service_name:
            if j["Thing ID"] == thing_id:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                json_call = {
                    "Tweet Type" : "Service call",
                    "Thing ID" : j["Thing ID"],
                    "Entity ID" : j["Entity ID"],
                    "Space ID" : j["Space ID"],
                    "Service Name" : j["Name"],
                    "Service Inputs" : "0"
                }
                json_call = json.dumps(json_call)
                clientSocket.connect((j["IP Address"],6668))
                clientSocket.send(json_call.encode("utf-8"))
                dataFromServer = clientSocket.recv(1024)
                string_data = dataFromServer.decode('utf-8')
                string_data = json.dumps(string_data)
                json_data = json.loads(string_data)
                # this needed to happen twice for it to be a dict
                json_data = json.loads(json_data)
                # this is the service result (has "No Output" if it returned nothing)
                return_data = json_data["Service Result"]
    print("first done")
    for j in services_list:
        if j["Name"] == second_name:
            if j["Thing ID"] == thing_id:
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                if return_data == "No Output":
                    return_data = 0
                json_call = {
                    "Tweet Type" : "Service call",
                    "Thing ID" : j["Thing ID"],
                    "Entity ID" : j["Entity ID"],
                    "Space ID" : j["Space ID"],
                    "Service Name" : j["Name"],
                    "Service Inputs" : str(return_data)
                }
                json_call = json.dumps(json_call)
                clientSocket.connect((j["IP Address"],6668))
                clientSocket.send(json_call.encode("utf-8"))
                dataFromServer = clientSocket.recv(1024)
    print("second done")

def deploy_app(relationship_list, services_list, app_data):
    relation = False
    for task in app_data:
        relation = False
        for j in relationship_list:
            if j["Name"] == task[0]:
                if j["Thing ID"] == task[1]:
                    
                    set_relationship(relationship_list, services_list, task[0], task[1])
                    
                    relation = True
        if(relation == False):
            
            invoke_service(services_list, task[0], task[1])
            
        if(config.stop_var == True):
            config.stop_var = False
            return
        
                    