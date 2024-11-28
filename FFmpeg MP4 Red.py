import customtkinter
import os
import sys
import subprocess
import re
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
from PIL import Image, ImageTk

# Initialize CustomTkinter
customtkinter.set_appearance_mode("dark")  # Dark mode
customtkinter.set_default_color_theme("dark-blue")

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller. """
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    full_path = os.path.join(base_path, relative_path)
    
    # Debugging: print the path to make sure it is correct
    print(f"Icon path: {full_path}")
    
    return full_path

def set_icon(window):
    icon_path = resource_path("duck.ico")
    
    if os.path.exists(icon_path):
        window.iconbitmap(icon_path)  # Tkinter's iconbitmap method
    else:
        print(f"Error: Icon file not found: {icon_path}")

def select_input_file():
    """Allow the user to select the input file."""
    file = filedialog.askopenfilename(title="Select Input File", filetypes=[("Video files", "*.mp4"), ("All files", "*.*")])
    if file:
        input_file_var.set(file)

def sanitize_filename(filename):
    """Replace spaces and special characters with safe alternatives."""
    return re.sub(r'[^\w\-.]', '_', filename)

def select_output_directory():
    folder = filedialog.askdirectory(title="Select Output Folder")
    if folder:
        output_folder_var.set(folder)

def toggle_loading(state):
    if state:
        loading_label.grid(row=6, column=0, columnspan=2, pady=10)  # Show loading indicator
    else:
        loading_label.grid_remove()  # Hide loading indicator

def run_ffmpeg():
    def process():
        toggle_loading(True)  # Show loading indicator
        input_file = input_file_var.get()
        crf_value = crf_var.get()
        save_to_different_location = save_to_different_location_var.get()
        overwrite_original = overwrite_original_var.get()

        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist.")
            toggle_loading(False)
            return

        if save_to_different_location:
            output_folder = output_folder_var.get()
            if not output_folder:
                messagebox.showerror("Error", "Please select an output folder.")
                toggle_loading(False)
                return
            output_file = os.path.join(output_folder, os.path.basename(input_file))
        else:
            output_file = input_file

        if not overwrite_original:
            directory, filename = os.path.split(output_file)
            filename = f"ffmpeg-red-{filename}"
            output_file = os.path.join(directory, filename)

        command = f'ffmpeg -i "{input_file}" -vcodec libx264 -crf {crf_value} "{output_file}"'

        try:
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Get original and new file sizes
            original_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
            new_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            change_percentage = ((original_size - new_size) / original_size) * 100
            messagebox.showinfo("Success", f"File processed successfully:\n{output_file}\n\n"
                                          f"Original file size: {original_size:.2f} MB\n"
                                          f"New file size: {new_size:.2f} MB\n"
                                          f"Change: {change_percentage:.2f}%")
            input_file_var.set('')  # Clear input field after success
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred:\nCommand: {command}\n{e}")
        finally:
            toggle_loading(False)  # Hide loading indicator

    # Run the process in a separate thread
    threading.Thread(target=process).start()

def show_success_dialog(output_file, original_size, new_size, size_difference):
    """Display a custom success dialog with file details and a 'Show in folder' button."""
    dialog = customtkinter.CTkToplevel(root)
    dialog.title("Processing Complete")
    dialog.geometry("400x250")
    dialog.resizable(False, False)

    # Add details to the dialog
    message_label = customtkinter.CTkLabel(
        dialog,
        text=(
            f"File processed successfully!\n\n"
            f"Original file size: {original_size:.2f} MB\n"
            f"New file size: {new_size:.2f} MB\n"
            f"Change: {size_difference:.2f}%"
        ),
        font=("Segoe UI", 12),
        justify="left"
    )
    message_label.pack(pady=10, padx=20)

    # Add buttons
    button_frame = customtkinter.CTkFrame(dialog)
    button_frame.pack(pady=20, fill="x")

    # OK Button
    ok_button = customtkinter.CTkButton(
        button_frame,
        text="Ok",
        command=dialog.destroy,
        font=("Segoe UI", 12, "bold"),
        corner_radius=5,
        fg_color="#107a2a",
        hover_color="#055b16",
        text_color="white"
    )
    ok_button.pack(side="left", padx=20)

    # Show in Folder Button
    def open_in_folder():
        if os.name == "nt":  # Windows
            os.startfile(os.path.dirname(output_file))
        elif os.name == "posix":  # macOS or Linux
            webbrowser.open(f"file://{os.path.dirname(output_file)}")
    
    show_button = customtkinter.CTkButton(
        button_frame,
        text="Show in folder",
        command=open_in_folder,
        font=("Segoe UI", 12, "bold"),
        corner_radius=5,
        fg_color="#cc461b",
        hover_color="#66230d",
        text_color="white"
    )
    show_button.pack(side="right", padx=20)

    # Center the dialog on the screen
    dialog.grab_set()
    dialog.transient(root)
    dialog.wait_window()

root = customtkinter.CTk()
root.title("FFmpeg MP4 Video File Size Reducer")
root.geometry("500x410")
root.resizable(False, False)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)

set_icon(root)

input_file_var = customtkinter.StringVar()
output_folder_var = customtkinter.StringVar()
crf_var = customtkinter.IntVar(value=20)
save_to_different_location_var = customtkinter.BooleanVar(value=False)
overwrite_original_var = customtkinter.BooleanVar(value=False)

# Create frames
frame_input = customtkinter.CTkFrame(root)
frame_input.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

frame_output = customtkinter.CTkFrame(root)
frame_output.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

# Input file section
input_label = customtkinter.CTkLabel(frame_input, text="Input file", font=("Segoe UI", 12, "bold"))
input_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
input_entry = customtkinter.CTkEntry(frame_input, textvariable=input_file_var, width=300, font=("Segoe UI", 12))
input_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

# Browse button for "Input file"
input_button = customtkinter.CTkButton(frame_input, 
                                       text="Browse", 
                                       command=select_input_file, 
                                       font=("Segoe UI", 12, "bold"),
                                       corner_radius=5, 
                                       fg_color="#cc461b",
                                       hover_color="#66230d",
                                       text_color="white")
input_button.grid(row=1, column=1, padx=10, pady=5)

# CRF slider and value display
crf_label = customtkinter.CTkLabel(root, text="CRF Value (18-25):", font=("Segoe UI", 12, "bold"))
crf_label.grid(row=2, column=0, padx=15, pady=5, sticky="w")

# CRF value label
crf_value_label = customtkinter.CTkLabel(root, text=str(crf_var.get()), font=("Segoe UI", 12, "bold"))
crf_value_label.grid(row=2, column=0, padx=120, pady=5, sticky="w")

# CRF slider
crf_slider = customtkinter.CTkSlider(root, from_=18, to=25, number_of_steps=7,
                                     command=lambda value: (crf_var.set(round(float(value))),
                                                            crf_value_label.configure(text=str(round(float(value))))))
crf_slider.configure(button_color="#cc461b")
crf_slider.configure(button_hover_color="#66230d")
crf_slider.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

# Overwrite checkbox
overwrite_original_check = customtkinter.CTkCheckBox(root, text="Overwrite original file?", variable=overwrite_original_var, font=("Segoe UI", 12, "bold"))
overwrite_original_check.grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="w")
overwrite_original_check.configure(hover_color="#66230d", fg_color="#107a2a", checkbox_width=20, checkbox_height=20)

# Save to different location section
frame_save_location = customtkinter.CTkFrame(frame_output)
frame_save_location.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
frame_save_location.configure(fg_color="#212121")

# Label for 'Save to a different location?'
save_location_label = customtkinter.CTkLabel(frame_save_location, text="Save to a different location?", font=("Segoe UI", 12, "bold"))
save_location_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

# Checkbox for 'Save to a different location?'
save_location_check = customtkinter.CTkCheckBox(frame_save_location, text="", variable=save_to_different_location_var, font=("Segoe UI", 10, "bold"), command=lambda: toggle_output_options())
save_location_check.grid(row=0, column=1, sticky="w", padx=5, pady=5)
save_location_check.configure(hover_color="#66230d", fg_color="#107a2a", checkbox_width=20, checkbox_height=20)

# Output folder entry and browse button
output_entry = customtkinter.CTkEntry(frame_output, textvariable=output_folder_var, width=300, state="disabled", font=("Segoe UI", 12))
output_entry.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

# Browse button for "Output folder"
output_button = customtkinter.CTkButton(frame_output, 
                                        text="Browse", 
                                        command=select_output_directory, 
                                        state="disabled", 
                                        font=("Segoe UI", 12, "bold"),
                                        corner_radius=5, 
                                        fg_color="#cc461b",
                                        hover_color="#66230d",
                                        text_color="white")
output_button.grid(row=3, column=1, padx=10, pady=5)

# Run button
run_button = customtkinter.CTkButton(
    root, 
    text="Reduce it!", 
    command=run_ffmpeg, 
    font=("Segoe UI", 24, "bold"), 
    corner_radius=10, 
    fg_color="#cc461b", 
    text_color="white",
    hover_color="#66230d",
)
run_button.grid(row=5, column=0, pady=10, padx=10, sticky="e")

# Processing label
loading_label = customtkinter.CTkLabel(
    root,
    text="Processing...",
    font=("Segoe UI", 14, "bold"),
    text_color="#cc461b"
)
loading_label.grid(row=5, column=1, pady=10, sticky="w", padx=10)
loading_label.grid_remove()

def toggle_output_options():
    """Enable/Disable output directory options based on checkbox."""
    if save_to_different_location_var.get():
        output_entry.configure(state="normal")
        output_button.configure(state="normal")
    else:
        output_entry.configure(state="disabled")
        output_button.configure(state="disabled")

# Run the app
root.mainloop()