import glob, os, random, time
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from bing_image_downloader import downloader

def menu():
    settings = {
        "path": "C:/aircraft_recognition_program/images/",
        "slideshow_length": 30,
        "slideshow_time": 10,
        "instant_reveal": False,
        "intermission_time": 0,
        "variance": 2,
        "txt_file": get_txt("default.txt"),
        "text_size": 50,
        "extension": " airplane",
        "timer": True,
    }

    print("---Aircraft Recognition Program---")
    slideshowmenu(settings)

def slideshowmenu(settings):
    match input("competition, casual, learn or custom mode?\n").lower():
        case "competition":
            pass  # No changes needed, defaults are for competition mode
        case "casual":
            settings.update({
                "slideshow_length": 20,
                "intermission_time": 5,
                "extension": " aircraft",
            })
        case "learn":
            settings.update({
                "slideshow_length": -1,
                "slideshow_time": 9999,
                "instant_reveal": True,
                "timer": False,
                "txt_file": get_txt(),
                "extension": " aircraft",
            })
        case "test":
            settings.update({
            "slideshow_length": 3,
            "slideshow_time": 2,
            "instant_reveal": True,
            "intermission_time": 2,
            })
        case _:
            if input("Reveal answers immediately y/n\n").lower() == "y": instant_reveal = True
            else: instant_reveal = False
            if input("Visible countdown timer y/n\n").lower() == "y": timer = True
            else: timer = False
            settings.update({
                "txt_file": get_txt(),
                "slideshow_length": int(input("Slide count (-1 will use entire list):\n")),
                "slideshow_time": int(input("Slide length (seconds):\n")),
                "instant_reveal": instant_reveal,
                "intermission_time": int(input("intermission length (seconds):\n")),
                "extension": (" " + input("Search modifier: e.g top view, in flight, [or leave blank]\n")).rstrip(),
                "timer": timer,
            })

    slideshow(**settings)

def get_txt(file):
    if os.path.exists(file): return file
    elif not file: get_txt(input("TXT list choice:" + str(glob.glob("*.txt")) + "\n"))
    elif glob.glob("*.txt") == []: crash("No txt lists found.")
    else:
        print("Failed to find",file)
        while os.path.exists(file) == False:
            file = input("Choose a TXT list: " + str(glob.glob("*.txt")) + "\n")
        return file
    
def crash(reason):
    print("Program shutting down. Reason:",reason)
    time.sleep(5)
    os._exit(0)

def slideshow(path,slideshow_length,slideshow_time,instant_reveal,intermission_time,variance,txt_file,text_size,extension,timer):
    with open('paths.txt', 'w'): pass
    selected_aircraft = aircraft_selector(txt_file,slideshow_length)
    image_downloader(selected_aircraft,extension,path,variance)
    print("\n\n\n---------------------------------------------------------------------------------")
    input("Press enter to continue: ")
    run_slideshow(slideshow_time,path,text_size,timer,instant_reveal,selected_aircraft,intermission_time,extension)
    show_list_of_aircraft(selected_aircraft,text_size)
    menu()

def aircraft_selector(txt_file,slideshow_length):
    with open(txt_file, 'r') as file:
        aircraft_list = file.read().splitlines()
    if slideshow_length <= len(aircraft_list) and slideshow_length > 0:
        selected_aircraft = random.sample(aircraft_list, slideshow_length)
        return selected_aircraft
    elif slideshow_length == -1:
        return aircraft_list
    else: print("INVALID SLIDESHOW LENGTH")

def image_downloader(selected_aircraft, extension, path, variance):
    for aircraft in selected_aircraft:
        query = aircraft + extension
        output_path = os.path.join(path, query)
        for _ in range(2):  # Try to download the image
            num_files_before = len(os.listdir(output_path)) if os.path.exists(output_path) else 0
            downloader.download(query, limit=variance, output_dir=path, adult_filter_off=False, force_replace=False, timeout=10, filter="photo", verbose=False)
            if num_files_before < len(os.listdir(output_path)): break
        else: print(f"Failed to download image for {query} after 2 attempts.")
        
def show_image(remaining_time,timer,instant_reveal,text_size,filename,image_path,intermission,intermission_time,slide_num):
    root = tk.Tk()
    root.title("Aircraft Image")
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}")  
    root.attributes("-topmost", True)
    if intermission: root.configure(bg='black')
    
    def close_window():
        root.destroy()

    if not intermission:
        img = Image.open(image_path)
        resize_image = img.resize((w, h))
        photo = ImageTk.PhotoImage(resize_image)
        label = ttk.Label(root, image=photo)
        label.pack(fill=tk.BOTH, expand=tk.YES)
        
    timer_label = ttk.Label(root, text=str(remaining_time), font=('Arial', text_size), foreground='orange')
    aircraft_label = ttk.Label(root, text=filename, font=('Arial', text_size), foreground='white', background='black')
    slide_label = ttk.Label(root, text=slide_num, font=('Arial', text_size), foreground='black', background='white')
    
    def place_labels():
        root.update()  # Update the window to get the correct dimensions
        if timer:
            timer_label.place(x=root.winfo_width()-100, y=20)
        else:
            timer_label.place_forget()
            
        if instant_reveal:
            if intermission:
                aircraft_label.place(x=w/2, y=h/2, anchor="center")
            elif intermission_time == 0:
                aircraft_label.place(x=w/2, y=35, anchor="center")
        else:
            aircraft_label.place_forget()

        if not intermission:
            slide_label.place(x=w/20, y=35, anchor="nw")
    
    def update_timer():
        nonlocal remaining_time  # Use nonlocal to modify the outer variable
        remaining_time -= 1
        timer_label.config(text=str(remaining_time))
        root.after(1000, update_timer)
    
    root.after(remaining_time*1000, close_window)

    place_labels()
    update_timer()

    root.mainloop()

def run_slideshow(slideshow_time, path, text_size, timer, instant_reveal, selected_aircraft, intermission_time, extension):
    slide_num = 1
    for aircraft in selected_aircraft:
        folder_path = os.path.join(path, aircraft + extension) # get the folder path for each aircraft
        images = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1] in (".png", ".jpg", ".jpeg")] # list the image files in the folder
        if not images: 
            print(f"Image not found: {aircraft}")
            continue

        image_path = os.path.join(folder_path, random.choice(images)) # get the full image path
        with open("paths.txt", "a") as f:
            f.write(image_path + "\n")
        
        show_image(slideshow_time, timer, instant_reveal, text_size, aircraft, image_path, False, intermission_time,slide_num)
        
        if intermission_time > 0: 
            show_image(intermission_time, timer, instant_reveal, text_size, aircraft, image_path, True, intermission_time,"")

        slide_num += 1

def open_image(photo_references, image_path, aircraft_name):
    try:
        root = tk.Toplevel()  # Use Toplevel instead of Tk
        root.title(f"{aircraft_name} - Image Viewer")

        image = Image.open(image_path)
        new_width = int(root.winfo_screenwidth() * 0.70)
        new_height = int(root.winfo_screenheight() * 0.70)
        image = image.resize((new_width, new_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=photo) # Display the image
        label.image = photo  # Keep a reference to the image to prevent garbage collection
        label.pack()
        photo_references.append(photo) # Store photo reference globally
        aircraft_label = tk.Label(root, text=aircraft_name, font=('Arial', 30)) # Display the aircraft name
        aircraft_label.pack()

        root.mainloop()

    except Exception as e: print(f"Error opening image {image_path} for aircraft {aircraft_name}: {e}")

def show_list_of_aircraft(selected_aircraft, text_size):
    def on_aircraft_click(event):
        index = listbox.nearest(event.y)
        if 0 <= index < len(selected_aircraft):
            selected_aircraft_name = selected_aircraft[index]  # Get the aircraft name
            with open("paths.txt") as file:
                paths = [path.strip() for path in file.readlines()]
                if index < len(paths):
                    pather = paths[index]  # Get the path at the clicked index
                    photo_references = []
                    open_image(photo_references, pather, selected_aircraft_name)
                else:
                    print(f"No path found for aircraft {selected_aircraft_name}")

    root = tk.Tk()
    root.title("List of Selected Aircraft")
    listbox = tk.Listbox(root, font=('Arial', text_size), selectbackground='lightblue', selectforeground='black')
    listbox.pack(fill=tk.BOTH, expand=tk.YES)
    
    for i, aircraft in enumerate(selected_aircraft, start=1):
        listbox.insert(tk.END, f"{i}. {aircraft}")  #index and full aircraft name for the answer list
    
    listbox.bind('<Double-1>', on_aircraft_click)  # Bind double click event to callback
    root.mainloop()

menu()