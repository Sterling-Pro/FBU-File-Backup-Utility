## Instructions 
To back up all files and/or folders in a working directory:
1. Place the `fbu.pyw` file in the directory, and open it - alternatively uncheck the "Use Working Directory" Box and you can specify any directory to copy from without placing the .pyw file in the input folder.
2. Select up to 3 backup destinations
3. Press "Backup Files + Folders" to initiate the backup
  - If you wish for the program to remember which destinations you chose and re-use them by default, click on "Save Destinations". This will create a .JSON file named 'directorypull.JSON' which stores the selected destination directories for later use. 
  - It will also create a log file (toggleable in the GUI) inside of a folder in the working directory called "backup_logs" (on by default, and will create the folder upon opening the program)


Image of GUI:
![image](https://github.com/user-attachments/assets/a5337deb-95be-4821-9b9d-73e5a128ec30)

## Key Technical Features:

* Flexible Source Selection:
** Toggle between working directory and user-specified source
** Utilizes os.getcwd() for current directory and filedialog.askdirectory() for custom selection
* Multi-Destination Backup:
** Supports up to three concurrent backup destinations
** Destination paths stored in JSON for persistence between sessions
* Comprehensive File Handling:
** Recursively processes directories using os.walk()
** Maintains source directory structure in backups
* Progress Monitoring:
** Dual progress bars for overall and per-file progress
** Implemented using CustomTkinter's CTkProgressBar
* Logging System:
** Real-time logging to GUI and optional file logging
* Timestamp-based log files for easy tracking
    ** Error Handling:
        *** Try-except blocks for robust error management
        *** User notifications via messagebox for critical issues
    ** Resource Management:
        *** Pre-backup space checks using shutil.disk_usage() or os.statvfs()
        *** Size calculations in MB for user-friendly reporting
    ** Multithreading:
        *** Backup operations run in separate threads to maintain GUI responsiveness

  # Libraries used for FBU
* tkinter
* customtkinter
* os
* shutil
* json
* threading
* platform
* datetime


**I AM NOT RESPONSIBLE FOR YOUR MISUSE OF THE PROGRAM AND FOR ANY LOST FILES. USE THE PROGRAM CAREFULLY AND REVIEW THE CODE BEFORE USING ON IMPORTANT FILES, THANK YOU.**
