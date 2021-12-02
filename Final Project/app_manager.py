import os
from os import listdir, remove
from os.path import isfile, join
from relationship_handler import *

def save_app(app_name, app_data): #saves app
    if not os.path.exists('apps'):
        os.mkdir('apps')
    filename = './apps/' + app_name
    file = open(filename, 'w')
    for i in app_data:
        file.write(str(i[0]))
        file.write("\n")
        file.write(str(i[1]))
        file.write("\n")

def savenontuple_app(app_name, app_data): #saves app from editor
    if not os.path.exists('apps'):
        os.mkdir('apps')
    filename = './apps/' + app_name
    file = open(filename, 'w')
    file.write(app_data)

def load_app_from_list(app_filename): #uploads app
    app_filename = './apps/' + app_filename
    file = open(app_filename, 'r')
    contents = file.readlines()
    clean_contents = []
    for i in contents:
        i = i.rstrip()
        clean_contents.append(i)
    print("contents:\n" + str(clean_contents))
    return clean_contents


def load_app(relationship_list, service_list, app_filename): #deploy app
    app_filename = './apps/' + app_filename
    file = open(app_filename, 'r')
    contents = file.readlines()
    tuple_list = []
    track = 0
    for i in range(0, int(len(contents)/2)):
        name = contents[track]
        track = track + 1
        thing_id = contents[track]
        track = track + 1
        name = name.rstrip()
        thing_id = thing_id.rstrip()
        new_tuple = (name, thing_id)
        tuple_list.append(new_tuple)
    
    deploy_app(relationship_list, service_list, tuple_list)


def delete_app(app_name): #delete app
    files = [f for f in listdir('./apps/') if isfile(join('./apps/', f))]
    is_file = False
    for f in files:
        if f == app_name:
            is_file = True
    if is_file:
        app_name = './apps/' + app_name
        os.remove(app_name)
    else:
        print("not a file")
