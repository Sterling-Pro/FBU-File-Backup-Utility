# version 1.0.7
# author Sterling-Pro

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter
import os
import shutil
import json
import threading
import platform
from datetime import datetime

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")

class BackupGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Folder Backup Utility v1.0.7")
        self.geometry("900x600")
        self.iconbitmap("fbuicon.ico")  # Set the icon to "fbuicon.ico" in the working directory
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.json_file = 'directorypull.json'
        self.destinations = ["", "", ""]
        self.entries = []
        self.load_destinations()
        self.create_widgets()

    def create_widgets(self):
        # Top frame for destinations
        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(self.top_frame, text="Backup Destinations", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10))
        for i in range(3):
            customtkinter.CTkLabel(self.top_frame, text=f"Destination {i+1}:").grid(row=i+1, column=0, padx=5, pady=5, sticky="e")
            entry = customtkinter.CTkEntry(self.top_frame, width=300)
            entry.grid(row=i+1, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, self.destinations[i])
            self.entries.append(entry)
            customtkinter.CTkButton(self.top_frame, text="Browse", width=80, command=self.create_browse_command(i), fg_color="silver", text_color="black").grid(row=i+1, column=2, padx=5, pady=5)

        # Main content frame
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Log box
        self.log_box = customtkinter.CTkTextbox(self.main_frame, wrap="word")
        self.log_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.log_box.configure(state="disabled")

        # Bottom frame for buttons and progress bars
        self.bottom_frame = customtkinter.CTkFrame(self)
        self.bottom_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)
        customtkinter.CTkButton(self.bottom_frame, text="Save Destinations", command=self.save_destinations, fg_color="silver", text_color="black").grid(row=0, column=0, padx=5, pady=10)
        customtkinter.CTkButton(self.bottom_frame, text="Backup Files", command=lambda: self.start_backup('files'), fg_color="silver", text_color="black").grid(row=0, column=1, padx=5, pady=10)
        customtkinter.CTkButton(self.bottom_frame, text="Backup Folders", command=lambda: self.start_backup('folders'), fg_color="silver", text_color="black").grid(row=0, column=2, padx=5, pady=10)
        customtkinter.CTkLabel(self.bottom_frame, text="Overall Progress:").grid(row=1, column=0, columnspan=3, pady=(10, 0))
        self.overall_progress_bar = customtkinter.CTkProgressBar(self.bottom_frame)
        self.overall_progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")
        customtkinter.CTkLabel(self.bottom_frame, text="Current File Progress:").grid(row=3, column=0, columnspan=3, pady=(10, 0))
        self.current_file_progress_bar = customtkinter.CTkProgressBar(self.bottom_frame)
        self.current_file_progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")
        self.logging_enabled = tk.BooleanVar(value=True)
        customtkinter.CTkCheckBox(self.bottom_frame, text="Enable Logging", variable=self.logging_enabled).grid(row=5, column=0, columnspan=3, pady=10)
        self.setup_log_file()

    def setup_log_file(self):
        log_directory = "backup_logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        log_filename = f"backup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.log_file_path = os.path.join(log_directory, log_filename)
        if self.logging_enabled.get():
            with open(self.log_file_path, 'w') as f:
                f.write(f"Backup started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def create_browse_command(self, index):
        return lambda: self.browse_directory(index)

    def browse_directory(self, index):
        directory = filedialog.askdirectory()
        if directory:
            self.destinations[index] = directory
            self.entries[index].delete(0, tk.END)
            self.entries[index].insert(0, directory)

    def save_destinations(self):
        for i in range(3):
            self.destinations[i] = self.entries[i].get()
        with open(self.json_file, 'w') as f:
            json.dump(self.destinations, f)
        self.log_message("Destinations saved successfully!")

    def load_destinations(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as f:
                self.destinations = json.load(f)

    def start_backup(self, backup_type):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        threading.Thread(target=self.backup_operation, args=(backup_type,), daemon=True).start()

    def log_message(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.update_idletasks()
        if self.logging_enabled.get():
            with open(self.log_file_path, 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

    def get_directory_size(self, directory):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size / (1024 * 1024)  # Convert to megabytes

    def get_free_space(self, directory):
        if platform.system() == 'Windows':
            free_bytes = shutil.disk_usage(directory).free
        else:
            st = os.statvfs(directory)
            free_bytes = st.f_bavail * st.f_frsize
        return free_bytes / (1024 * 1024)  # Convert to megabytes

    def get_all_files(self, directory):
        all_files = []
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                all_files.append(os.path.join(dirpath, f))
        return all_files

    def copy_file_with_progress(self, src, dst):
        total_size = os.path.getsize(src)
        copied_size = 0
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            while True:
                buf = fsrc.read(1024 * 1024)  # Read in 1MB chunks
                if not buf:
                    break
                fdst.write(buf)
                copied_size += len(buf)
                self.current_file_progress_bar.set(copied_size / total_size)
                self.update_idletasks()

    def backup_operation(self, backup_type):
        active_destinations = [dest for dest in self.destinations if dest]
        if not active_destinations:
            messagebox.showwarning("Warning", "Please select at least one destination directory.")
            return
        working_directory_size = self.get_directory_size('.')
        self.log_message(f"Working directory size: {working_directory_size:.2f} MB")
        for destination in active_destinations:
            free_space = self.get_free_space(destination)
            self.log_message(f"Available space on {destination}: {free_space:.2f} MB")
            if working_directory_size > free_space:
                messagebox.showwarning("Warning", f"Not enough space on {destination}. Required: {working_directory_size:.2f} MB, Available: {free_space:.2f} MB")
                return
        if backup_type == 'files':
            items = [f for f in os.listdir('.') if os.path.isfile(f)]
        else:  # folders
            items = self.get_all_files('.')
        if not items:
            self.log_message(f"No {backup_type} found in the current directory.")
            return
        total_items = len(items) * len(active_destinations)
        items_copied = 0
        for item in items:
            self.log_message(f"Processing: {item}")
            for destination in active_destinations:
                try:
                    dest_path = os.path.join(destination, os.path.relpath(item, '.'))
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    self.copy_file_with_progress(item, dest_path)
                    items_copied += 1
                    self.overall_progress_bar.set(items_copied / total_items)
                    self.log_message(f" Copied to: {destination}")
                except Exception as e:
                    error_message = f"Failed to copy {item} to {destination}. Error: {str(e)}"
                    self.log_message(f" Error: {error_message}")
                    messagebox.showerror("Error", error_message)
        self.current_file_progress_bar.set(0)
        self.update_idletasks()
        self.log_message(f"{backup_type.capitalize()} backup complete. {items_copied} out of {total_items} items copied successfully.")
        self.log_message("Backup completed")
        self.overall_progress_bar.set(1)

if __name__ == "__main__":
    app = BackupGUI()
    app.mainloop()
