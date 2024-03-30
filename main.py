import customtkinter as ctk
import ctypes
import time
import win32gui
import win32con
import json
from threading import Thread


user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)
windowList = []
selected_app = "0"
temp_win_height = 1080
temp_win_width = 1920

def enum_window_proc(hwnd, resultList):
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
        resultList.append((hwnd, win32gui.GetWindowText(hwnd)))

def update_window_list():
    global windowList

    while True:
        temp = []
        win32gui.EnumWindows(enum_window_proc, temp)

        if( windowList != temp ):
            try:
                panel.after(20, refresh_window_list)
            except:
                exit()

        windowList = temp
        time.sleep(2)

def refresh_window_list():
    global window_list_dropdown, windowList
    windowList_strings = [f"{title[0:54]}" for hwnd, title in windowList] #Dirty truncate to resize drop-down UI
    window_list_dropdown.configure(values = windowList_strings)

def save_theme(theme):
    try:
        with open("theme_setting.json", "w") as f:
            json.dump({"theme": theme}, f)
    except:
        pass

def load_theme():
    try:
        with open("theme_setting.json", "r") as f:
            theme = json.load(f).get("theme", "System")
            return theme
    except:
        return "System"

def change_appearance_mode_event(new_appearance_mode: str):
    ctk.set_appearance_mode(new_appearance_mode)
    save_theme(new_appearance_mode)

def combo_answer(choice):
    global selected_app 
    selected_app = choice

def make_borderless():
    global selected_app, windowList, temp_win_height, temp_win_width
    
    hwnd = None
    for win_hwnd, win_title in windowList:
        if win_title.startswith(selected_app):
            hwnd = win_hwnd
            break
    
    if hwnd is None:
        return
    
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    temp_win_height = bottom - top
    temp_win_width = right - left

    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE) & ~(win32con.WS_CAPTION)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

    win32gui.MoveWindow(hwnd, 0, 0, screen_width, screen_height, True)
    win32gui.SetWindowPos(hwnd, None, 0, 0, screen_width, screen_height, win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)

def restore_window():
    global selected_app, windowList, temp_win_height, temp_win_width
    
    hwnd = None
    for win_hwnd, win_title in windowList:
        if win_title.startswith(selected_app):
            hwnd = win_hwnd
            break
    
    if hwnd is None:
        return
    
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE) | win32con.WS_CAPTION | win32con.WS_SYSMENU | win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 350, 200, temp_win_width, temp_win_height, win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)

saved_theme = load_theme()
ctk.set_appearance_mode(saved_theme)
ctk.set_default_color_theme("blue")  # Themes: "blue" / "green" / "dark-blue"

panel = ctk.CTk()
panel.geometry("400x320+"+ str(int(screen_width/2) - 200) + '+' + str(int(screen_height/2) - 200))
panel.resizable(False, False)
panel.title('NoMoreBorder')


label = ctk.CTkLabel(panel, text="Display Resolution is " + str(screen_width) + 'x' + str(screen_height), font = ("Helvetica", 20))
label.pack(pady=20)

window_list_dropdown = ctk.CTkComboBox(panel, values = ["Select Application"], width = 400, command = combo_answer)
window_list_dropdown.pack(padx=20, pady=(0, 10))

buttons_frame = ctk.CTkFrame(panel)
buttons_frame.pack(pady=10)

submit_button = ctk.CTkButton(buttons_frame, text="Make it Borderless", command = make_borderless)
submit_button.grid(row=0, column=0, padx=5)

undo_button = ctk.CTkButton(buttons_frame, text="Undo Lmao!", command = restore_window)
undo_button.grid(row=0, column=1, padx=5)

toggle_mode = ctk.CTkLabel(panel, text="Appearance Mode:", anchor="w")
toggle_mode.pack(padx=20, pady=(10, 0))

toggle_mode_options = ctk.CTkOptionMenu(panel, values=[ "System", "Light", "Dark" ], command = change_appearance_mode_event)
toggle_mode_options.pack(padx=20, pady=(10, 0))
toggle_mode_options.set(saved_theme)

Thread(target = update_window_list).start()

# panel.attributes('-topmost', True)
panel.mainloop()

