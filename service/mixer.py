import threading
import json
import time

import pixels as PX
import controller as CTL
import state as ST


status_path = "status.json"
cocktails_path = "cocktails.json"
workers = []

with open(status_path, "r") as status_file:
    status = json.load(status_file)
with open(cocktails_path, "r") as cocktails_file:
    cocktails = json.load(cocktails_file)

def fill(tray, cl):
    # 4 sec for 1 cl
    CTL.motor_on(tray)
    
    duration = cl*4
    
    start = time.time()
    while ((time.time()- start) < duration):

        if ST.cancel == True:
            CTL.motor_off(tray)
            # calculate the used cl if canceld
            time_taken = time.time()- start
            used_cl = time_taken/4
            status[tray]["capacity"] = status[tray]["capacity"] - used_cl
            return

        delay = 0
        next_time = time.time()
        while not ST.is_glass:
            CTL.motor_off(tray)
            
            if ST.cancel == True:
                time_taken = time.time()- start
                used_cl = time_taken/4
                status[tray]["capacity"] = status[tray]["capacity"] - used_cl
                return
      
            delay = time.time()-next_time
            
        CTL.motor_on(tray)
        start += delay
        time.sleep(0.1)
        
    time_taken = time.time()- start
    
    status[tray]["capacity"] = status[tray]["capacity"] - cl    
    CTL.motor_off(tray)

def search_for_drink(name):
    for tray_num, tray_val in status.items():
        if tray_val["drink"] == name:
            return tray_num

def mix_cocktail(cocktail):
    ingredients = []
    for drink in cocktails:
        if drink["title"] == cocktail:
            ingredients = drink["ingredients"]
            break

    if not ingredients:
        return"Error: cocktail could not be found"
   
    time_to_wait = 0
    mix_list = {}
    for ing in ingredients:
        tray = search_for_drink(ing["title"])
        cl = float(ing["cl"])

        if status[tray]["capacity"] < cl:
            return "Error: not enough " + status[tray]["drink"] + " in tray: " + tray

        # wait for the greatest cl
        if (cl * 4) > time_to_wait:
            time_to_wait = cl * 4
        
        mix_list[tray] = cl

    ST.making_cocktail = True
    ST.duration = time_to_wait
    pixel_thread = threading.Thread(target=PX.making_wheel)
    pixel_thread.start()
    workers.append(pixel_thread)
    for tray in mix_list:
        cl = mix_list[tray]
        thread = threading.Thread(target=fill, args=(tray, cl))
        thread.start()
        workers.append(thread)

    threading.Thread(target=ending_routine).start()

    return str(ST.duration)


def ending_routine():
    #pixels_thread = threading.Thread(target=PX.making_wheel)
    #pixels_thread.start()
    
    
    start = time.time()
    ST.remaining_time = ST.duration
    ST.time_taken = 0
    while ((time.time()- start) < ST.duration):
        if ST.cancel == True:
            break
        delay = 0
        next_time = time.time()
        while not ST.is_glass:
            if ST.cancel == True:
               break
            delay = time.time()-next_time
            #hier damit der wert immer aktualisiert bleibt
            #ST.time_taken += delay
            #ST.remaining_time += delay
        start += delay
        time.sleep(0.1)
        #hier muss muss man das delay was vorher addiert hat subtrahieren
        #ST.time_taken -= delay #weil es in der (time() - next-time) drin ist 
        ST.time_taken += (time.time() - next_time)
        ST.remaining_time += delay
        ST.remaining_time -= (time.time() - next_time)

        #print("taken " +  str(ST.time_taken))
        #print("remain " + str(ST.remaining_time))
        
    ST.remaining_time = 0
    ST.time_taken = 0

    for thread in workers:
        thread.join()

    #pixels_thread.join()
    
    with open(status_path, 'w') as status_file:
            json.dump(status, status_file)

    PX.blink_green()
    PX.half_green()
    
    ST.making_cocktail = False
    ST.duration = 0
    return "your cocktail is ready"


def load_drink(tray, drink, size, cl):
    status[tray]["drink"] = drink
    status[tray]["capacity"] = float(cl)
    status[tray]["size"] = float(size)
    with open(status_path, "w") as status_file:
        json.dump(status, status_file)

def fill_pipe(tray):
    CTL.motor_on(tray)
    pipe_time = status[tray]["pipe"]
    if pipe_time is not None:
        time.sleep(status[tray]["pipe"])
    CTL.motor_off(tray)

def search_cocktail(name):
    for drink in cocktails:
        if drink['title'] == name:
            return drink

def get_image_path(name):
    cocktail = search_cocktail(name)
    if cocktail is not None:
        return "images/" + cocktail['img_name'].split('/')[2]
    
def cocktail_info(name):
    for drink in cocktails:
        if drink['title'] == name:
            return drink
        
def init(init_status):
    for tray in status:
        if tray in init_status:
            status[tray]["drink"] = init_status[tray]["drink"]
            status[tray]["capacity"] = float(init_status[tray]["capacity"])
            status[tray]["size"] = float(init_status[tray]["size"])
             
            threading.Thread(target=fill_pipe, args=(tray,)).start()

    with open(status_path, 'w') as status_file:
        json.dump(status, status_file)
        
        
def get_status():
    return status

def makeables():
    drinks = {}
    for tray in status:
        drinks[status[tray]["drink"]] = status[tray]["capacity"]
    
    cocktails_list = []
    for entry in cocktails:
        name = entry["title"]

        is_makeable = True

        for ing in entry["ingredients"]:
            if ing["title"] not in drinks:
                is_makeable = False
                break
            
            if float(ing["cl"]) > drinks[ing["title"]]:
                is_makeable = False
                break
                
        if is_makeable: 
            cocktails_list.append({'title':entry['title'],'ingredients':entry['ingredients']})    
        
    return cocktails_list   
        
    

