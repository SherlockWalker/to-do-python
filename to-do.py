import datetime
import os #to clear screen
import time
import tkinter as tk

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

rt = open("todo.txt", "r+")
# Structure of a task:
# Done, priority, timelist, current duration, task
# Done can take on "FINISHED", "CURRENT", "PAUSED" and "UNFINISHED"
# Priority: "HIGH", "MID", "LOW"
# Timelist in the txt formatted in datetime epoch seconds like #129837,198273-1283;etc in one block.
#   and is supposed to reflect start/end times of sessions. If empty notate using #
# Duration always hours(h)-minutes(m), default is 0; keeps track of how long
# Task is the name of task

def load(desync=False):
    """
    Reloads directly from the file; disregards anything unupdated to the file.
    """
    global tasks, counter #So that you do not have to worry about using it elsewhere
    # [Processing!]
    tasks = {}
    counter = 0
    rt.seek(0) #Reset pointer
    for line in rt.readlines():
        arr = [0, 0, 0, 0]
        temp = line
        for i in range(4):
            temp = temp.partition(" ")
            arr[i] = temp[0]
            temp = temp[2]

        if temp[-1] == "\n": temp = temp[:-1]
        
        done = arr[0]
        priority = arr[1]      
        try: 
            timelist = [tuple(int(x) for x in frame.split(","))
                        for frame in arr[2].lstrip("#").split(";") if frame]
        except: timelist = []
        duration = 0
        if timelist:
            for frame in timelist[0:-1]:
                duration += frame[1] - frame[0]
            if len(timelist[-1]) == 2: duration += timelist[-1][1] - timelist[-1][0]
        counter += 1
        tasks[counter] = [done, priority, timelist, duration, temp]
    
        

def display(navID=None):
    """
    Displays the current task list.
    If the navID is specified then it will show in detail what the task is and its sessions.
    """
    global tasks
    clear()
    if navID and tasks.get(navID, 0):
        task = tasks[navID]
        print("[ SHERLOCK'S TASK LIST ]")
        print("Displaying task in detail:")
        print("({}) [ {} ] [ {} ]".format(navID, task[0], task[1]) + " -------˗ˏˋ ★ ˎˊ˗-------")
        print("    ✧", task[4])
        for key, timeframe in enumerate(task[2]):
            if len(timeframe) == 2:
                print("Session #{}: {} - {}; duration: {}h{}m{}s".format(key+1,
                datetime.datetime.fromtimestamp(timeframe[0]).strftime('%Y-%m-%d %H:%M:%S'),
                datetime.datetime.fromtimestamp(timeframe[1]).strftime('%Y-%m-%d %H:%M:%S'),
                (timeframe[1] - timeframe[0])//3600,
                (timeframe[1] - timeframe[0])%3600//60,
                (timeframe[1] - timeframe[0])%60
                ))
            else:
                print("Session #{}: {} - {}; duration: {}h{}m{}s, ongoing".format(key+1,
                datetime.datetime.fromtimestamp(timeframe[0]).strftime('%Y-%m-%d %H:%M:%S'),
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                (int(datetime.datetime.now().timestamp()) - timeframe[0])//3600,
                (int(datetime.datetime.now().timestamp()) - timeframe[0])%3600//60,
                (int(datetime.datetime.now().timestamp()) - timeframe[0])%60
                ))
    elif navID:
        display()
        print(f"\nNo task of ID {navID} exists.")
    else:
        print("[ SHERLOCK'S TASK LIST ]")
        # [Displaying!]
        if tasks:
            for key, task in tasks.items():
                # Done, priority, timelist, current duration, task
                print("({}) [ {} ] [ {} ]".format(key, task[0], task[1]) + " -------˗ˏˋ ★ ˎˊ˗-------")
                print("    ✧", task[4])

                duration = 0
                for timeframe in task[2]:
                    if len(timeframe) == 2: duration += timeframe[1] - timeframe[0]
                    else: duration += int(datetime.datetime.now().timestamp()) - timeframe[0]
                print("     ", "[Duration]: {}h{}m{}s".format(
                    duration//3600, duration%3600//60, duration%60))
        else:
            print("No tasks here! Try typing 'insert' to input new task.")

def update(): 
    global tasks
    threads = []
    temptasks, tempcounter = {}, 1
    for task in tasks.values():
        frames = ";".join(",".join(str(x) for x in frame) for frame in task[2])
        threads.append("{} {} {} {} {}".format(
            task[0], task[1], "#"+frames, str(task[3]), task[4]))
        
        temptasks[tempcounter] = task
        tempcounter += 1
    tasks = temptasks 
    
    wt = open("todo.txt", "w")
    for thread in threads:
        wt.write(thread+"\n")



# ----------
# Commands to change.
# [navID] denotes the navigation ID, [taskID] for the uniqueID if I can bring myself to do it
# Look at task (and its timeframes): look task [navID]
def look(navID): display(navID)

# Insert new task/Delete task: (ins/insert OR del/delete) task
def insert():
    """
    Next commands: type out one of these (optional)
        done priority task
    and then on the same line consecutively by that command
        done (FINISHED, CURRENT, PAUSED, UNFINISHED)
        priority (HIGH, MID, LOW)
        task (a line that contains the task)
    which you can continue adding on until you type anything that doesn't fit the pattern
    """
    global tasks, counter
    print("Type 'QUIT' anytime to abort insert operation.")
    def helper(s, option=""):
        while True:
            temp = input(f"Enter the task's {s} here" + (f" (Options: {"/".join(option)})" if option else "") +": ")
            t = temp.strip().lower()
            if t == "quit": raise Exception()
            elif t == "": display(); print("\nThat wasn't very useful!")
            elif option and t not in option: print("\nThat wasn't very useful!")
            else: return temp
    try:
        name = helper("name")
        priority = helper("priority", ["high", "mid", "low"])
        counter += 1
        tasks[counter] = ["UNFINISHED", priority.upper(), [], 0, name]
        update()
        display()
        print(f"\nInsertion of task #{counter} successful.")
    except: 
        display()
        print("\nInsertion aborted.")

# Delete task: del/delete [navID]
def delete(navID):
    """
    Deletes a task. 
    Always has confirmation Y/N to see if you really want to. 
    """
    global tasks
    if tasks.get(navID, 0):
        display(navID)
        confirmation = input("Are you really sure you want to delete this task? (Y/N)\n")
        if confirmation and confirmation[0].lower()=="y":
            name = tasks[navID][4]
            del tasks[navID]
            update()
            display()
            print(f"\nTask {navID}: '{name}' has been deleted.")
        else: display()
    else:
        display()
        print(f"\nProcess cannot be deleted: Task #{navID} does not exist.")


def start(navID): 
    global tasks
    now = int(datetime.datetime.now().timestamp())
    if tasks.get(navID, 0):
        task = tasks[navID]
        if task[2]:
            if len(task[2][-1]) == 1:
                display(navID); print("\nYou have already started task", f"{navID}.")
            else:
                tasks[navID][2].append((now,)); 
                tasks[navID][0] = "CURRENT"
                update()
                display(navID)
                print("Started task {} at {}".format(
                    navID,
                    datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
                ))
        else:
            tasks[navID][2].append((now,)); 
            tasks[navID][0] = "CURRENT"
            update()
            display(navID)
            print("Started task {} at {}".format(
                navID,
                datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
            ))
    else:
        display()
        print(f"\nProcess cannot be started: Task #{navID} does not exist.")

def pause(navID):
    global tasks
    now = int(datetime.datetime.now().timestamp())
    if tasks.get(navID, 0):
        task = tasks[navID]
        if task[2]:
            if len(task[2][-1]) == 2:
                display(navID)
                print("\nProcess cannot be stopped: You have already stopped task", f"{navID}.")
            else:
                tasks[navID][2][-1] = (task[2][-1][0], int(datetime.datetime.now().timestamp())); 
                tasks[navID][0] = "PAUSED"
                update()
                display(navID)
                print("Stopped task {} at {}".format(
                    navID,
                    datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
                ))
        else:
            display(navID); print(f"\nProcess cannot be stopped: Task {navID} was never started.")
    else:
        display()
        print(f"\nProcess cannot be stopped: Task #{navID} does not exist.")

def archive(navID):
    ra = open("todoArchive.txt", "a")
    global tasks
    if tasks.get(navID, 0):
        display(navID)
        confirmation = input("Are you really sure you want to archive this task? (Y/N)\n")
        if confirmation and confirmation[0].lower()=="y":
            name = tasks[navID][4]
            task = tasks[navID]
            frames = ";".join(",".join(str(x) for x in frame) for frame in task[2])
            ra.write("\n{} {} {} {} {}".format(
            task[0], task[1], "#"+frames, str(task[3]), task[4]))
            del tasks[navID]
            update()
            display()
            print(f"\nTask {navID}: '{name}' has been archived.")
        else: display()
    else:
        display()
        print(f"\nProcess cannot be deleted: Task #{navID} does not exist.")

def help(): 
    display()
    help = """
Commands to change.
[navID] denotes the navigation ID.
    - Look at tasks (and its timeframes): look [navID]
    - Insert new task: ins/insert
    - Delete task: del/delete [navID]
    - Modify task: mod/modify [navID]
    - Mark as done: done [navID]
    - Rescind done status: undone [navID]
    - Start/Pause task: (start OR pause/stop) [navID]
    - Archive a task: archive [navID] 
        [!] You can only archive and NEVER take out again
    - Sort task: sort task (priority OR status (finished/current/paused/unfinished) OR name)
    - Load (in the case where the list desyncs with the todo.txt list): load
    - Help: help / man [command] / manual [command]
    - End session: quit
"""
    print(help)

manual_dict = {
"look":"Look at tasks (and its timeframes): look [navID]",
"insert":"Insert new task: insert", 
"ins":"Insert new task (alias of insert): ins", 
"delete":"Delete task: delete [navID]",
"del":"Delete task (alias of delete): del [navID]",
"modify":"Modify task: modify [navID]",
"mod":"Modify task (alias of modify): mod [navID]",
"done":"Mark as done: done [navID]",
"undone":"Rescind done status: undone [navID]",
"start":"Start task: start [navID]",
"pause":"Pause/stop task: pause [navID]",
"stop":"Pause/stop task: stop [navID]",
"archive":"Archive a task: archive [navID]\n[!] You can only archive and NEVER take out again",
"sort":"Sort task: sort task (priority OR status (finished/current/paused/unfinished) OR name)",
"load":"Load (in the case where the list desyncs with the todo.txt list): load",
"help":"Gives a list of the basic commands: help",
"manual":"Gives a short manual of the needed command: manual [command]",
"man":"Gives a short manual of the needed command (alias of manual): man [command]",
"quit":"End session: quit"
}
def manual(command):
    if manual_dict.get(command, 0): 
        display()
        print("\n")
        print(manual_dict[command])
    else: confusion()

def done(navID): 
    global tasks
    if tasks.get(navID, 0):
        tasks[navID][0] = "FINISHED"
        update()
        display()
        print(f"\nTask #{navID} has been marked completed.") 
    else:
        display()
        print(f"\nProcess cannot be started: Task #{navID} does not exist.") 

def undone(navID):
    global tasks
    if tasks.get(navID, 0):
        tasks[navID][0] = "PAUSED"
        update()
        display()
        print(f"\nTask #{navID} has been marked completed.") 
    else:
        display()
        print(f"\nProcess cannot be started: Task #{navID} does not exist.") 

# Unimplemented, since I could just mod the txt file directly and felt no need for it
def modify(navID): pass

def confusion():
    display()
    print("\nSorry, I didn't know which command you were trying to do?")
    print("Type 'help' to get commands.")

load()
display()
print("\nType 'help' to get commands.")
while True:
    print("\nPS C:\\Users\\Sherlock\\To-Do>", end=" ")
    command = input().split()
    if len(command) == 1:
        c = command[0]
        if c in ["help", "man", "manual"]: help()
        elif c == "load": load(); display()
        elif c == "quit":
            update(); display(); print("\nGoodbye!"); exit()
        elif c in ["ins", "insert"]: insert()
        elif c == "update": update()
        else: confusion()
    elif len(command) == 2:
        c = command[0]
        if c == "sort": pass
        elif c in ["pause", "stop"]:
            if command[1].isnumeric(): pause(int(command[1]))
            else: pass #Should have been pause all tasks; I didn't need it
        elif c == "start": start(int(command[1]))
        elif c in ["man", "manual"]: manual(command[1].lower())
        elif not command[1].isnumeric(): confusion() #All of the below uses IDs
        elif c in ["del", "delete"]: delete(int(command[1]))
        elif c in ["mod", "modify"]: modify(int(command[1]))
        elif c == "look": look(int(command[1]))
        elif c == "done": done(int(command[1]))
        elif c == "archive": archive(int(command[1]))
        else: confusion()
    else:
        confusion()
