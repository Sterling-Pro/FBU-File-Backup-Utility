# RAW Code, feel free to edit it or build upon it.

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import os
import shutil
import json
import threading
import platform
from datetime import datetime

class BackupGUI:
    def __init__(self, master):
        self.master = master
        master.title("ALLBack File and Folder Backup Utility")
        master.geometry("600x700") 

        self.json_file = 'directorypull.json'
        self.destinations = ["", "", ""]
        self.entries = []
        self.load_destinations()

        tk.Label(master, text="Select up to 3 backup destinations:", font=("Arial", 12)).grid(row=0, column=0, columnspan=3, pady=10)

        for i in range(3):
            tk.Label(master, text=f"Destination {i+1}:", anchor="e", width=12).grid(row=i+1, column=0, padx=5, pady=5, sticky="e")
            entry = tk.Entry(master, width=50)
            entry.grid(row=i+1, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, self.destinations[i])
            self.entries.append(entry)
            tk.Button(master, text="Browse", width=10, command=self.create_browse_command(i)).grid(row=i+1, column=2, padx=5, pady=5)

        button_frame = tk.Frame(master)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        tk.Button(button_frame, text="Save Destinations", width=15, command=self.save_destinations).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Backup Files", width=15, command=lambda: self.start_backup('files')).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Backup Folders", width=15, command=lambda: self.start_backup('folders')).pack(side=tk.LEFT, padx=10)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(master, textvariable=self.status_var, font=("Arial", 10), wraplength=580).grid(row=5, column=0, columnspan=3, pady=10)

        
        self.log_box = scrolledtext.ScrolledText(master, height=10, width=70, wrap=tk.WORD)
        self.log_box.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.log_box.config(state=tk.DISABLED) 

       
        tk.Label(master, text="Overall Progress:", font=("Arial", 10)).grid(row=7, column=0, columnspan=3, pady=5)
        self.overall_progress_var = tk.DoubleVar()
        self.overall_progress_bar = ttk.Progressbar(master, variable=self.overall_progress_var, maximum=100)
        self.overall_progress_bar.grid(row=8, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        tk.Label(master, text="Current File Progress:", font=("Arial", 10)).grid(row=9, column=0, columnspan=3, pady=5)
        self.current_file_progress_var = tk.DoubleVar()
        self.current_file_progress_bar = ttk.Progressbar(master, variable=self.current_file_progress_var, maximum=100)
        self.current_file_progress_bar.grid(row=10, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(6, weight=1) 
       
        self.logging_enabled = tk.BooleanVar(value=True)
        tk.Checkbutton(master, text="Enable Logging", variable=self.logging_enabled).grid(row=11, column=0, columnspan=3, pady=5)

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
        self.status_var.set("Destinations saved successfully!")

    def load_destinations(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as f:
                self.destinations = json.load(f)

    def start_backup(self, backup_type):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.delete(1.0, tk.END)
        self.log_box.config(state=tk.DISABLED)
        threading.Thread(target=self.backup_operation, args=(backup_type,), daemon=True).start()

    def log_message(self, message):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)
        self.master.update_idletasks()

        if self.logging_enabled.get():
            with open(self.log_file_path, 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

    def get_directory_size(self, directory):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size / (1024 * 1024)

    def get_free_space(self, directory):
        if platform.system() == 'Windows':
            free_bytes = shutil.disk_usage(directory).free
        else:
            st = os.statvfs(directory)
            free_bytes = st.f_bavail * st.f_frsize
        return free_bytes / (1024 * 1024) 

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
                buf = fsrc.read(1024 * 1024)  
                if not buf:
                    break
                fdst.write(buf)
                copied_size += len(buf)
                self.current_file_progress_var.set((copied_size / total_size) * 100)
                self.master.update_idletasks()

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
        else: 
            items = self.get_all_files('.')

        if not items:
            self.status_var.set(f"No {backup_type} found in the current directory.")
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
                    self.overall_progress_var.set((items_copied / total_items) * 100)
                    self.log_message(f" Copied to: {destination}")
                except Exception as e:
                    error_message = f"Failed to copy {item} to {destination}. Error: {str(e)}"
                    self.log_message(f" Error: {error_message}")
                    messagebox.showerror("Error", error_message)

            
            self.current_file_progress_var.set(0)
            self.master.update_idletasks()

        self.status_var.set(f"{backup_type.capitalize()} backup complete. {items_copied} out of {total_items} items copied successfully.")
        self.log_message("Backup completed")
        self.overall_progress_var.set(100)

root = tk.Tk()
app = BackupGUI(root)
root.mainloop()
