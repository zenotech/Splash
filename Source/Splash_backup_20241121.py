# Standard library imports 
import os
import re
import vtk
import signal
import time
import datetime
import glob
import shutil # For file copying
import threading # For running a process in a separate thread
import tkinter as tk
import webbrowser
import subprocess
import tkinter.simpledialog 

# Importing third-party libs 
from tkinter import ttk, filedialog, font, messagebox, simpledialog, colorchooser
from PIL import Image, ImageTk
from tkinter import scrolledtext
from tkinter import Listbox
from collections import defaultdict # Import defaultdict | for mesh parameters 
from tkinter.colorchooser import askcolor
from tkinter.font import Font
from STLProcessor import STLProcessor

# Importing local classes
from SearchWidget import SearchWidget  # Import the SearchWidget class from the other file
from ReplaceProperties import ReplacePropertiesPopup
from ReplaceMeshParameters import ReplaceMeshParameters
from ReplaceControlDictParameters import ReplaceControlDictParameters
from ReplaceSimulationSetupParameters import ReplaceSimulationSetupParameters

# Define menu functions
def edit_undo():
    print("In the works")

def show_help():
    print("Show Help")

def view_status_bar():
    print("Status Bar View")

def view_toolbar():
    print("Toolbar View")
#______________
#
# TERMINAL APP 
#______________           

class Splash:  
    def __init__(self, root):
        self.root = root
        self.root.config(background="white")
        self.root.title("Splash - v0.2")
        
        # Get the absolute path of the script directory
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Convert relative path to absolute path
        icon_path = os.path.join(base_path, "../Resources/Logos/simulitica_icon_logo.png")

        # Ensure the path is absolute
        icon_path = os.path.abspath(icon_path)

        # Load the icon
        if os.path.exists(icon_path):  # Check if the file exists before loading
            icon_image = tk.PhotoImage(file=icon_path)
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon_image)
        else:
            print(f"Error: Icon file not found at {icon_path}")
    
        # Set the window icon using a PhotoImage
        #icon_path = "../Resources/Logos/simulitica_icon_logo.png"  # Replace with the actual path to your icon file
        icon_image = tk.PhotoImage(file=icon_path)
        self.root.tk.call('wm', 'iconphoto', self.root._w, icon_image)
        
        # ======================= Create a menubar ----------------------------->
        menubar = tk.Menu(root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New File", command=self.file_new)
        file_menu.add_command(label="Create Case", command=self.case_creator)
        file_menu.add_command(label="Analyze STL file", command=self.process_stl)
        file_menu.add_command(label="Profile theme", command=self.change_theme)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=edit_undo)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Status Bar", command=view_status_bar)
        toolbar_submenu = tk.Menu(view_menu, tearoff=0)
        toolbar_submenu.add_command(label="Show Toolbar", command=view_toolbar)
        toolbar_submenu.add_command(label="Hide Toolbar", command=lambda: print("Hide Toolbar"))
        view_menu.add_cascade(label="Toolbar", menu=toolbar_submenu)
        view_menu.add_command(label="Results Panel", command=self.toggle_results_panel)
        menubar.add_cascade(label="View", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about_message)
        help_menu.add_command(label="Manual", command=self.splash_online_manual, background="black", foreground="cyan")
        help_menu.add_command(label="Splash-GPT", command=self.splash_GPT_page, background="black", foreground="pink")
        help_menu.add_command(label="Report an issue", command=self.open_contact_page, background="black", foreground="red")
        help_menu.add_command(label="Support Splash", command=self.support_Splash, background="black", foreground="lightgreen")
        help_menu.add_command(label="Cloud HPC", command=self.cloud_HPC, background="black", foreground="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Display the menu bar
        root.config(menu=menubar)
        # ======================= Create a menubar -----------------------------<

        # ============= Time Recorder =============>
        # License parameters
        self.start_time = time.time()
        self.license_start_date_file = "license_start_date.txt"  # File to store the start date
        self.license_duration = 1 * 365 * 24 * 3600  # 1 year in seconds
        #self.license_duration = 14 * 24 * 3600  # 14 days in seconds
        self.notice_period_before_end = 15 * 24 * 3600  # Notify 15 days before the license expires
        self.elapsed_time_file = ".elapsed_time.txt"  # Making the file name start with a dot to "hide" it in Unix/Linux
        
        # Create a label for the "Elapsed Time" text
        self.elapsed_time_label = tk.Label(root, text="Elapsed Time", font=("Helvetica", 24), bg="white", fg="darkblue")
        self.elapsed_time_label.grid(row=0, column=7, sticky="nsew")  # Updated to sticky="nsew" for dynamic resizing
        
        # Create a label for the timer
        self.timer_label = tk.Label(root, text="00:00:00.0", font=("Helvetica", 35, "bold"), bg="white", fg="darkblue")
        self.timer_label.grid(row=1, column=7, sticky="nsew")  # Updated to sticky="nsew" for dynamic resizing
        
        # Start updating the timer
        self.update_timer()
        # ============= Time Recorder =============<
        
        # Display the main text box widget
        self.setup_ui()
        
        # Variable to track visibility state of the action bar
        self.show_first_column = True 

        # Add a background image
        self.add_bgImage()
        
        # Initialize the bg color of the 3D STL CAD
        self.bg_color_counter = 1
        
        # Bind the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Display a welcome message
        self.show_welcome_message()
        
        # Ensure that the column and row have weight to resize dynamically
        self.root.grid_columnconfigure(10, weight=1)  # Ensures that the column with index 10 resizes dynamically
        self.root.grid_rowconfigure(2, weight=1)  # Ensures that the row with index 2 (Elapsed Time label) resizes
        self.root.grid_rowconfigure(3, weight=1)  # Ensures that the row with index 3 (Timer label) resizes

        # Add logos
        self.add_logos()

        # ----------------------
        # Style of Action Panel 
        # ----------------------
        # Create a ttk.Style to configure buttons
        style = ttk.Style()
        style.configure(
            "TButton",
            padding=5,
            relief="flat",
            background="lightblue",
            foreground="black",
            font=("Arial", 12, "bold")  
        )
        
        # Initialize the STLProcessor
        self.stl_processor = STLProcessor(self)
        
        # Initialize geometry loaded flag and VTK visualization
        self.geometry_loaded = False
        self.selected_file_path = None  # Initialize selected file path
        self.vtk_figure = None
        self.vtk_canvas = None
        self.main_vtk_figure = None
        self.main_vtk_canvas = None
        self.current_view = "console"

        # Initialize status label early to prevent AttributeError
        self.status_label = ttk.Label(self.root, text="Initializing...")
        self.status_label.grid(row=21, column=1, columnspan=8, pady=1, padx=10, sticky="new")
        self.status_label.config(text="Ready to import geometry", font=("Helvetica", 12), background="white", foreground="darkblue")

        # Create a button to import a geometry file
        self.import_button = ttk.Button(self.root, text="Import Geometry", command=self.import_geometry)
        self.import_button.grid(row=0, column=0, pady=1, padx=10, sticky="nsew")
        
        # Create a mesh type variable (set it so "Cartesian" as a default)
        self.mesh_type_var = tk.StringVar(value="Cartesian")
        self.mesh_type = None
        
        # Create a button to create the mesh
        self.create_mesh_button = ttk.Button(self.root, text="Create Mesh", command=self.create_mesh)
        self.create_mesh_button.grid(row=1, column=0, pady=1, padx=10, sticky="nsew")
        
        # Create a button to load the case directory
        self.load_case_button = ttk.Button(self.root, text="Load Case", command=self.load_case)
        self.load_case_button.grid(row=2, column=0, pady=1, padx=10, sticky="nsew")
        
        # Create a button to initialize the command execution
        self.initialize_simulation_button = ttk.Button(self.root, text="Initialize Simulation", command=self.initialize_simulation)
        self.initialize_simulation_button.grid(row=3, column=0, pady=1, padx=10, sticky="nsew")
        
        # Create a button to configure the simulation settings before run
        self.configure_simulation_button = ttk.Button(self.root, text="Configure Simulation", command=self.open_simulation_setup_popup)
        self.configure_simulation_button.grid(row=4, column=0, pady=1, padx=10, sticky="nsew")

        # Create a button to run simulation
        self.run_simulation_button = ttk.Button(self.root, text="Run Simulation", command=self.run_simulation)
        self.run_simulation_button.grid(row=5, column=0, pady=1, padx=10, sticky="nsew")
        
        # Stop Simulation Button
        self.stop_simulation_button = ttk.Button(self.root, text="Stop Simulation", command=self.stop_simulation)
        self.stop_simulation_button.grid(row=6, column=0, pady=1, padx=10, sticky="nsew")
        
        # Create a button to plot results using xmgrace (2D Plotting)
        self.plot_results_xmgrace_button = ttk.Button(self.root, text="2D Plotting", command=self.plot_results_xmgrace)
        self.plot_results_xmgrace_button.grid(row=7, column=0, pady=1, padx=10, sticky="nsew")  # Changed sticky to "nsew" for dynamic resizing
        self.add_tooltip(self.plot_results_xmgrace_button, "Click to plot simulation results using xmgrace")

        # Configure the row where the 2D Plotting button is located to allow resizing
        self.root.grid_rowconfigure(7, weight=1)  # Ensure row 7 resizes

        # Create a button for post-processing
        self.paraview_button = ttk.Button(self.root, text="Post-processing", command=self.paraview_application)
        self.paraview_button.grid(row=8, column=0, pady=1, padx=10, sticky="nsew")

        # Configuring row and column weights to make window responsive
        no_global_columns = 5
        no_global_rows = 22  # Increased for better vertical spacing

        for i in range(no_global_rows):
            # More balanced weight distribution
            if i <= 9:  # Main visualization area gets moderate weight
                self.root.rowconfigure(i, weight=1, uniform="main_area")
            elif i in [10]:  # Control area gets minimal weight
                self.root.rowconfigure(i, weight=0, uniform="")
            elif i in [11, 12]:  # CLI area gets minimal weight
                self.root.rowconfigure(i, weight=0, uniform="")
            elif i in [13, 14, 15, 16]:  # Terminal output gets higher weight for visibility
                self.root.rowconfigure(i, weight=1, uniform="terminal_area")
            else:  # Footer areas get minimal weight
                self.root.rowconfigure(i, weight=0, uniform="")

        for i in range(no_global_columns):
            self.root.columnconfigure(i, weight=1, uniform="columns")
        
        # Set the initial size of the window to fit a small monitor
        self.root.geometry("1400x1000")  # Increased height for better vertical spacing

        # Centering the window on the screen:
        self.root.update_idletasks()  # Ensure window has been drawn
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create a button to execute commands to the terminal kernel
        self.execute_button = tk.Button(self.root, text="CLI", command=self.execute_command)
        self.execute_button.configure(relief="flat", background="lightblue", foreground="black", font=("Arial", 12, "bold"))
        self.execute_button.grid(row=12, column=1, pady=3, padx=1, sticky="new")  # Moved down to row 12
        self.add_tooltip(self.execute_button, "Click to run a terminal command")
        
        # Configure a smaller style for the button
        style = ttk.Style()
        style.configure("Small.TButton", font=("TkDefaultFont", 10), padding=3, background="lightblue")

        # Configure a custom style for the Entry widget
        style.configure('Professional.TEntry', 
                        foreground='lightblue', 
                        font=('Helvetica', 11, 'bold'), 
                        borderwidth=2, 
                        relief='flat',
                        padding=10)
        
        # Create an entry field for entering the commands by the user
        default_sentence = "top"  # Or "htop"
        self.entry = ttk.Entry(self.root, style='Professional.TEntry', width=18, foreground="lightblue", font=("Arial", 12, "bold"))
        self.entry.grid(row=11, column=1, pady=3, padx=1, sticky="sew")  # Moved down to row 11
        self.entry.insert(0, default_sentence)
        
        # Ensure the button and entry field can resize
        self.root.grid_rowconfigure(13, weight=1)  # Ensures the row for the execute button resizes dynamically
        self.root.grid_rowconfigure(14, weight=1)  # Ensures the row for the entry field resizes dynamically

# --------------->
#  Check buttons
# <--------------
        # Set different weights for the rows to control how they resize
        self.root.grid_rowconfigure(15, weight=0)  # Reset Profile Theme button's row gets some priority
        self.root.grid_rowconfigure(16, weight=0)  # Give less weight to the rows below so they shrink first
        self.root.grid_rowconfigure(17, weight=0)
        self.root.grid_rowconfigure(18, weight=0)
        
        # Create a Checkbutton for resetting profile theme to default
        self.reset_var = tk.BooleanVar()
        reset_checkbutton_style = ttk.Style()
        reset_checkbutton_style.configure("Custom.TCheckbutton", foreground="black", background="white")
        
        reset_checkbutton = ttk.Checkbutton(root, text="Reset Profile Theme", variable=self.reset_var, style="Custom.TCheckbutton", command=self.toggle_reset)
        reset_checkbutton.grid(row=15, column=0, padx=7, pady=1, sticky="nw")  # Moved to row 15
        
        # Create Checkbutton for monitoring simulation
        self.monitor_simulation_var = tk.BooleanVar()
        monitor_simulation_checkbutton = ttk.Checkbutton(root, text="Monitor Simulation", variable=self.monitor_simulation_var, command=self.toggle_monitor_simulation, style="Custom.TCheckbutton")
        monitor_simulation_checkbutton.grid(row=16, column=0, pady=1, padx=7, sticky="nsew")  # Moved to row 16
        
        # Create Checkbutton for monitoring simulation log
        self.monitor_simulationLog_var = tk.BooleanVar()
        monitor_simulationLog_checkbutton = ttk.Checkbutton(root, text="Simulation log", variable=self.monitor_simulationLog_var, command=self.toggle_simulation_results, style="Custom.TCheckbutton")
        monitor_simulationLog_checkbutton.grid(row=17, column=0, pady=1, padx=7, sticky="nsew")  # Moved to row 17

        # Create a Checkbutton using the custom style for showing/hiding the results section
        self.results_panel_var = tk.BooleanVar(value=True)  # Set to False so it starts unchecked
        toggle_visibility_button = ttk.Checkbutton(
            root, 
            text="Show Elapsed Time", 
            variable=self.results_panel_var, 
            command=self.toggle_results_panel, 
            style="Custom.TCheckbutton"
        )
        toggle_visibility_button.grid(row=18, column=0, pady=1, padx=7, sticky="nsew")  # Moved to row 18

        # Store initial profile theme values
        self.initial_font = self.text_box.cget("font")
        self.initial_foreground = self.text_box.cget("foreground")
        self.initial_background = self.text_box.cget("background")
        
        # Helper method to add text to terminal output
    def add_terminal_output(self, text, also_main_console=True):
        """Add text to the dedicated terminal output window and optionally to main console"""
        # Add to terminal output window
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.terminal_output.update_idletasks()
        
        # Also add to main console if requested
        if also_main_console:
            self.text_box.insert(tk.END, text)
            self.text_box.see(tk.END)
            self.text_box.update_idletasks()

    def clear_terminal_output(self):
        """Clear the terminal output window"""
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete(1.0, tk.END)
        self.terminal_output.config(state=tk.DISABLED)

        # Create a style for the progress bar
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", troughcolor="white", background="lightblue", thickness=10)

        # Create a progress bar with the custom style
        self.progress_bar_canvas = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=280,
            mode="indeterminate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar_canvas.grid(row=9, column=0, padx=10, pady=5, sticky="new")  # Move to row 9
        self.progress_bar_canvas_flag = True
        
        #----------Text Widget with Scrollbar-----------       
        # Add the search widget to the main app
        self.search_widget = SearchWidget(root, self.text_box)
        
        # Initialize variables for simulation thread
        self.simulation_thread = None
        self.simulation_running = False
        
        # Initialize the available fuels to choose from
        self.fuels = ["Propane", "Gasoline", "Ethanol", "Hydrogen", "Methanol", "Ammonia", "Dodecane", "Heptane"]
        
        # Define the fuel options
        fuels = ["Methanol", "Ammonia", "Dodecane"]
        
        # Create a StringVar to store the selected fuel
        self.selected_fuel = tk.StringVar()
        
        # Set a default value for the dropdown
        default_value = "Available fuel options"
        self.selected_fuel.set(default_value)
        
        # Create a label for status messages
        self.status_label_title = ttk.Label(self.root, text="")
        status_title = "Splash v0.2"
        self.status_label_title.grid(row=16, column=1, columnspan=1, pady=1, padx=10, sticky="nsew")  # Changed to sticky="nsew" for dynamic resizing
        self.status_label_title.config(text=status_title, font=("Helvetica", 14, "bold"), background="white", foreground="grey")
        
        # Separate the status bar 
        separator = tk.Frame(self.root, height=1, bg="darkred")
        separator.grid(row=15, column=1, columnspan=1, pady=(5, 1), padx=10, sticky="new")
        
        # Status label already initialized earlier - update position and text
        self.status_label.grid_forget()  # Remove from previous position
        self.status_label.grid(row=16, column=1, columnspan=8, pady=1, padx=10, sticky="new")
        default_status = "Start by importing your geometry or configuring an existing OpenFOAM case!"
        self.status_label.config(text=default_status, font=("Helvetica", 12), background="white", foreground="darkblue")
   
        # Other parameter initializations 
        self.selected_file_path = None
        self.selected_openfoam_path = None  
        self.selected_file_content = None
        self.mesh_dict_file_path = None
        self.control_dict_file_path = None
        self.selected_mesh_file_content = None
        self.selected_control_file_content = None
        self.geometry_dest_path = None
        self.control_dict_path = None 
        self.separateMeshLogFile = False
        self.openfoam_sourced = False
        self.caseMeshLogFile = False
        self.solverLogFile = False 
        self.geometry_loaded = False

        # Mesh parameters 
        self.mesh_params = ["minCellSize", "maxCellSize", "boundaryCellSize", "nLayers", "optimiseLayer", "untangleLayers", "thicknessRatio", 
                            "maxFirstLayerThickness", "nSmoothNormals", "maxNumIterations", "featureSizeFactor", "reCalculateNormals", 
                            "relThicknessTol", "restartFromLatestStep", "enforceGeometryConstraints"]
        
        self.control_dict_params = ["application", "startFrom", "startTime", "stopAt", "endTime", "deltaT", "writeControl", "writeInterval", 
                                    "purgeWrite", "writeFormat", "writePrecision", "timePrecision", "runTimeModifiable", "maxCo"]
        
        # Add header
        self.header = """/*--------------------------------*- C++ -*----------------------------------*\\
          =========                 |
          \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
           \\\\    /   O peration     | Website:  https://openfoam.org
            \\\\  /    A nd           | Version:  Splash v0.2
             \\\\/     M anipulation  |
        \\*---------------------------------------------------------------------------*/\n"""
        
        self.thermo_type_params = ["type", "mixture", "transport", "thermo", "equationOfState", "specie", "energy"]
        self.mixture_params = ["molWeight", "rho", "rho0", "p0", "B", "gamma", "Cv", "Cp", "Hf", "mu", "Pr"]


    # Creating an empty text file
    def file_new(self):
        # Define the path for the new file
        new_file_path = os.path.join(os.getcwd(), "new_file.txt")

        # Create a new empty text file
        with open(new_file_path, 'w') as new_file:
            new_file.write("")  # Writing an empty string (left for furture dev.)

        # Function to open the file in gedit in a separate thread
        def open_in_gedit():
            try:
                subprocess.run(["gedit", new_file_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to open gedit: {e}")

        # Start the open_in_gedit function in a new thread to avoid blocking the UI
        gedit_thread = threading.Thread(target=open_in_gedit)
        gedit_thread.start()
    
    def case_creator(self):
        """Launch the Case Creator GUI built with PySide."""
        # Script path for SplashCaseCreator
        script_path = os.path.abspath(os.path.join("CaseCreator", "SplashCaseCreator_gui.py"))

        try:
            print(f"Launching Case Creator at: {script_path}")
            # Set environment variable to force Qt to use X11
            env = os.environ.copy()
            env["QT_QPA_PLATFORM"] = "xcb"

            # Set the working directory to CaseCreator to ensure the .ui file can be accessed
            process = subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=os.path.abspath("CaseCreator")
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                print(f"Error launching Case Creator: {stderr.decode().strip()}")
                messagebox.showerror("Error", f"Case Creator failed to launch. See console for details.")
            else:
                print(f"Case Creator launched successfully: {stdout.decode().strip()}")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Script not found: {script_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Case Creator: {e}")
    # -------------- Main logos -------------------------->    
    def add_logos(self):
    
        # Create PhotoImage objects directly from image files
        base_path = os.path.dirname(os.path.abspath(__file__))

        self.logo_openfoam = tk.PhotoImage(file=os.path.abspath(os.path.join(base_path, "../Resources/Logos/openfoam_logo.png")))
        self.logo_simulitica = tk.PhotoImage(file=os.path.abspath(os.path.join(base_path, "../Resources/Logos/simulitica_logo.png")))

        #self.logo_openfoam = tk.PhotoImage(file="../Resources/Logos/openfoam_logo.png")
        #self.logo_simulitica = tk.PhotoImage(file="../Resources/Logos/simulitica_logo.png")
    
        # Resize images if needed
        self.logo_openfoam = self.logo_openfoam.subsample(3, 3)  # Restored to original size
        self.logo_simulitica = self.logo_simulitica.subsample(8, 8)  # Adjust the subsample as needed
    
        # Create the OpenFOAM logo as a clickable label (not a button) to avoid ghost button appearance
        self.OF_version_label = tk.Label(
            self.root,
            image=self.logo_openfoam,
            cursor="hand2",  # Make it clear it's clickable
            background="white",
            relief="flat",
            borderwidth=0
        )
        self.OF_version_label.grid(row=9, column=0, pady=3, padx=10, sticky="nsew")  # Increased pady from 1 to 3 and padx from 5 to 10 for consistent spacing
        
        # Bind click event to the label
        self.OF_version_label.bind("<Button-1>", lambda event: self.select_openfoam_version())



        # Add the Simulitica logo
        self.simLabel = tk.Label(self.root, image=self.logo_simulitica)
        self.simLabel.grid(row=10, column=0, pady=2, padx=10, sticky="nsew")  # Increased pady from 1 to 2 and padx from 5 to 10 for consistent spacing
        self.simLabel.configure(background="white")
    
        # Add copyright text
        self.copyright_label = ttk.Label(self.root, text="© 2023 Simulitica Ltd")
        self.copyright_label.grid(row=11, column=0, pady=2, padx=10, sticky="nsew")  # Increased pady from 1 to 2 and padx from 5 to 10 for consistent spacing
        self.copyright_label.configure(background="white", font="bold")
    # -------------- Main logos --------------------------<

    def process_stl(self):
        # Open file dialog to select STL file
        self.selected_file_path = filedialog.askopenfilename(title="Select STL File", filetypes=[("STL files", "*.stl")])
        if self.selected_file_path:
            self.stl_processor.process_stl(self.selected_file_path)
            messagebox.showinfo("Processing Complete", "STL analysis completed. Check the generated report.")
            
    def paraview_application(self):
        # This function will be executed in a separate thread to avoid blocking the main GUI thread
        def run_paraview():
            try:
                # Launch ParaView in a non-blocking way using Popen
                subprocess.Popen(["paraview"])
            except Exception as e:
                # Handle errors if ParaView fails to launch
                print(f"Error running ParaView: {e}")

        # Create a new thread to run the ParaView process
        paraview_thread = threading.Thread(target=run_paraview)

        # Set daemon to True so the thread will not block the application from closing
        paraview_thread.daemon = True

        # Start the thread, which will run ParaView in the background without blocking the main UI
        paraview_thread.start()

    # Toggle function for action bar visibility
    def toggle_results_panel(self):
        self.show_first_column = self.results_panel_var.get()  # Check the state of the variable

        # Toggle the visibility of buttons in the first column
        if self.show_first_column:
            # Show elements including car image
            self.elapsed_time_label.grid(row=0, column=7, sticky="nsew")
            self.timer_label.grid(row=1, column=7, sticky="nsew")
            # Always show car image when results panel is visible - don't hide it for VTK viewer
            self.splash_bgImage_label.grid(row=2, column=7, pady=5, padx=10, sticky="nsew", rowspan=6)
        else:
            # Hide elements
            self.elapsed_time_label.grid_remove()
            self.timer_label.grid_remove()
            self.splash_bgImage_label.grid_remove()

    def browse_directory(self):
        selected_file = filedialog.askopenfilename()

        if selected_file and os.path.basename(selected_file).startswith("physicalProperties"):
            self.selected_file_path = selected_file
            self.status_label.config(text=f"Selected file: {selected_file}")

            # Update the current fuel status label
            current_fuel = self.detect_current_fuel()
            if current_fuel:
                self.status_label.config(text=f"Current fuel: {current_fuel}")

                # Check if the detected current fuel matches any of the available fuels
                # If it does, set it as the selected fuel in the dropdown
                for fuel in self.fuels:
                    if fuel.lower() == current_fuel.lower():
                        self.selected_fuel.set(fuel)
                        break

            with open(selected_file, 'r') as file:
                file_content = file.read()
                self.selected_file_content = file_content
                old_values_mixture = {param: match.group(1) for param in self.mixture_params
                                      for match in re.finditer(rf'{param}\s+(\S+)(;|;//.*)', file_content)}
                old_values_thermo_type = {param: match.group(1) for param in self.thermo_type_params
                                           for match in re.finditer(rf'{param}\s+(\S+)(;|;//.*)', file_content)}
                self.open_replace_properties_popup(old_values_mixture, old_values_thermo_type)
        else:
            tk.messagebox.showerror("Error", "Selected file is not a physicalProperties file! Please look for the constant dir in your OF case!")
            

    def open_replace_properties_popup(self, old_values_mixture, old_values_thermo_type):
        selected_file = self.selected_file_path
        if selected_file:
            # Open a popup to replace the properties for the mixture and thermoType blocks
            ReplacePropertiesPopup(self, self.thermo_type_params, self.mixture_params, old_values_thermo_type, old_values_mixture)

        else:
            tk.messagebox.showerror("Error", "Please select a valid file first.")
            
    def detect_current_fuel(self):
        # Assuming the path is in the format '.../OpenFOAM-<version>/cases/<case_name>/constant/physicalProperties'
        parts = os.path.abspath(self.selected_file_path).split('.')   #split(os.sep)
        #partsi = os.path.abspath(self.selected_file_path).split('constant')   #split(os.sep)
        try:
            #index = parts.index('constant') 
            current_fuel = parts[1] # 0 + 1
            #print(current_fuel)
            return current_fuel
        except ValueError:
            return None
                  
    def on_fuel_selected(self, event):
        selected_fuel = self.fuel_options_menu.get().lower()
        if selected_fuel and selected_fuel != "Fuel Options":
            current_fuel = self.detect_current_fuel()
            if current_fuel:
                self.status_label.config(text=f"Current fuel: {current_fuel}")
                self.replace_fuel(selected_fuel, current_fuel)

    def replace_fuel(self, selected_fuel, current_fuel):
        # Assuming the 'constant' directory is inside the case directory
        case_directory = os.path.dirname(os.path.dirname(self.selected_file_path))
            
        
        # Use find and exec to run sed on all files under the 'constant' directory
        sed_command = f"find {case_directory}/constant -type f -exec sed -i 's/{current_fuel}/{selected_fuel}/g' {{}} +"
        
        # Execute the sed command
        subprocess.run(sed_command, shell=True)
        
        # --------------------- Renaming files inside constant/ after the selected fuel ----------------------->
        # Rename the file associated with the current fuel
        current_file_path = os.path.join(case_directory, 'constant', f'physicalProperties.{current_fuel.lower()}')
        new_file_path = os.path.join(case_directory, 'constant', f'physicalProperties.{selected_fuel.lower()}')
        try:
            os.rename(current_file_path, new_file_path)
            tk.messagebox.showinfo("Fuel option", f"Fuel has been updated to {selected_fuel}!")
        except FileNotFoundError:
            # Handle the case where the file does not exist
            pass
            
        # Update the status label
        self.status_label.config(text=f"Fuel replaced. Selected fuel: {selected_fuel}")
        # -----------------------------------------------------------------------------------------------------<

    # -------------- Welcome Message --------------------------    
    def show_welcome_message(self):
        welcome_message = (
            "\n"
            "Welcome to Splash!\n\n"
            "Your interactive OpenFOAM simulation platform.\n"
            "_____________________________________________________________________________\n"
            "\n"
            "Copyright (C) Simulitica Ltd. - All Rights Reserved.\n"
            "This program is licensed under the GNU Lesser General Public License (LGPL) v3.0.\n"
            "You may redistribute and/or modify this software under the terms of the LGPL.\n"
            "For full license details, please refer to the LICENSE file provided with this software.\n"
            "Written by Mohamed Aly SAYED (mohamed.sayed@simulitica.com), November 2023.\n"
            "_____________________________________________________________________________"
        )

        # Create a Label to display the welcome message
        welcome_label = ttk.Label(self.root, text=welcome_message, font=("TkDefaultFont", 12), background="white", justify='center', relief='sol', borderwidth=1)
        welcome_label.grid(row=0, column=0, columnspan=5, rowspan=10, pady=1, padx=10, sticky="nsew")

        # Create a PhotoImage object and set it to the Label
        base_path = os.path.dirname(os.path.abspath(__file__))
        welcome_image = tk.PhotoImage(file=os.path.abspath(os.path.join(base_path, "../Resources/Images/racing-car.png")))
        #welcome_image = tk.PhotoImage(file="../Resources/Images/racing-car.png")
        welcome_image = welcome_image.subsample(9, 9)
        welcome_label.config(image=welcome_image, compound="top")

        # Update the main loop to display the image for 2 seconds
        self.root.update()
        time.sleep(2)  # wait for 3 seconds
        welcome_label.destroy()  # Destroy the Label to collapse the popup

    def show_about_message(self):
        about_message = (
            "\n"
            "Welcome to Splash!\n\n"
            "Your interactive OpenFOAM simulation platform.\n"
            "_____________________________________________________________________________\n"
            "\n"
            "Copyright (C) Simulitica Ltd. - All Rights Reserved.\n"
            "This program is licensed under the GNU Lesser General Public License (LGPL) v3.0.\n"
            "You may redistribute and/or modify this software under the terms of the LGPL.\n"
            "For full license details, please refer to the LICENSE file provided with this software.\n"
            "Written by Mohamed Aly SAYED (mohamed.sayed@simulitica.com), November 2023.\n"
            "_____________________________________________________________________________"
        )

        # Create a Toplevel window for the welcome message
        popup = tk.Toplevel(self.root)
        popup.title("Splash v0.2")
        popup.geometry("750x700")  # Adjust the size as needed

        # Create a Label in the Toplevel window to display the welcome message
        welcome_label = ttk.Label(popup, text=about_message, font=("TkDefaultFont", 12), justify='center')
        welcome_label.pack(padx=10, pady=10)

        # Create a PhotoImage object and set it to the Label
        base_path = os.path.dirname(os.path.abspath(__file__))
        welcome_image = tk.PhotoImage(file=os.path.join(base_path, "../Resources/Images/racing-car.png"))
        #welcome_image = tk.PhotoImage(file="../Resources/Images/racing-car.png")  # Adjust the path as needed
        welcome_image = welcome_image.subsample(4, 4)  # Adjust subsampling as needed
        welcome_label.config(image=welcome_image, compound="top")
        welcome_label.image = welcome_image  # Keep a reference
        
    # -------------- Welcome Message -------------------------- 
     
    # -------------- Splash background image(s) -------------------------->  

##    # Clickable background image (process STL file)
##    #______________________________________________
##    def add_bgImage(self):
##        # Specify the image path
##        image_path = "../Resources/Images/racing-car.png"

##        # Create a tk.PhotoImage object directly from the file
##        self.splash_bgImage = tk.PhotoImage(file=image_path)

##        # Adjust the subsample as needed
##        self.splash_bgImage = self.splash_bgImage.subsample(6, 6)

##        # Create a button with the image, and bind it to the process_stl function
##        self.splash_bgImage_button = tk.Button(
##            self.root, 
##            image=self.splash_bgImage, 
##            bg="white",  # Set background color to white
##            activebackground="white",  # Set active background to white to prevent color change on click
##            bd=0,  # Remove border
##            command=self.process_stl_click,  # Attach the function directly
##            cursor="hand2",  # Set cursor to hand on hover
##            relief="flat"  # Flat border style
##        )

##        # Use grid() for layout
##        self.splash_bgImage_button.grid(row=2, column=7, pady=5, padx=10, sticky="nsew", rowspan=6)


         # Clickable background image (website link)
         #______________________________________________
#        # Create a label to display the image, initially without the frame effect [FLAG: Do we need this at all?!]
#        self.splash_bgImage_label = tk.Label(self.root, image=self.splash_bgImage, bg="white", cursor="hand2")
#        self.splash_bgImage_label.grid(row=2, column=7, pady=1, padx=10, sticky="nsew", rowspan=4)

#        # Bind the hover effect
#        self.splash_bgImage_label.bind("<Enter>", self.on_hover)
#        self.splash_bgImage_label.bind("<Leave>", self.off_hover)

#        # Make the image clickable
#        #self.splash_bgImage_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.buymeacoffee.com/simulitica/membership"))
#        #self.splash_bgImage_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.skool.com/cfd-dose-5227/about"))
#        self.splash_bgImage_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.cfddose.substack.com"))

#    def on_hover(self, event):
#        # Change the label appearance to simulate a frame around it on hover
#        event.widget.config(bg="white", bd=1, relief="groove")

#    def off_hover(self, event):
#        # Revert the label appearance when not hovering over it
#        event.widget.config(bg="white", bd=0, relief="flat")

    def add_bgImage(self):
        # Specify the image path
        
        #image_path = "../Resources/Images/racing-car.png"
        base_path = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.abspath(os.path.join(base_path, "../Resources/Images/racing-car.png"))

        # Create a tk.PhotoImage object directly from the file
        self.splash_bgImage = tk.PhotoImage(file=image_path)

        # Adjust the subsample as needed
        self.splash_bgImage = self.splash_bgImage.subsample(6, 6)

        # Create a label to display the image (not clickable)
        self.splash_bgImage_label = tk.Label(
            self.root, 
            image=self.splash_bgImage, 
            bg="white"  # Set background color to white to match the background
        )

        # Use grid for layout
        self.splash_bgImage_label.grid(row=2, column=7, pady=5, padx=10, sticky="new", rowspan=6)
         
                    
    def process_stl_click(self, event=None):
        # Call the process_stl method when the image is clicked
        self.process_stl()        

    # -------------- Splash background image(s) --------------------------< 
            
    # ------------------------------------- Importing the geometry ------------------------------------->    
    def import_geometry(self):
        file_path = filedialog.askopenfilename(
            title="Select Geometry File",
            filetypes=[("STL Files", "*.stl"), ("OBJ Files", "*.obj"), ("STEP Files", "*.stp"), ("All Files", "*.*")],
            initialdir=os.path.dirname(self.selected_file_path) if self.selected_file_path else None
        )
            
        if file_path:
            self.selected_file_path = file_path
            meshing_folder = os.path.join(os.path.dirname(self.selected_file_path), "Meshing")
            self.status_label.config(text="The geometry file is successfully imported!")
            # To enable meshing to start
            self.geometry_loaded = True
            
            # Display geometry in main window if it's an STL file
            if file_path.lower().endswith('.stl'):
                self.create_embedded_interactive_viewer(file_path)

            # Create the Meshing folder if it doesn't exist
            if not os.path.exists(meshing_folder):
                os.makedirs(meshing_folder)

            # Initiate the text_box with a nice mesh representation! 
            self.generate_cad_visual()
           
            # Copy and rename the geometry file
            geometry_filename = f"CAD.{file_path.split('.')[-1].lower()}"
            geometry_dest = os.path.join(meshing_folder, geometry_filename)
            self.geometry_dest_path = os.path.join(geometry_dest.split('CAD')[0])
            shutil.copyfile(self.selected_file_path, geometry_dest)

            # Directly display geometry in main window without popup selection
            self.display_vtk_free_geometry(geometry_dest)
            
            # --------- Toggle for processing the imported CAD file ----------->
            # Add a toggle button at the bottom of the popup
            self.toggle_on = False  # Initialize the toggle state to off

            # Directly display the geometry
            if file_path.lower().endswith('.stl'):
                self.visualize_stl(file_path)  # This will call our new integrated display
                self.status_label.config(text=f"Interactive 3D loaded: {os.path.basename(file_path)}")
            else:
                # For non-STL files, show info and suggest conversion
                self.status_label.config(text=f"Geometry imported: {os.path.basename(file_path)} (Convert to STL for 3D preview)")
                self.generate_cad_visual()

        else:
            tk.messagebox.showinfo("No Selection", "No file selected for import")
   # ------------------------------------- Importing the geometry -------------------------------------<    
        
    def display_geometry_in_main_window(self, file_path):
        """Display geometry in the main visualization area with crash-safe approach"""
        try:
            # Hide or minimize the text box to make room for visualization
            self.text_box.grid_forget()
            
            # Store geometry info for refresh capability
            self.current_geometry_file = file_path
            
            # Create matplotlib figure and canvas in MAIN area
            if not hasattr(self, 'main_vtk_figure') or self.main_vtk_figure is None:
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                from matplotlib.figure import Figure
                
                self.main_vtk_figure = Figure(figsize=(10, 8), dpi=80, facecolor='black')
                self.main_vtk_canvas = FigureCanvasTkAgg(self.main_vtk_figure, master=self.root)
                # Place in the main visualization area (where text_box was)
                self.main_vtk_canvas.get_tk_widget().grid(row=0, column=1, columnspan=4, padx=1, pady=1, sticky="nsew", rowspan=9)
                
                # Bind events for display handling
                self.main_vtk_canvas.mpl_connect('button_press_event', lambda event: self.refresh_geometry_view())
                
                # Note: Control buttons are now created by create_interactive_controls()
                # Remove old conflicting button code - buttons are handled by the responsive system
            
            # Use safe geometry display method
            self.display_safe_geometry_info(file_path)
            
            # Store current view state
            self.current_view = "geometry"
            
        except Exception as e:
            print(f"Error displaying geometry in main window: {e}")
            # Restore text box if display fails
            self.text_box.grid(row=0, column=1, columnspan=4, padx=1, pady=1, sticky="nsew", rowspan=9)
            tk.messagebox.showerror("Visualization Error", f"Could not display geometry: {e}")
    
    def display_safe_geometry_info(self, file_path):
        """Safe geometry display that won't crash - focuses on info rather than 3D rendering"""
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
            import numpy as np
            
            # Clear the figure
            self.main_vtk_figure.clear()
            
            # Create main subplot
            ax = self.main_vtk_figure.add_subplot(111)
            ax.set_facecolor('black')
            
            # Read STL file safely to get geometry information
            try:
                reader = vtk.vtkSTLReader()
                reader.SetFileName(file_path)
                reader.Update()
                polydata = reader.GetOutput()
                
                # Get geometry statistics
                num_points = polydata.GetNumberOfPoints()
                num_cells = polydata.GetNumberOfCells()
                bounds = polydata.GetBounds()
                x_size = bounds[1] - bounds[0]
                y_size = bounds[3] - bounds[2]
                z_size = bounds[5] - bounds[4]
                
                # Calculate file size
                file_size = os.path.getsize(file_path)
                file_size_mb = file_size / (1024 * 1024)
                
                # Create a better visual representation with actual 3D preview
                self.create_enhanced_geometry_visualization(ax, file_path, num_points, num_cells, x_size, y_size, z_size, file_size_mb, polydata)
                
            except Exception as vtk_error:
                print(f"VTK reading error: {vtk_error}")
                # Fallback display without VTK
                self.create_simple_geometry_display(ax, file_path)
            
            # Set dark background and refresh
            self.main_vtk_figure.patch.set_facecolor('black')
            self.main_vtk_canvas.draw()
            
            # Update status
            self.status_label.config(text=f"Geometry loaded: {os.path.basename(file_path)} (Click 'Open 3D Viewer' for full visualization)")
            
        except Exception as e:
            print(f"Error in safe geometry display: {e}")
            self.create_error_display(file_path, str(e))
    
    
    # Matplotlib functions have been removed from this file
    # Geometry visualization now uses text-only display
    
    
    
    # create_enhanced_geometry_visualization removed (matplotlib)
    
    
    # create_2d_geometry_visualization removed (matplotlib)
    

    
    
    # create_simple_geometry_display removed (matplotlib)
    
    def create_error_display(self, file_path, error_msg):
        """Display error information"""
        try:
            self.main_vtk_figure.clear()
            ax = self.main_vtk_figure.add_subplot(111)
            ax.set_facecolor('darkred')
            
            ax.text(0.5, 0.6, "Display Error", transform=ax.transAxes, 
                   fontsize=18, color='white', ha='center', weight='bold')
            ax.text(0.5, 0.4, f"File: {os.path.basename(file_path)}", transform=ax.transAxes, 
                   fontsize=12, color='yellow', ha='center')
            ax.text(0.5, 0.2, "Try 'Open 3D Viewer' button", transform=ax.transAxes, 
                   fontsize=12, color='lightgreen', ha='center')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            self.main_vtk_figure.patch.set_facecolor('darkred')
            self.main_vtk_canvas.draw()
            
        except Exception as e:
            print(f"Error creating error display: {e}")
    
    def render_geometry_to_canvas(self, file_path):
        """SAFE method to render geometry info without VTK offscreen rendering"""
        try:
            # Use the safe display method instead of VTK offscreen rendering
            self.display_safe_geometry_info(file_path)
            
        except Exception as e:
            print(f"Error in render_geometry_to_canvas: {e}")
            self.display_fallback_geometry_info(file_path)
    
    def display_fallback_geometry_info(self, file_path):
        """Display basic geometry info if VTK rendering fails"""
        try:
            self.main_vtk_figure.clear()
            ax = self.main_vtk_figure.add_subplot(111)
            ax.set_facecolor('black')
            
            # Get basic STL info
            try:
                reader = vtk.vtkSTLReader()
                reader.SetFileName(file_path)
                reader.Update()
                polydata = reader.GetOutput()
                num_points = polydata.GetNumberOfPoints()
                num_cells = polydata.GetNumberOfCells()
                bounds = polydata.GetBounds()
                x_size = bounds[1] - bounds[0]
                y_size = bounds[3] - bounds[2]
                z_size = bounds[5] - bounds[4]
                
                info_text = f"STL Geometry Loaded\\n\\nFile: {os.path.basename(file_path)}\\nPoints: {num_points:,}\\nTriangles: {num_cells:,}\\nSize: {x_size:.2f} × {y_size:.2f} × {z_size:.2f}\\n\\n3D rendering temporarily unavailable\\nClick to open external 3D viewer"
            except:
                info_text = f"STL Geometry Loaded\\n\\nFile: {os.path.basename(file_path)}\\n\\n3D rendering temporarily unavailable\\nClick to open external 3D viewer"
            
            ax.text(0.5, 0.5, info_text, transform=ax.transAxes, fontsize=14, color='white', 
                   ha='center', va='center', bbox=dict(boxstyle="round,pad=1", facecolor='navy', alpha=0.8))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1) 
            ax.axis('off')
            
            self.main_vtk_figure.patch.set_facecolor('black')
            self.main_vtk_canvas.draw_idle()
            
        except Exception as e:
            print(f"Fallback display error: {e}")
    
    def refresh_geometry_view(self):
        """Refresh the geometry view - useful for display issues"""
        if hasattr(self, 'current_geometry_file') and self.current_geometry_file:
            self.render_geometry_to_canvas(self.current_geometry_file)
        else:
            tk.messagebox.showinfo("No Geometry", "No geometry file currently loaded.")
    
    def on_canvas_draw_event(self):
        """Handle canvas draw events for display stability"""
        try:
            # Force update after draw events to handle display changes
            self.root.after_idle(lambda: self.main_vtk_canvas.get_tk_widget().update())
        except:
            pass  # Ignore errors during cleanup
    
    def toggle_console_view(self):
        """Toggle between geometry view and console view"""
        if hasattr(self, 'current_view') and self.current_view == "geometry":
            # Switch to console
            if hasattr(self, 'main_vtk_canvas'):
                self.main_vtk_canvas.get_tk_widget().grid_forget()
            if hasattr(self, 'toggle_view_button'):
                self.toggle_view_button.grid_remove()
            if hasattr(self, 'refresh_view_button'):
                self.refresh_view_button.grid_remove()
            self.text_box.grid(row=0, column=1, columnspan=4, padx=1, pady=1, sticky="nsew", rowspan=9)
            self.current_view = "console"
        else:
            # Switch to geometry
            if hasattr(self, 'current_geometry_file') and self.current_geometry_file:
                self.create_embedded_interactive_viewer(self.current_geometry_file)
            else:
                tk.messagebox.showinfo("No Geometry", "Please load a geometry file first.")

    def display_simple_geometry_preview(self, file_path):
        """Fallback simple preview if VTK+matplotlib fails"""
        try:
            # Hide the background image
            if hasattr(self, 'splash_bgImage_label'):
                self.splash_bgImage_label.grid_remove()
            
            # Hide the geometry canvas since we now have the main VTK viewer
            if hasattr(self, 'geometry_canvas'):
                self.geometry_canvas.grid_remove()
                
            # Update status only
            filename = os.path.basename(file_path)
            self.status_label.config(text=f"Geometry loaded: {filename} (3D view active)")
            
        except Exception as e:
            print(f"Error in simple preview cleanup: {e}")

    def visualize_stl(self, file_path):
        """VTK-free STL visualization using only matplotlib and file parsing"""
        try:
            # Store the current geometry file
            self.current_geometry_file = file_path
            
            # Display directly in main window using VTK-free approach
            self.display_vtk_free_geometry(file_path)
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load geometry: {str(e)}")
            print(f"Geometry loading error: {e}")
    
    def display_vtk_free_geometry(self, file_path):
        """Display geometry using embedded interactive 3D viewer in main window"""
        try:
            # Hide text box to make room for visualization
            self.text_box.grid_forget()
            
            # Store geometry info
            self.current_geometry_file = file_path
            
            # Create the interactive viewer embedded in main window
            self.create_embedded_interactive_viewer(file_path)
            
            # Store current view state
            self.current_view = "geometry"
            
        except Exception as e:
            print(f"Error creating interactive viewer: {e}")
            import traceback
            traceback.print_exc()
    
    def create_embedded_interactive_viewer(self, file_path):
        """Create interactive 3D viewer properly embedded in Tkinter main window"""
        try:
            import pyvista as pv
            import vtk
            from PIL import Image, ImageTk
            import numpy as np
            
            # Create frame for the 3D viewer
            if hasattr(self, 'viewer_frame'):
                self.viewer_frame.destroy()
            
            # Hide the splash background image when showing VTK viewer
            if hasattr(self, 'splash_bgImage_label'):
                self.splash_bgImage_label.grid_remove()
            
            # Clean up any old matplotlib/control frame elements
            if hasattr(self, 'main_vtk_canvas') and hasattr(self.main_vtk_canvas, 'get_tk_widget'):
                self.main_vtk_canvas.get_tk_widget().destroy()
            if hasattr(self, 'main_vtk_figure'):
                del self.main_vtk_figure
            if hasattr(self, 'toolbar_frame'):
                self.toolbar_frame.destroy()
            
            # Remove any existing control frames that might be black rectangles
            widgets_to_remove = []
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame):
                    try:
                        bg_color = widget.cget('bg')
                        grid_info = widget.grid_info()
                        if grid_info and bg_color in ['black', '#000000']:
                            row = grid_info.get('row', -1)
                            column = grid_info.get('column', -1)
                            # Remove any black frames in the control button area or viewer area
                            if (row in [9, 10, 11] and column in [1, 2, 3, 4]) or (row in [0, 1, 2] and column == 7):
                                widgets_to_remove.append(widget)
                    except tk.TclError:
                        # Widget might be destroyed, skip it
                        pass
            
            for widget in widgets_to_remove:
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
            
            self.viewer_frame = tk.Frame(self.root, bg='black')
            self.viewer_frame.grid(row=0, column=1, columnspan=4, padx=1, pady=1, sticky="nsew", rowspan=9)
            
            # Configure grid weights for proper resizing
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(1, weight=1)
            
            # Create VTK pipeline
            self.setup_vtk_pipeline(file_path)
            
            # Create interactive canvas
            self.create_interactive_canvas()
            
            # Start the rendering loop
            self.start_rendering_loop()
            
            # Create control buttons
            self.create_interactive_controls()
            
            # Update status
            filename = os.path.basename(file_path)
            mesh_data = self.vtk_mesh
            self.status_label.config(
                text=f"Interactive 3D: {filename} | {mesh_data.GetNumberOfPoints():,} points | {mesh_data.GetNumberOfCells():,} cells | Full interaction enabled"
            )
            
            print(f"✅ Successfully created embedded interactive viewer for {filename}")
            
            # Ensure car image remains visible by refreshing the results panel
            # This is needed because the viewer frame creation might affect the layout
            self.root.after(100, self.ensure_car_image_visible)
            
        except Exception as e:
            print(f"Error creating embedded viewer: {e}")
            import traceback
            traceback.print_exc()
    
    def ensure_car_image_visible(self):
        """Ensure car image remains visible after geometry loading"""
        try:
            # Force refresh of results panel to show car image
            if self.results_panel_var.get():  # If results panel is enabled
                self.splash_bgImage_label.grid(row=2, column=7, pady=5, padx=10, sticky="nsew", rowspan=6)
                print("🚗 Car image visibility restored")
        except Exception as e:
            print(f"Error restoring car image: {e}")
    
    def setup_vtk_pipeline(self, file_path):
        """Set up VTK rendering pipeline"""
        try:
            import vtk
            
            print(f"🔧 Setting up VTK pipeline for: {file_path}")
            
            # Create renderer and render window
            self.renderer = vtk.vtkRenderer()
            self.render_window = vtk.vtkRenderWindow()
            self.render_window.AddRenderer(self.renderer)
            self.render_window.SetSize(800, 600)
            self.render_window.SetOffScreenRendering(1)  # Off-screen for canvas rendering
            
            # Set background
            self.renderer.SetBackground(0.1, 0.1, 0.1)
            
            # Load STL file
            reader = vtk.vtkSTLReader()
            reader.SetFileName(file_path)
            reader.Update()
            
            print(f"📁 STL Reader output: {reader.GetOutput().GetNumberOfPoints()} points, {reader.GetOutput().GetNumberOfCells()} cells")
            
            # Clean the mesh
            cleaner = vtk.vtkCleanPolyData()
            cleaner.SetInputConnection(reader.GetOutputPort())
            cleaner.Update()
            
            print(f"🧹 After cleaning: {cleaner.GetOutput().GetNumberOfPoints()} points, {cleaner.GetOutput().GetNumberOfCells()} cells")
            
            # Generate normals for proper lighting
            normals = vtk.vtkPolyDataNormals()
            normals.SetInputConnection(cleaner.GetOutputPort())
            normals.ComputePointNormalsOn()
            normals.ComputeCellNormalsOn()
            normals.Update()
            
            # Store mesh for reference
            self.vtk_mesh = normals.GetOutput()
            
            print(f"📐 After normals: {self.vtk_mesh.GetNumberOfPoints()} points, {self.vtk_mesh.GetNumberOfCells()} cells")
            print(f"📏 Mesh bounds: {self.vtk_mesh.GetBounds()}")
            
            # Create mapper and actor
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(normals.GetOutputPort())
            
            self.mesh_actor = vtk.vtkActor()
            self.mesh_actor.SetMapper(mapper)
            
            # Set surface properties for nice rendering
            prop = self.mesh_actor.GetProperty()
            prop.SetColor(0.7, 0.9, 1.0)  # Light blue
            prop.SetOpacity(0.9)
            prop.SetSpecular(0.3)
            prop.SetDiffuse(0.8)
            prop.SetAmbient(0.2)
            prop.EdgeVisibilityOn()
            prop.SetEdgeColor(0.2, 0.2, 0.6)
            prop.SetInterpolationToPhong()  # Smooth shading
            
            # Add actor to renderer
            self.renderer.AddActor(self.mesh_actor)
            
            print(f"🎭 Mesh actor added to renderer")
            
            # Set up lighting
            self.setup_renderer_lighting(self.renderer)
            
            # Set initial camera position based on GEOMETRY bounds (not axes)
            bounds = self.vtk_mesh.GetBounds()
            center_x = (bounds[0] + bounds[1]) / 2
            center_y = (bounds[2] + bounds[3]) / 2  
            center_z = (bounds[4] + bounds[5]) / 2
            
            max_dimension = max(bounds[1] - bounds[0], 
                              bounds[3] - bounds[2], 
                              bounds[5] - bounds[4])
            
            # Store geometry bounds for axis view functions (compatible format)
            self.geometry_bounds = (center_x, center_y, center_z, max_dimension / 2)
            
            print(f"📊 Geometry center: ({center_x:.4f}, {center_y:.4f}, {center_z:.4f})")
            print(f"📏 Max dimension: {max_dimension:.4f}")
            print(f"📐 Geometry bounds stored: {self.geometry_bounds}")
            
            # Reset camera to fit all actors (this sets the focal point)
            self.renderer.ResetCamera()
            camera = self.renderer.GetActiveCamera()
            
            # NOW set the focal point to the geometry center
            camera.SetFocalPoint(center_x, center_y, center_z)
            
            # Position camera at an appropriate distance from the center
            distance = max_dimension * 3.0  # Good viewing distance
            camera.SetPosition(
                center_x + distance * 0.7,  # Offset in X
                center_y + distance * 0.5,  # Offset in Y  
                center_z + distance * 0.7   # Offset in Z
            )
            camera.SetViewUp(0, 1, 0)  # Y up (standard orientation)
            
            # Get the current camera position after reset
            pos_before = camera.GetPosition()
            fp_before = camera.GetFocalPoint()
            
            print(f"📷 Camera position: {pos_before}")
            print(f"🎯 Camera focal point: {fp_before}")
            
            camera.SetParallelProjection(False)  # Perspective view for better interaction
            
            # Immediately position camera for isometric view to ensure geometry is visible
            camera.SetPosition(center_x + distance * 0.7,
                             center_y + distance * 0.7, 
                             center_z + distance * 0.7)
            camera.SetFocalPoint(center_x, center_y, center_z)
            camera.SetViewUp(0, 1, 0)  # Y-up orientation
            
            # Ensure proper clipping planes
            camera.SetClippingRange(distance * 0.01, distance * 100.0)
            
            # NOW add coordinate axes (after camera is properly set for geometry)
            self.setup_coordinate_axes()
            
            # Final render to display the properly positioned geometry
            if hasattr(self, 'render_window'):
                self.render_window.Render()
            print("📷 Camera positioned for optimal geometry view")
            
            print("✅ VTK pipeline setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up VTK pipeline: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def setup_coordinate_axes(self):
        """Add coordinate axes to the scene scaled appropriately"""
        try:
            import vtk
            
            # Calculate appropriate axes size based on geometry bounds
            bounds = self.vtk_mesh.GetBounds()
            x_size = bounds[1] - bounds[0]  # max_x - min_x
            y_size = bounds[3] - bounds[2]  # max_y - min_y  
            z_size = bounds[5] - bounds[4]  # max_z - min_z
            
            # Use 20% of the largest dimension for axes length
            max_size = max(x_size, y_size, z_size)
            axes_length = max_size * 0.2
            
            print(f"📏 Geometry size: X={x_size:.4f}, Y={y_size:.4f}, Z={z_size:.4f}")
            print(f"📐 Axes length set to: {axes_length:.4f}")
            
            # Create axes actor
            axes = vtk.vtkAxesActor()
            axes.SetTotalLength(axes_length, axes_length, axes_length)
            axes.SetCylinderRadius(0.002 * max_size)  # Scale cylinder radius
            axes.SetConeRadius(0.005 * max_size)     # Scale cone radius
            axes.SetSphereRadius(0.003 * max_size)   # Scale sphere radius
            
            # Set axis labels
            axes.SetXAxisLabelText("X")
            axes.SetYAxisLabelText("Y") 
            axes.SetZAxisLabelText("Z")
            
            # Position axes at the corner of geometry bounds
            axes.SetPosition(bounds[0], bounds[2], bounds[4])
            
            # Add to renderer
            self.renderer.AddActor(axes)
            
            print(f"📍 Axes positioned at: ({bounds[0]:.4f}, {bounds[2]:.4f}, {bounds[4]:.4f})")
            
        except Exception as e:
            print(f"Error setting up axes: {e}")
    
    def create_interactive_canvas(self):
        """Create interactive canvas for VTK rendering"""
        try:
            # Create main canvas
            self.canvas = tk.Canvas(self.viewer_frame, bg='black', width=800, height=600)
            self.canvas.pack(fill="both", expand=True)
            
            # Initialize interaction state
            self.last_mouse_x = 0
            self.last_mouse_y = 0
            self.mouse_mode = "rotate"  # rotate, pan, zoom
            
            # Bind mouse events for interaction
            self.canvas.bind("<Button-1>", self.on_left_click)
            self.canvas.bind("<B1-Motion>", self.on_left_drag)
            self.canvas.bind("<Button-2>", self.on_middle_click)
            self.canvas.bind("<B2-Motion>", self.on_middle_drag)
            self.canvas.bind("<Button-3>", self.on_right_click)
            self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
            self.canvas.bind("<KeyPress>", self.on_key_press)
            
            # Make canvas focusable for keyboard events
            self.canvas.focus_set()
            
            print("✅ Interactive canvas created with full mouse/keyboard support")
            
        except Exception as e:
            print(f"Error creating interactive canvas: {e}")
            raise
    
    def start_rendering_loop(self):
        """Start controlled rendering loop for interactivity"""
        try:
            # Render once initially
            self.render_scene()
            
            # Now that rendering is working, set up camera properly with delays
            # This ensures the VTK pipeline is fully initialized
            self.root.after(100, self.force_initial_camera_setup)
            self.root.after(250, self.reset_camera_view)
            self.root.after(500, self.final_camera_setup)
            
        except Exception as e:
            print(f"Error in initial render: {e}")
    
    def render_scene(self):
        """Render VTK scene to canvas"""
        try:
            import vtk
            from PIL import Image, ImageTk
            import numpy as np
            
            # Render the scene
            self.render_window.Render()
            
            # Get the rendered image
            w2if = vtk.vtkWindowToImageFilter()
            w2if.SetInput(self.render_window)
            w2if.SetInputBufferTypeToRGBA()
            w2if.ReadFrontBufferOff()
            w2if.Update()
            
            # Convert VTK image to PIL Image
            vtk_image = w2if.GetOutput()
            dims = vtk_image.GetDimensions()
            
            # Get image data
            vtk_array = vtk_image.GetPointData().GetScalars()
            components = vtk_array.GetNumberOfComponents()
            
            # Convert to numpy array using proper VTK method
            try:
                # Try the modern VTK numpy support
                from vtkmodules.util.numpy_support import vtk_to_numpy
                np_array = vtk_to_numpy(vtk_array)
            except ImportError:
                # Fallback to direct conversion
                np_array = np.frombuffer(vtk_array, dtype=np.uint8)
            
            # Reshape to image dimensions
            np_array = np_array.reshape(dims[1], dims[0], components)
            
            # Flip vertically (VTK renders upside down)
            np_array = np.flipud(np_array)
            
            # Convert to PIL Image (ensure RGB)
            if components >= 3:
                pil_image = Image.fromarray(np_array[:,:,:3], 'RGB')
            else:
                pil_image = Image.fromarray(np_array, 'L')
            
            # Convert to Tkinter PhotoImage
            self.current_image = ImageTk.PhotoImage(pil_image)
            
            # Update canvas
            self.canvas.delete("render")
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # Only if canvas is properly sized
                self.canvas.create_image(
                    canvas_width // 2, 
                    canvas_height // 2, 
                    anchor="center", 
                    image=self.current_image, 
                    tags="render"
                )
            
            print("✅ Scene rendered successfully")
            
        except Exception as e:
            print(f"Error rendering scene: {e}")
            import traceback
            traceback.print_exc()
    
    def request_render(self):
        """Request a render update (safe for interactive use)"""
        try:
            # Schedule render in main thread
            self.root.after_idle(self.render_scene)
        except Exception as e:
            print(f"Error requesting render: {e}")
    
    def on_left_click(self, event):
        """Handle left mouse click - start rotation"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.mouse_mode = "rotate"
    
    def on_left_drag(self, event):
        """Handle left mouse drag - rotate camera"""
        try:
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            
            if hasattr(self, 'renderer'):
                camera = self.renderer.GetActiveCamera()
                camera.Azimuth(dx * 0.5)
                camera.Elevation(-dy * 0.5)  # Negative for intuitive direction
                
                # Request a render update
                self.request_render()
                
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            
        except Exception as e:
            print(f"Error in rotation: {e}")
    
    def on_middle_click(self, event):
        """Handle middle mouse click - start panning"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.mouse_mode = "pan"
    
    def on_middle_drag(self, event):
        """Handle middle mouse drag - pan camera"""
        try:
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            
            if hasattr(self, 'renderer'):
                camera = self.renderer.GetActiveCamera()
                
                # Get camera parameters for panning
                focal_point = camera.GetFocalPoint()
                position = camera.GetPosition()
                
                # Calculate pan vectors
                factor = 0.01
                camera.SetFocalPoint(
                    focal_point[0] - dx * factor,
                    focal_point[1] + dy * factor,
                    focal_point[2]
                )
                camera.SetPosition(
                    position[0] - dx * factor,
                    position[1] + dy * factor,
                    position[2]
                )
                
                # Request a render update
                self.request_render()
                
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            
        except Exception as e:
            print(f"Error in panning: {e}")
    
    def on_right_click(self, event):
        """Handle right click - context menu"""
        try:
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Reset View", command=self.reset_camera_view)
            context_menu.add_command(label="Toggle Wireframe", command=self.toggle_wireframe_mode)
            context_menu.add_command(label="Toggle Projection", command=self.toggle_projection_mode)
            context_menu.add_separator()
            context_menu.add_command(label="Fit to Window", command=self.fit_to_window)
            context_menu.add_command(label="Save Screenshot", command=self.save_current_view)
            
            context_menu.tk_popup(event.x_root, event.y_root)
            
        except Exception as e:
            print(f"Error showing context menu: {e}")
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel - zoom"""
        try:
            if hasattr(self, 'renderer'):
                camera = self.renderer.GetActiveCamera()
                if event.delta > 0:
                    camera.Zoom(1.1)
                else:
                    camera.Zoom(0.9)
                
                # Request a render update
                self.request_render()
                    
        except Exception as e:
            print(f"Error in zoom: {e}")
    
    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        try:
            if event.keysym == 'r':
                self.reset_camera_view()
            elif event.keysym == 'w':
                self.toggle_wireframe_mode()
            elif event.keysym == 'p':
                self.toggle_projection_mode()
            elif event.keysym == 'f':
                self.fit_to_window()
                
        except Exception as e:
            print(f"Error handling key press: {e}")
    
    def final_camera_setup(self):
        """Final camera setup attempt with forced render update"""
        try:
            if hasattr(self, 'renderer') and hasattr(self, 'render_window'):
                # Force a complete render cycle
                self.render_window.Render()
                
                # Reset camera one more time
                self.reset_camera_view()
                
                # Force another render and update canvas
                self.render_window.Render()
                self.render_scene()
                
                print("🎯 Final camera setup complete")
        except Exception as e:
            print(f"Error in final camera setup: {e}")
    
    def force_initial_camera_setup(self):
        """Force initial camera setup with multiple render calls"""
        try:
            if hasattr(self, 'renderer') and hasattr(self, 'render_window'):
                # Force multiple renders to ensure proper initialization
                self.render_window.Render()
                self.renderer.ResetCamera()
                self.render_window.Render()
                
                # Apply our custom camera positioning
                self.reset_camera_view()
                
                # Force another render
                self.render_window.Render()
                print("🔄 Force initial camera setup complete")
        except Exception as e:
            print(f"Error in force camera setup: {e}")
    
    def reset_camera_view(self):
        """Reset camera to default view with gimbal lock prevention"""
        try:
            if hasattr(self, 'renderer'):
                camera = self.renderer.GetActiveCamera()
                
                # Get geometry bounds for proper positioning
                if hasattr(self, 'geometry_bounds'):
                    # geometry_bounds format: (center_x, center_y, center_z, max_range)
                    center_x, center_y, center_z, max_range = self.geometry_bounds
                    center = [center_x, center_y, center_z]
                    distance = max_range * 3.0  # Ensure good viewing distance
                    
                    # Set camera position for isometric view (avoid gimbal lock)
                    camera.SetPosition(center[0] + distance * 0.7,
                                     center[1] + distance * 0.7, 
                                     center[2] + distance * 0.7)
                    camera.SetFocalPoint(center)
                    camera.SetViewUp(0, 1, 0)  # Y-up orientation (standard)
                    
                    # Ensure proper clipping planes
                    camera.SetClippingRange(distance * 0.1, distance * 10.0)
                else:
                    # Fallback to renderer reset
                    self.renderer.ResetCamera()
                    camera.Azimuth(45)
                    camera.Elevation(25)
                
                # Multiple render calls to ensure camera update takes effect
                self.request_render()
                if hasattr(self, 'render_window'):
                    self.render_window.Render()
                    self.render_window.Modified()
                    
                print("✅ Camera view reset")
        except Exception as e:
            print(f"Error resetting camera: {e}")
    
    def set_axis_view(self, axis_direction):
        """Set camera to axis-aligned view with gimbal lock prevention"""
        try:
            if not hasattr(self, 'renderer'):
                print("⚠️ No VTK renderer available")
                return
                
            camera = self.renderer.GetActiveCamera()
            
            # Get geometry bounds for proper positioning
            if hasattr(self, 'geometry_bounds'):
                # geometry_bounds format: (mid_x, mid_y, mid_z, max_range)
                mid_x, mid_y, mid_z, max_range = self.geometry_bounds
                center = [mid_x, mid_y, mid_z]
                distance = max_range * 3.0  # Ensure good viewing distance
                
                # Set camera position and view-up vector based on axis
                if axis_direction == 'x+':
                    # View along X+ axis (YZ plane visible)
                    camera.SetPosition(center[0] + distance, center[1], center[2])
                    camera.SetViewUp(0, 0, 1)  # Z-up
                    print("📷 View X+ (YZ plane)")
                    
                elif axis_direction == 'y+':
                    # View along Y+ axis (XZ plane visible)
                    camera.SetPosition(center[0], center[1] + distance, center[2])
                    camera.SetViewUp(0, 0, 1)  # Z-up
                    print("📷 View Y+ (XZ plane)")
                    
                elif axis_direction == 'z+':
                    # View along Z+ axis (XY plane visible)
                    camera.SetPosition(center[0], center[1], center[2] + distance)
                    camera.SetViewUp(0, 1, 0)  # Y-up for top view
                    print("📷 View Z+ (XY plane)")
                    
                elif axis_direction == 'iso':
                    # Isometric view (45-45-45 degrees)
                    camera.SetPosition(center[0] + distance * 0.7,
                                     center[1] + distance * 0.7, 
                                     center[2] + distance * 0.7)
                    camera.SetViewUp(0, 0, 1)  # Z-up
                    print("📷 Isometric view")
                
                # Set focal point and clipping
                camera.SetFocalPoint(center)
                camera.SetClippingRange(distance * 0.01, distance * 100.0)
                
                self.request_render()
                
            else:
                print("⚠️ No geometry bounds available for axis view")
                
        except Exception as e:
            print(f"Error setting axis view: {e}")
    
    def toggle_wireframe_mode(self):
        """Toggle between wireframe and surface rendering"""
        try:
            if hasattr(self, 'mesh_actor'):
                prop = self.mesh_actor.GetProperty()
                if prop.GetRepresentation() == 2:  # Surface
                    prop.SetRepresentationToWireframe()
                    print("✅ Wireframe mode enabled")
                else:
                    prop.SetRepresentationToSurface()
                    print("✅ Surface mode enabled")
                
                self.request_render()
        except Exception as e:
            print(f"Error toggling wireframe: {e}")
    
    def toggle_projection_mode(self):
        """Toggle between perspective and parallel projection"""
        try:
            if hasattr(self, 'renderer'):
                camera = self.renderer.GetActiveCamera()
                if camera.GetParallelProjection():
                    camera.SetParallelProjection(False)
                    print("✅ Perspective projection enabled")
                else:
                    camera.SetParallelProjection(True)
                    print("✅ Parallel projection enabled")
                
                self.request_render()
        except Exception as e:
            print(f"Error toggling projection: {e}")
    
    def fit_to_window(self):
        """Fit geometry to window"""
        try:
            if hasattr(self, 'renderer'):
                self.renderer.ResetCamera()
                self.request_render()
                print("✅ Geometry fitted to window")
        except Exception as e:
            print(f"Error fitting to window: {e}")
    
    def save_current_view(self):
        """Save screenshot of current view"""
        try:
            if hasattr(self, 'current_image'):
                from tkinter import filedialog
                filename = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
                )
                if filename:
                    # Convert PhotoImage back to PIL and save
                    # This is a simplified implementation
                    print(f"✅ Would save screenshot to {filename}")
        except Exception as e:
            print(f"Error saving screenshot: {e}")
    
    def create_interactive_controls(self):
        """Create control buttons for interactive viewer with responsive spacing"""
        try:
            # Clear any existing control buttons first
            if hasattr(self, 'control_buttons'):
                for btn, _, _ in self.control_buttons:
                    btn.destroy()
            
            # Initialize or reinitialize button references for dynamic resizing
            self.control_buttons = []
            
            def create_button_label(parent, text, bg_color, command):
                """Create a clickable label that looks like a button"""
                label = tk.Label(parent, text=text, 
                               bg=bg_color, fg="white", 
                               font=("Arial", 9, "bold"),
                               relief="raised", bd=2, 
                               cursor="hand2",
                               pady=1, padx=2)
                label.bind("<Button-1>", lambda e: command())
                # Add hover effects
                def on_enter(e):
                    darker_color = "#365A9B" if bg_color == "#4472C4" else "#5E8F3A"
                    label.config(bg=darker_color)
                def on_leave(e):
                    label.config(bg=bg_color)
                label.bind("<Enter>", on_enter)
                label.bind("<Leave>", on_leave)
                return label
            
            def update_button_layout():
                """Update button sizes and positions based on current window size"""
                try:
                    # Get current window width for calculations
                    window_width = self.root.winfo_width()
                    if window_width < 100:  # Window not fully initialized yet
                        window_width = 800  # Use reasonable default
                    
                    # Calculate responsive dimensions
                    button_width = max(5, min(9, window_width // 120))  # 5-9 characters
                    col_spacing = max(8, window_width // 80)  # Proper column spacing
                    pair_spacing = max(3, window_width // 160)  # Tighter pair spacing
                    
                    # Update all buttons with consistent spacing
                    for btn, col, is_left in self.control_buttons:
                        btn.config(width=button_width)
                        if is_left:
                            padx = (col_spacing, pair_spacing)
                        else:
                            padx = (pair_spacing, col_spacing)
                        btn.grid(padx=padx, pady=(8, 6))
                        
                except Exception as e:
                    print(f"Error updating button layout: {e}")
            
            # Create all buttons - Row 9 across columns 1-4
            
            # Column 1: Control group - Reset & Wireframe (Blue theme)
            reset_btn = create_button_label(self.root, "Reset", "#4472C4", self.reset_camera_view)
            reset_btn.grid(row=9, column=1, sticky="w")
            self.control_buttons.append((reset_btn, 1, True))
            
            wire_btn = create_button_label(self.root, "Wire", "#4472C4", self.toggle_wireframe_mode)
            wire_btn.grid(row=9, column=1, sticky="e")
            self.control_buttons.append((wire_btn, 1, False))
            
            # Column 2: Control group - Projection & Fit (Blue theme)
            proj_btn = create_button_label(self.root, "Proj", "#4472C4", self.toggle_projection_mode)
            proj_btn.grid(row=9, column=2, sticky="w")
            self.control_buttons.append((proj_btn, 2, True))
            
            fit_btn = create_button_label(self.root, "Fit", "#4472C4", self.fit_to_window)
            fit_btn.grid(row=9, column=2, sticky="e")
            self.control_buttons.append((fit_btn, 2, False))
            
            # Column 3: Axis group - X+ & Y+ (Green theme)
            x_btn = create_button_label(self.root, "X+", "#70AD47", lambda: self.set_axis_view('x+'))
            x_btn.grid(row=9, column=3, sticky="w")
            self.control_buttons.append((x_btn, 3, True))
            
            y_btn = create_button_label(self.root, "Y+", "#70AD47", lambda: self.set_axis_view('y+'))
            y_btn.grid(row=9, column=3, sticky="e")
            self.control_buttons.append((y_btn, 3, False))
            
            # Column 4: Axis group - Z+ & Isometric (Green theme)
            z_btn = create_button_label(self.root, "Z+", "#70AD47", lambda: self.set_axis_view('z+'))
            z_btn.grid(row=9, column=4, sticky="w")
            self.control_buttons.append((z_btn, 4, True))
            
            iso_btn = create_button_label(self.root, "Iso", "#70AD47", lambda: self.set_axis_view('iso'))
            iso_btn.grid(row=9, column=4, sticky="e")
            self.control_buttons.append((iso_btn, 4, False))
            
            # Set up initial layout and bind resize event (only once)
            if not hasattr(self, '_resize_bound'):
                self.root.bind('<Configure>', lambda e: self.root.after_idle(update_button_layout))
                self._resize_bound = True
            
            # Apply initial layout
            self.root.after(100, update_button_layout)
            
            print("✅ Interactive controls created (8 buttons with responsive spacing)")
            
        except Exception as e:
            print(f"Error creating controls: {e}")
    def setup_renderer_lighting(self, renderer):
        """Set up enhanced lighting for VTK renderer"""
        try:
            import vtk
            
            # Remove default lights
            renderer.RemoveAllLights()
            
            # Add key light (main illumination)
            key_light = vtk.vtkLight()
            key_light.SetPosition(1, 1, 1)
            key_light.SetFocalPoint(0, 0, 0)
            key_light.SetColor(1.0, 1.0, 1.0)
            key_light.SetIntensity(0.8)
            renderer.AddLight(key_light)
            
            # Add fill light (soften shadows)
            fill_light = vtk.vtkLight()
            fill_light.SetPosition(-1, -1, 1)
            fill_light.SetFocalPoint(0, 0, 0)
            fill_light.SetColor(0.8, 0.8, 1.0)
            fill_light.SetIntensity(0.4)
            renderer.AddLight(fill_light)
            
            # Add back light (rim lighting)
            back_light = vtk.vtkLight()
            back_light.SetPosition(0, 0, -1)
            back_light.SetFocalPoint(0, 0, 0)
            back_light.SetColor(1.0, 1.0, 0.8)
            back_light.SetIntensity(0.2)
            renderer.AddLight(back_light)
            
            print("✅ Enhanced lighting setup complete")
            
        except Exception as e:
            print(f"Error setting up lighting: {e}")

    def load_stl_mesh_with_vtk(self, file_path):
        """Load STL file using VTK for proper surface rendering"""
        import vtk
        
        try:
            # Create STL reader
            reader = vtk.vtkSTLReader()
            reader.SetFileName(file_path)
            reader.Update()
            
            # Get the mesh
            mesh = reader.GetOutput()
            
            # Clean the mesh
            cleaner = vtk.vtkCleanPolyData()
            cleaner.SetInputData(mesh)
            cleaner.Update()
            
            # Generate normals for better lighting
            normals = vtk.vtkPolyDataNormals()
            normals.SetInputConnection(cleaner.GetOutputPort())
            normals.ComputePointNormalsOn()
            normals.ComputeCellNormalsOn()
            normals.Update()
            
            cleaned_mesh = normals.GetOutput()
            
            print(f"Loaded STL: {cleaned_mesh.GetNumberOfPoints()} points, {cleaned_mesh.GetNumberOfCells()} cells")
            
            return cleaned_mesh
            
        except Exception as e:
            print(f"Error loading STL with VTK: {e}")
            # Return empty mesh as fallback
            return vtk.vtkPolyData()
    
    def add_axes_to_renderer(self):
        """Add coordinate axes to the VTK renderer"""
        import vtk
        
        try:
            # Create axes actor
            axes = vtk.vtkAxesActor()
            axes.SetTotalLength(50, 50, 50)  # Set axis length
            axes.SetCylinderRadius(0.02)
            axes.SetConeRadius(0.05)
            axes.SetSphereRadius(0.03)
            
            # Add axes to renderer
            self.renderer.AddActor(axes)
            
            # Create text labels
            self.add_axis_labels()
            
        except Exception as e:
            print(f"Error adding axes: {e}")
    
    def add_axis_labels(self):
        """Add axis labels to the renderer"""
        import vtk
        
        try:
            # Create text actors for axis labels
            labels = ['X', 'Y', 'Z']
            colors = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Red, Green, Blue
            positions = [[60, 0, 0], [0, 60, 0], [0, 0, 60]]
            
            for i, (label, color, pos) in enumerate(zip(labels, colors, positions)):
                text_actor = vtk.vtkTextActor3D()
                text_actor.SetInput(label)
                text_actor.SetPosition(pos)
                text_actor.GetTextProperty().SetFontSize(20)
                text_actor.GetTextProperty().SetColor(color)
                text_actor.GetTextProperty().BoldOn()
                
                self.renderer.AddActor(text_actor)
                
        except Exception as e:
            print(f"Error adding axis labels: {e}")
    
    def setup_vtk_lighting(self):
        """Set up enhanced lighting for VTK renderer"""
        import vtk
        
        try:
            # Remove default lights
            self.renderer.RemoveAllLights()
            
            # Add key light
            key_light = vtk.vtkLight()
            key_light.SetPosition(1, 1, 1)
            key_light.SetFocalPoint(0, 0, 0)
            key_light.SetColor(1.0, 1.0, 1.0)
            key_light.SetIntensity(0.8)
            self.renderer.AddLight(key_light)
            
            # Add fill light
            fill_light = vtk.vtkLight()
            fill_light.SetPosition(-1, -1, 1)
            fill_light.SetFocalPoint(0, 0, 0)
            fill_light.SetColor(0.8, 0.8, 1.0)
            fill_light.SetIntensity(0.4)
            self.renderer.AddLight(fill_light)
            
            # Add back light
            back_light = vtk.vtkLight()
            back_light.SetPosition(0, 0, -1)
            back_light.SetFocalPoint(0, 0, 0)
            back_light.SetColor(1.0, 1.0, 0.8)
            back_light.SetIntensity(0.2)
            self.renderer.AddLight(back_light)
            
        except Exception as e:
            print(f"Error setting up lighting: {e}")
        """Load STL file and process for proper surface rendering"""
        import pyvista as pv
        import numpy as np
        
        try:
            # Load the mesh
            mesh = pv.read(file_path)
            
            # Check if mesh has cells (faces) for proper surface rendering
            if mesh.n_cells == 0:
                print("Mesh has no cells, creating surface from points...")
                # If no faces, try to create a surface from points
                if mesh.n_points > 3:
                    # Use Delaunay triangulation to create surface
                    surface = mesh.delaunay_2d()
                    if surface.n_cells > 0:
                        mesh = surface
                    else:
                        # Fallback: create point cloud surface
                        mesh = mesh.reconstruct_surface()
            
            # Ensure mesh has proper normals for rendering
            if mesh.n_cells > 0:
                mesh = mesh.compute_normals()
                
            # Clean the mesh
            mesh = mesh.clean()
            
            print(f"Processed mesh: {mesh.n_points} points, {mesh.n_cells} cells")
            
            return mesh
            
        except Exception as e:
            print(f"Error processing STL mesh: {e}")
            # Return original mesh as fallback
            return pv.read(file_path)
    
    def add_enhanced_mesh_to_plotter(self, mesh):
        """Add mesh to PyVista plotter with enhanced rendering"""
        import pyvista as pv
        
        try:
            # Clear any existing meshes
            self.pv_plotter.clear()
            
            # Set background
            self.pv_plotter.background_color = '#1a1a1a'
            
            if mesh.n_cells > 0:
                # Render as surface mesh
                print(f"Rendering as surface: {mesh.n_cells} faces")
                
                # Add the surface mesh with proper lighting
                actor = self.pv_plotter.add_mesh(
                    mesh,
                    color='lightblue',
                    show_edges=True,
                    edge_color='darkblue',
                    opacity=0.9,
                    smooth_shading=True,
                    lighting=True,
                    specular=0.5,
                    diffuse=0.8,
                    ambient=0.2
                )
                
                # Add wireframe overlay for better definition
                wireframe_actor = self.pv_plotter.add_mesh(
                    mesh,
                    style='wireframe',
                    color='white',
                    opacity=0.3,
                    line_width=1
                )
                
            else:
                # Render as point cloud if no faces
                print(f"Rendering as point cloud: {mesh.n_points} points")
                
                actor = self.pv_plotter.add_mesh(
                    mesh,
                    style='points',
                    point_size=3,
                    color='cyan',
                    opacity=0.8,
                    render_points_as_spheres=True
                )
            
            # Add coordinate axes
            self.pv_plotter.show_axes(
                xlabel='X (mm)',
                ylabel='Y (mm)', 
                zlabel='Z (mm)',
                line_width=2
            )
            
            # Add enhanced lighting
            self.pv_plotter.add_light(pv.Light(position=(1, 1, 1), focal_point=(0, 0, 0), intensity=0.8))
            self.pv_plotter.add_light(pv.Light(position=(-1, -1, 1), focal_point=(0, 0, 0), intensity=0.4))
            
        except Exception as e:
            print(f"Error adding mesh to plotter: {e}")
    
    def setup_pyvista_camera(self):
        """Configure PyVista camera for optimal viewing"""
        try:
            # Set up camera position
            self.pv_plotter.camera.azimuth = 45
            self.pv_plotter.camera.elevation = 25
            
            # Auto-scale to fit the geometry
            self.pv_plotter.reset_camera()
            
            # Enable parallel projection for technical viewing
            self.pv_plotter.enable_parallel_projection()
            
        except Exception as e:
            print(f"Error setting up camera: {e}")
                    
        """Create web-based 3D visualization using Plotly as fallback"""
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
            import numpy as np
            import webbrowser
            import tempfile
            import os
            
            # Parse STL file for plotly
            vertices, triangles, file_size_mb = self.parse_stl_file_advanced(file_path)
            
            if len(vertices) == 0:
                raise Exception("No vertices found in STL file")
                
            vertices = np.array(vertices)
            
            # Create 3D scatter plot for Plotly
            if len(triangles) > 0 and len(triangles) < 10000:
                # Use mesh3d for surface rendering
                triangles_array = np.array(triangles)
                
                # Flatten triangles to get i, j, k indices
                i = triangles_array[:, 0, :].flatten()
                j = triangles_array[:, 1, :].flatten() 
                k = triangles_array[:, 2, :].flatten()
                
                fig = go.Figure(data=[
                    go.Mesh3d(
                        x=vertices[:, 0],
                        y=vertices[:, 1], 
                        z=vertices[:, 2],
                        i=np.arange(0, len(vertices), 3),
                        j=np.arange(1, len(vertices), 3),
                        k=np.arange(2, len(vertices), 3),
                        color='lightblue',
                        opacity=0.8,
                        lighting=dict(ambient=0.4, diffuse=0.8, specular=0.1)
                    )
                ])
            else:
                # Use scatter3d for point cloud
                fig = go.Figure(data=[
                    go.Scatter3d(
                        x=vertices[:, 0],
                        y=vertices[:, 1],
                        z=vertices[:, 2],
                        mode='markers',
                        marker=dict(
                            size=2,
                            color=vertices[:, 2],
                            colorscale='viridis',
                            opacity=0.8
                        )
                    )
                ])
            
            # Update layout for better visualization
            filename = os.path.basename(file_path)
            fig.update_layout(
                title=f"Interactive 3D: {filename}",
                scene=dict(
                    xaxis_title='X (mm)',
                    yaxis_title='Y (mm)',
                    zaxis_title='Z (mm)',
                    bgcolor='rgb(26,26,26)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                paper_bgcolor='rgb(26,26,26)',
                plot_bgcolor='rgb(26,26,26)',
                font=dict(color='white')
            )
            
            # Create temporary HTML file and open in browser
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                html_content = pyo.plot(fig, output_type='div', include_plotlyjs=True)
                full_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>SplashFOAM 3D Viewer - {filename}</title>
                    <style>
                        body {{ margin: 0; padding: 20px; background-color: #1a1a1a; color: white; font-family: Arial; }}
                        .info {{ padding: 10px; background-color: #333; border-radius: 5px; margin-bottom: 10px; }}
                    </style>
                </head>
                <body>
                    <div class="info">
                        <h2>SplashFOAM Interactive 3D Viewer</h2>
                        <p><strong>File:</strong> {filename} | <strong>Vertices:</strong> {len(vertices):,} | <strong>Size:</strong> {file_size_mb:.1f}MB</p>
                        <p><strong>Controls:</strong> Click+Drag to rotate | Scroll to zoom | Double-click to reset</p>
                    </div>
                    {html_content}
                </body>
                </html>
                """
                f.write(full_html)
                temp_file_path = f.name
            
            # Open in default browser
            webbrowser.open('file://' + temp_file_path)
            
            # Show info in main window
            self.create_fallback_info_display(file_path, "Web browser 3D viewer opened")
            
            self.status_label.config(text=f"Web 3D viewer opened: {filename} | {len(vertices):,} vertices")
            
        except Exception as e:
            print(f"Error creating web-based visualization: {e}")
            self.create_fallback_info_display(file_path, f"Visualization error: {e}")
    
    def create_pyvista_controls(self):
        """Create control buttons for PyVista visualization"""
        try:
            control_frame = tk.Frame(self.root, bg='#1a1a1a')
            control_frame.grid(row=10, column=1, columnspan=4, pady=5, sticky="ew")
            
            ttk.Button(control_frame, text="Reset View", 
                     command=self.reset_pyvista_view).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Wireframe", 
                     command=self.toggle_pyvista_wireframe).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Lighting", 
                     command=self.toggle_pyvista_lighting).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Screenshot", 
                     command=self.save_pyvista_screenshot).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Show Console", 
                     command=self.toggle_console_view).pack(side=tk.LEFT, padx=5)
            
            # Add help text
            help_label = tk.Label(control_frame, 
                                text="🖱️ Full 3D interaction enabled | Right-click for context menu",
                                fg='#80d0ff', bg='#1a1a1a', font=('Arial', 9))
            help_label.pack(side=tk.RIGHT, padx=10)
            
        except Exception as e:
            print(f"Error creating PyVista controls: {e}")
        """Create enhanced interactive 3D visualization using matplotlib"""
        try:
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            import matplotlib.pyplot as plt
            
            # Parse STL file manually to get vertex data
            vertices, triangles, file_size_mb = self.parse_stl_file_advanced(file_path)
            
            if len(vertices) == 0:
                raise Exception("No vertices found in STL file")
            
            # Convert to numpy arrays for processing
            vertices = np.array(vertices)
            x_coords = vertices[:, 0]
            y_coords = vertices[:, 1]
            z_coords = vertices[:, 2]
            
            # Calculate statistics
            num_points = len(vertices)
            num_triangles = len(triangles) if triangles else num_points // 3
            x_size = np.max(x_coords) - np.min(x_coords)
            y_size = np.max(y_coords) - np.min(y_coords)
            z_size = np.max(z_coords) - np.min(z_coords)
            
            # Clear and create interactive 3D subplot
            self.main_vtk_figure.clear()
            self.ax3d = self.main_vtk_figure.add_subplot(111, projection='3d')
            self.ax3d.set_facecolor('#1a1a1a')
            
            filename = os.path.basename(file_path)
            
            # Enhanced rendering with surface triangulation if available
            if triangles and len(triangles) > 0 and len(triangles) < 20000:  # Limit for performance
                # Create surface plot with triangles
                from mpl_toolkits.mplot3d.art3d import Poly3DCollection
                
                # Sample triangles for performance
                max_triangles = min(len(triangles), 10000)
                sample_triangles = triangles[:max_triangles]
                
                # Create 3D polygon collection
                poly_collection = Poly3DCollection(sample_triangles, alpha=0.7)
                poly_collection.set_facecolor('#00bfff')  # Deep sky blue
                poly_collection.set_edgecolor('#004080')  # Darker blue edges
                poly_collection.set_linewidth(0.1)
                
                self.ax3d.add_collection3d(poly_collection)
                
                # Add wireframe overlay for better definition
                wireframe_collection = Poly3DCollection(sample_triangles[:min(2000, len(sample_triangles))], alpha=0.1)
                wireframe_collection.set_facecolor('none')
                wireframe_collection.set_edgecolor('#80d0ff')
                wireframe_collection.set_linewidth(0.3)
                self.ax3d.add_collection3d(wireframe_collection)
                
            else:
                # Fallback to point cloud with better visualization
                # Sample points intelligently for performance
                if num_points > 15000:
                    # Use spatial sampling to maintain shape
                    step = max(1, num_points // 10000)
                    display_vertices = vertices[::step]
                else:
                    display_vertices = vertices
                
                x_display = display_vertices[:, 0]
                y_display = display_vertices[:, 1]
                z_display = display_vertices[:, 2]
                
                # Create enhanced 3D scatter plot with depth-based coloring
                z_norm = (z_display - np.min(z_display)) / (np.max(z_display) - np.min(z_display) + 1e-10)
                
                self.current_plot = self.ax3d.scatter(
                    x_display, y_display, z_display, 
                    c=z_norm, cmap='viridis', s=2.0, alpha=0.8, 
                    edgecolors='none', depthshade=True
                )
                
                # Add colorbar for depth visualization
                cbar = self.main_vtk_figure.colorbar(self.current_plot, ax=self.ax3d, shrink=0.5, aspect=20, pad=0.1)
                cbar.set_label('Height', color='white', fontsize=10)
                cbar.ax.yaxis.set_tick_params(color='white', labelsize=8)
                cbar.outline.set_edgecolor('white')
            
            # Set equal aspect ratio and limits with padding
            max_range = max(x_size, y_size, z_size) / 2.0
            mid_x = (np.min(x_coords) + np.max(x_coords)) * 0.5
            mid_y = (np.min(y_coords) + np.max(y_coords)) * 0.5
            mid_z = (np.min(z_coords) + np.max(z_coords)) * 0.5
            
            padding = max_range * 0.1  # 10% padding
            self.ax3d.set_xlim(mid_x - max_range - padding, mid_x + max_range + padding)
            self.ax3d.set_ylim(mid_y - max_range - padding, mid_y + max_range + padding)
            self.ax3d.set_zlim(mid_z - max_range - padding, mid_z + max_range + padding)
            
            # Enhanced styling
            self.ax3d.set_xlabel('X (mm)', color='white', fontsize=11, weight='bold')
            self.ax3d.set_ylabel('Y (mm)', color='white', fontsize=11, weight='bold')
            self.ax3d.set_zlabel('Z (mm)', color='white', fontsize=11, weight='bold')
            self.ax3d.tick_params(colors='white', labelsize=9)
            
            # Enhance grid and panes
            self.ax3d.xaxis.pane.fill = False
            self.ax3d.yaxis.pane.fill = False
            self.ax3d.zaxis.pane.fill = False
            self.ax3d.xaxis.pane.set_edgecolor('#404040')
            self.ax3d.yaxis.pane.set_edgecolor('#404040')
            self.ax3d.zaxis.pane.set_edgecolor('#404040')
            self.ax3d.xaxis.pane.set_alpha(0.2)
            self.ax3d.yaxis.pane.set_alpha(0.2)
            self.ax3d.zaxis.pane.set_alpha(0.2)
            self.ax3d.grid(True, alpha=0.3, color='gray')
            
            # Set enhanced viewing angle for better initial view
            self.ax3d.view_init(elev=25, azim=45)
            self.current_azim = 45
            self.current_elev = 25
            
            # Store data for enhanced interactions
            self.current_coords = (x_coords, y_coords, z_coords)
            self.geometry_bounds = (mid_x, mid_y, mid_z, max_range)
            self.rotation_speed = 5  # degrees per click
            self.zoom_factor = 0.9
            
            # Enhanced title and info with better formatting
            self.main_vtk_figure.suptitle(f"Interactive 3D Geometry: {filename}", 
                                        color='white', fontsize=16, weight='bold', y=0.95)
            
            info_text = (
                f"📊 {num_points:,} vertices | {num_triangles:,} triangles | {file_size_mb:.1f}MB\n"
                f"📐 Dimensions: {x_size:.1f} × {y_size:.1f} × {z_size:.1f} mm\n"
                f"🖱️ Interactive: Click+Drag to rotate, Scroll to zoom, Toolbar for advanced controls"
            )
            
            self.main_vtk_figure.text(0.02, 0.02, info_text, 
                                    transform=self.main_vtk_figure.transFigure,
                                    fontsize=10, color='#00ff80', 
                                    verticalalignment='bottom',
                                    bbox=dict(boxstyle='round,pad=0.8', 
                                            facecolor='#1a1a1a', alpha=0.9,
                                            edgecolor='#00ff80', linewidth=1))
            
            # Set dark theme
            self.main_vtk_figure.patch.set_facecolor('#0d0d0d')
            
            # Enable enhanced mouse interactions
            self.setup_enhanced_3d_interactions()
            
            # Draw the canvas
            self.main_vtk_canvas.draw()
            
            # Update status with enhanced info
            self.status_label.config(text=f"Enhanced 3D View: {filename} | {num_points:,} vertices | Interactive controls enabled")
            
        except Exception as e:
            print(f"Error creating enhanced 3D visualization: {e}")
            self.create_fallback_info_display(file_path)
            max_range = max(x_size, y_size, z_size) / 2.0
            mid_x = (np.min(x_coords) + np.max(x_coords)) * 0.5
            mid_y = (np.min(y_coords) + np.max(y_coords)) * 0.5
            mid_z = (np.min(z_coords) + np.max(z_coords)) * 0.5
            
            self.ax3d.set_xlim(mid_x - max_range, mid_x + max_range)
            self.ax3d.set_ylim(mid_y - max_range, mid_y + max_range)
            self.ax3d.set_zlim(mid_z - max_range, mid_z + max_range)
            
            # Style the plot
            self.ax3d.set_xlabel('X', color='white', fontsize=10)
            self.ax3d.set_ylabel('Y', color='white', fontsize=10)
            self.ax3d.set_zlabel('Z', color='white', fontsize=10)
            self.ax3d.tick_params(colors='white', labelsize=8)
            
            # Set dark theme
            self.ax3d.xaxis.pane.fill = False
            self.ax3d.yaxis.pane.fill = False
            self.ax3d.zaxis.pane.fill = False
            self.ax3d.xaxis.pane.set_edgecolor('gray')
            self.ax3d.yaxis.pane.set_edgecolor('gray')
            self.ax3d.zaxis.pane.set_edgecolor('gray')
            self.ax3d.xaxis.pane.set_alpha(0.1)
            self.ax3d.yaxis.pane.set_alpha(0.1)
            self.ax3d.zaxis.pane.set_alpha(0.1)
            
    def rotate_view(self):
        """Enhanced auto-rotate with smooth animation"""
        try:
            if hasattr(self, 'ax3d'):
                # Start/stop auto-rotation
                if hasattr(self, 'auto_rotating') and self.auto_rotating:
                    self.stop_auto_rotation()
                else:
                    self.start_auto_rotation()
        except Exception as e:
            print(f"Error toggling auto-rotation: {e}")
    
    def start_auto_rotation(self):
        """Start automatic rotation animation"""
        try:
            self.auto_rotating = True
            self.rotate_animation_step()
            # Update button text
            if hasattr(self, 'control_buttons'):
                for widget in self.control_buttons:
                    if 'Rotate' in str(widget['text']):
                        widget.config(text="Stop Rotation")
        except Exception as e:
            print(f"Error starting auto-rotation: {e}")
    
    def stop_auto_rotation(self):
        """Stop automatic rotation"""
        try:
            self.auto_rotating = False
            # Update button text
            if hasattr(self, 'control_buttons'):
                for widget in self.control_buttons:
                    if 'Stop' in str(widget['text']):
                        widget.config(text="Auto Rotate")
        except Exception as e:
            print(f"Error stopping auto-rotation: {e}")
    
    def rotate_animation_step(self):
        """Single step of rotation animation"""
        try:
            if hasattr(self, 'auto_rotating') and self.auto_rotating and hasattr(self, 'ax3d'):
                self.current_azim += 2  # Smooth rotation
                if self.current_azim >= 360:
                    self.current_azim = 0
                self.ax3d.view_init(elev=self.current_elev, azim=self.current_azim)
                self.main_vtk_canvas.draw_idle()
                # Schedule next frame
                self.root.after(50, self.rotate_animation_step)  # 20 FPS
        except Exception as e:
            print(f"Error in rotation animation: {e}")
            self.auto_rotating = False
            
            # Store data for view controls
            self.current_coords = (x_display, y_display, z_display)
            self.geometry_bounds = (mid_x, mid_y, mid_z, max_range)
            
            # Add title and info
            self.main_vtk_figure.suptitle(f"Interactive 3D: {filename}", color='white', fontsize=14, y=0.95)
            
            info_text = (f"📊 {num_points:,} vertices | {num_triangles:,} triangles | {file_size_mb:.1f}MB\n"
                        f"📐 {x_size:.1f} × {y_size:.1f} × {z_size:.1f}\n"
                        f"🖱️ Use navigation toolbar for zoom/pan | VTK-Free visualization")
            
            self.main_vtk_figure.text(0.02, 0.02, info_text, 
                                    transform=self.main_vtk_figure.transFigure,
                                    fontsize=9, color='yellow', 
                                    verticalalignment='bottom',
                                    bbox=dict(boxstyle='round,pad=0.5', 
                                            facecolor='black', alpha=0.8))
            
            # Set dark background
            self.main_vtk_figure.patch.set_facecolor('black')
            
            # Draw the canvas
            self.main_vtk_canvas.draw()
            
            # Update status
            self.status_label.config(text=f"VTK-Free 3D loaded: {filename} | Use toolbar for navigation")
            
        except Exception as e:
            print(f"Error creating VTK-free visualization: {e}")
            self.create_fallback_info_display(file_path)
    
    def parse_stl_file_advanced(self, file_path):
        """Enhanced STL file parsing that extracts both vertices and triangles"""
        vertices = []
        triangles = []
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        try:
            with open(file_path, 'rb') as f:
                # Check if binary STL (first 5 bytes should not be "solid")
                header = f.read(5)
                f.seek(0)
                
                if header == b'solid':
                    # ASCII STL format
                    vertices, triangles = self.parse_ascii_stl_advanced(f)
                else:
                    # Binary STL format
                    vertices, triangles = self.parse_binary_stl_advanced(f)
                    
        except Exception as e:
            print(f"Error parsing STL file: {e}")
            # Fallback: create some sample data
            import numpy as np
            vertices = np.random.rand(1000, 3) * 10
            triangles = []
            
        return vertices, triangles, file_size_mb
    
    def parse_binary_stl_advanced(self, file_handle):
        """Enhanced binary STL parsing with triangle extraction"""
        import struct
        import numpy as np
        
        vertices = []
        triangles = []
        vertex_index = 0
        
        # Skip header (80 bytes)
        file_handle.seek(80)
        
        # Read number of triangles
        num_triangles_data = file_handle.read(4)
        if len(num_triangles_data) < 4:
            return vertices, triangles
            
        num_triangles = struct.unpack('<I', num_triangles_data)[0]
        
        # Read triangles (limit to prevent memory issues)
        max_triangles = min(num_triangles, 30000)  # Increased limit for better quality
        
        for i in range(max_triangles):
            try:
                # Skip normal vector (12 bytes)
                file_handle.seek(file_handle.tell() + 12)
                
                # Read 3 vertices for this triangle
                triangle_vertices = []
                triangle_indices = []
                
                for j in range(3):
                    vertex_data = file_handle.read(12)
                    if len(vertex_data) < 12:
                        return vertices, triangles
                    x, y, z = struct.unpack('<fff', vertex_data)
                    vertices.append([x, y, z])
                    triangle_vertices.append([x, y, z])
                    triangle_indices.append(vertex_index)
                    vertex_index += 1
                
                # Store triangle as array of 3 vertices
                triangles.append(triangle_vertices)
                
                # Skip attribute byte count (2 bytes)
                file_handle.seek(file_handle.tell() + 2)
                
            except Exception as e:
                print(f"Error reading triangle {i}: {e}")
                break
                
        return vertices, triangles
    
    def parse_ascii_stl_advanced(self, file_handle):
        """Enhanced ASCII STL parsing with triangle extraction"""
        vertices = []
        triangles = []
        current_triangle = []
        vertex_count = 0
        max_vertices = 30000  # Increased limit
        
        try:
            for line_num, line in enumerate(file_handle):
                if vertex_count >= max_vertices:
                    break
                    
                line = line.decode('utf-8', errors='ignore').strip()
                
                if line.startswith('vertex'):
                    try:
                        parts = line.split()
                        if len(parts) >= 4:
                            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                            vertex = [x, y, z]
                            vertices.append(vertex)
                            current_triangle.append(vertex)
                            vertex_count += 1
                            
                            # Complete triangle when we have 3 vertices
                            if len(current_triangle) == 3:
                                triangles.append(current_triangle.copy())
                                current_triangle = []
                                
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error reading ASCII STL: {e}")
            
        return vertices, triangles
    
    def parse_binary_stl(self, file_handle):
        """Parse binary STL format"""
        import struct
        import numpy as np
        
        vertices = []
        
        # Skip header (80 bytes)
        file_handle.seek(80)
        
        # Read number of triangles
        num_triangles_data = file_handle.read(4)
        if len(num_triangles_data) < 4:
            return vertices
            
        num_triangles = struct.unpack('<I', num_triangles_data)[0]
        
        # Read triangles (limit to prevent memory issues)
        max_triangles = min(num_triangles, 50000)  # Limit for performance
        
        for i in range(max_triangles):
            try:
                # Skip normal vector (12 bytes)
                file_handle.seek(file_handle.tell() + 12)
                
                # Read 3 vertices (36 bytes total)
                for j in range(3):
                    vertex_data = file_handle.read(12)
                    if len(vertex_data) < 12:
                        return vertices
                    x, y, z = struct.unpack('<fff', vertex_data)
                    vertices.append([x, y, z])
                
                # Skip attribute byte count (2 bytes)
                file_handle.seek(file_handle.tell() + 2)
                
            except Exception as e:
                print(f"Error reading triangle {i}: {e}")
                break
                
        return vertices
    
    def parse_ascii_stl(self, file_handle):
        """Parse ASCII STL format"""
        vertices = []
        vertex_count = 0
        max_vertices = 15000  # Limit for performance
        
        try:
            for line_num, line in enumerate(file_handle):
                if vertex_count >= max_vertices:
                    break
                    
                line = line.decode('utf-8', errors='ignore').strip()
                
                if line.startswith('vertex'):
                    try:
                        parts = line.split()
                        if len(parts) >= 4:
                            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                            vertices.append([x, y, z])
                            vertex_count += 1
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error reading ASCII STL: {e}")
            
        return vertices
    
    def setup_enhanced_3d_interactions(self):
        """Setup enhanced mouse and keyboard interactions for 3D view"""
        try:
            # Store initial view state
            self.last_mouse_pos = None
            self.is_rotating = False
            
            # Connect enhanced interaction events
            self.main_vtk_canvas.mpl_connect('button_press_event', self.on_mouse_press_3d)
            self.main_vtk_canvas.mpl_connect('button_release_event', self.on_mouse_release_3d)
            self.main_vtk_canvas.mpl_connect('motion_notify_event', self.on_mouse_move_3d)
            self.main_vtk_canvas.mpl_connect('scroll_event', self.on_scroll_3d)
            self.main_vtk_canvas.mpl_connect('key_press_event', self.on_key_press_3d)
            
            # Enable focus for key events
            self.main_vtk_canvas.get_tk_widget().focus_set()
            
        except Exception as e:
            print(f"Error setting up 3D interactions: {e}")
    
    def on_mouse_press_3d(self, event):
        """Handle mouse press for 3D interaction"""
        if event.inaxes == self.ax3d:
            self.last_mouse_pos = (event.x, event.y)
            self.is_rotating = True
    
    def on_mouse_release_3d(self, event):
        """Handle mouse release for 3D interaction"""
        self.is_rotating = False
        self.last_mouse_pos = None
    
    def on_mouse_move_3d(self, event):
        """Handle mouse movement for 3D rotation"""
        if self.is_rotating and self.last_mouse_pos and event.inaxes == self.ax3d:
            try:
                dx = event.x - self.last_mouse_pos[0]
                dy = event.y - self.last_mouse_pos[1]
                
                # Update viewing angles based on mouse movement
                sensitivity = 0.5
                self.current_azim += dx * sensitivity
                self.current_elev -= dy * sensitivity  # Invert for natural feel
                
                # Clamp elevation to reasonable range
                self.current_elev = max(-90, min(90, self.current_elev))
                
                # Apply the rotation
                self.ax3d.view_init(elev=self.current_elev, azim=self.current_azim)
                self.main_vtk_canvas.draw_idle()  # Use draw_idle for smooth updates
                
                self.last_mouse_pos = (event.x, event.y)
            except Exception as e:
                print(f"Error during mouse rotation: {e}")
    
    def on_scroll_3d(self, event):
        """Handle scroll wheel for 3D zooming"""
        if event.inaxes == self.ax3d and hasattr(self, 'geometry_bounds'):
            try:
                mid_x, mid_y, mid_z, current_range = self.geometry_bounds
                
                # Zoom in/out based on scroll direction
                if event.step > 0:
                    zoom_factor = 0.9  # Zoom in
                else:
                    zoom_factor = 1.1  # Zoom out
                
                new_range = current_range * zoom_factor
                
                # Update bounds
                self.ax3d.set_xlim(mid_x - new_range, mid_x + new_range)
                self.ax3d.set_ylim(mid_y - new_range, mid_y + new_range)
                self.ax3d.set_zlim(mid_z - new_range, mid_z + new_range)
                
                # Store new range
                self.geometry_bounds = (mid_x, mid_y, mid_z, new_range)
                
                self.main_vtk_canvas.draw_idle()
            except Exception as e:
                print(f"Error during scroll zoom: {e}")
    
    def on_key_press_3d(self, event):
        """Handle keyboard shortcuts for 3D view"""
        try:
            if event.key == 'r':
                self.reset_3d_view_enhanced()
            elif event.key == 'up':
                self.current_elev = min(90, self.current_elev + 5)
                self.ax3d.view_init(elev=self.current_elev, azim=self.current_azim)
                self.main_vtk_canvas.draw_idle()
            elif event.key == 'down':
                self.current_elev = max(-90, self.current_elev - 5)
                self.ax3d.view_init(elev=self.current_elev, azim=self.current_azim)
                self.main_vtk_canvas.draw_idle()
            elif event.key == 'left':
                self.current_azim -= 5
                self.ax3d.view_init(elev=self.current_elev, azim=self.current_azim)
                self.main_vtk_canvas.draw_idle()
            elif event.key == 'right':
                self.current_azim += 5
                self.ax3d.view_init(elev=self.current_elev, azim=self.current_azim)
                self.main_vtk_canvas.draw_idle()
        except Exception as e:
            print(f"Error handling key press: {e}")
    
    def reset_3d_view_enhanced(self):
        """Enhanced reset view with smooth transition"""
        try:
            if hasattr(self, 'ax3d') and hasattr(self, 'current_coords'):
                # Reset viewing angles
                self.current_azim = 45
                self.current_elev = 25
                self.ax3d.view_init(elev=self.current_elev, azim=self.current_azim)
                
                # Reset zoom to fit geometry
                if hasattr(self, 'current_coords'):
                    x_coords, y_coords, z_coords = self.current_coords
                    x_size = np.max(x_coords) - np.min(x_coords)
                    y_size = np.max(y_coords) - np.min(y_coords)
                    z_size = np.max(z_coords) - np.min(z_coords)
                    
                    max_range = max(x_size, y_size, z_size) / 2.0
                    mid_x = (np.min(x_coords) + np.max(x_coords)) * 0.5
                    mid_y = (np.min(y_coords) + np.max(y_coords)) * 0.5
                    mid_z = (np.min(z_coords) + np.max(z_coords)) * 0.5
                    
                    padding = max_range * 0.1
                    self.ax3d.set_xlim(mid_x - max_range - padding, mid_x + max_range + padding)
                    self.ax3d.set_ylim(mid_y - max_range - padding, mid_y + max_range + padding)
                    self.ax3d.set_zlim(mid_z - max_range - padding, mid_z + max_range + padding)
                    
                    # Update stored bounds
                    self.geometry_bounds = (mid_x, mid_y, mid_z, max_range)
                
                self.main_vtk_canvas.draw()
                self.status_label.config(text="View reset to default position")
        except Exception as e:
            print(f"Error resetting 3D view: {e}")
    
    def toggle_wireframe_mode(self):
        """Toggle between solid and wireframe display modes"""
        try:
            if hasattr(self, 'current_geometry_file'):
                # Re-render with different style
                self.create_vtk_free_3d_visualization(self.current_geometry_file)
                self.status_label.config(text="Display mode toggled")
        except Exception as e:
            print(f"Error toggling wireframe: {e}")
    
    def toggle_projection(self):
        """Toggle between perspective and orthographic projection"""
        try:
            if hasattr(self, 'ax3d'):
                # Note: matplotlib 3D doesn't support true orthographic, 
                # but we can simulate it by adjusting the view distance
                current_dist = self.ax3d.dist if hasattr(self.ax3d, 'dist') else 10
                if current_dist > 50:
                    self.ax3d.dist = 10  # Perspective
                    btn_text = "Orthographic"
                else:
                    self.ax3d.dist = 100  # More orthographic-like
                    btn_text = "Perspective"
                
                # Update button text
                for widget in self.control_buttons:
                    if 'graphic' in str(widget['text']).lower():
                        widget.config(text=btn_text)
                        break
                
                self.main_vtk_canvas.draw()
        except Exception as e:
            print(f"Error toggling projection: {e}")
        """Fallback display when STL parsing fails"""
        try:
            self.main_vtk_figure.clear()
            ax = self.main_vtk_figure.add_subplot(111)
            ax.set_facecolor('black')
            
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            
            ax.text(0.5, 0.6, f"STL File Loaded", transform=ax.transAxes, 
                   fontsize=18, color='white', ha='center', weight='bold')
            ax.text(0.5, 0.5, filename, transform=ax.transAxes, 
                   fontsize=14, color='lightblue', ha='center')
            ax.text(0.5, 0.4, f"File Size: {file_size:.2f} MB", transform=ax.transAxes, 
                   fontsize=12, color='lightgreen', ha='center')
            ax.text(0.5, 0.2, "VTK-Free parsing available", transform=ax.transAxes, 
                   fontsize=12, color='cyan', ha='center')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            self.main_vtk_figure.patch.set_facecolor('black')
            self.main_vtk_canvas.draw()
            
        except Exception as e:
            print(f"Error creating matplotlib display: {e}")
    
    def reset_pyvista_view(self):
        """Reset PyVista camera view"""
        try:
            if hasattr(self, 'pv_plotter'):
                import pyvista as pv
                self.pv_plotter.reset_camera()
                self.pv_plotter.camera.azimuth = 45
                self.pv_plotter.camera.elevation = 25
        except Exception as e:
            print(f"Error resetting PyVista view: {e}")
    
    def toggle_pyvista_wireframe(self):
        """Toggle wireframe mode in PyVista"""
        try:
            if hasattr(self, 'pv_plotter') and hasattr(self, 'current_geometry_file'):
                import pyvista as pv
                self.pv_plotter.clear()
                mesh = pv.read(self.current_geometry_file)
                
                # Toggle between surface and wireframe
                if not hasattr(self, 'wireframe_mode'):
                    self.wireframe_mode = False
                    
                self.wireframe_mode = not self.wireframe_mode
                
                if self.wireframe_mode:
                    self.pv_plotter.add_mesh(mesh, style='wireframe', color='cyan')
                else:
                    self.pv_plotter.add_mesh(mesh, color='lightblue', show_edges=True)
                    
        except Exception as e:
            print(f"Error toggling wireframe: {e}")
    
    def toggle_pyvista_lighting(self):
        """Toggle lighting in PyVista"""
        try:
            if hasattr(self, 'pv_plotter'):
                if not hasattr(self, 'lighting_enabled'):
                    self.lighting_enabled = True
                    
                self.lighting_enabled = not self.lighting_enabled
                
                if self.lighting_enabled:
                    self.pv_plotter.enable_lightkit()
                else:
                    self.pv_plotter.disable_lightkit()
                    
        except Exception as e:
            print(f"Error toggling lighting: {e}")
    
    def save_pyvista_screenshot(self):
        """Save screenshot of PyVista visualization"""
        try:
            if hasattr(self, 'pv_plotter'):
                filename = f"splash_3d_screenshot_{int(time.time())}.png"
                self.pv_plotter.screenshot(filename)
                self.status_label.config(text=f"Screenshot saved: {filename}")
        except Exception as e:
            print(f"Error saving screenshot: {e}")
    
    def update_pyvista_display(self, file_path):
        """Update existing PyVista display with new file"""
        try:
            if hasattr(self, 'pv_plotter'):
                import pyvista as pv
                self.pv_plotter.clear()
                mesh = pv.read(file_path)
                self.pv_plotter.add_mesh(mesh, color='lightblue', show_edges=True)
                
                filename = os.path.basename(file_path)
                self.status_label.config(text=f"PyVista updated: {filename}")
        except Exception as e:
            print(f"Error updating PyVista display: {e}")
        """Display interactive geometry directly in the main window using safe matplotlib approach"""
        try:
            # Hide or minimize the text box to make room for visualization
            self.text_box.grid_forget()
            
            # Store geometry info for refresh capability
            self.current_geometry_file = file_path
            
            # Create matplotlib figure and canvas in MAIN area with interactive capabilities
            if not hasattr(self, 'main_vtk_figure') or self.main_vtk_figure is None:
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
                from matplotlib.figure import Figure
                
                self.main_vtk_figure = Figure(figsize=(12, 9), dpi=80, facecolor='black')
                self.main_vtk_canvas = FigureCanvasTkAgg(self.main_vtk_figure, master=self.root)
                # Place in the main visualization area
                self.main_vtk_canvas.get_tk_widget().grid(row=0, column=1, columnspan=4, padx=1, pady=1, sticky="nsew", rowspan=9)
                
                # Add interactive toolbar for matplotlib navigation
                self.toolbar_frame = tk.Frame(self.root)
                self.toolbar_frame.grid(row=9, column=1, columnspan=4, sticky="ew")
                self.nav_toolbar = NavigationToolbar2Tk(self.main_vtk_canvas, self.toolbar_frame)
                self.nav_toolbar.update()
                
                # Add control buttons
                control_frame = tk.Frame(self.root, bg='lightgray')
                control_frame.grid(row=10, column=1, columnspan=4, pady=5, sticky="ew")
                
                ttk.Button(control_frame, text="Reset View", 
                         command=self.reset_3d_view).pack(side=tk.LEFT, padx=5)
                ttk.Button(control_frame, text="Toggle Wireframe", 
                         command=self.toggle_wireframe_view).pack(side=tk.LEFT, padx=5)
                ttk.Button(control_frame, text="Show Console", 
                         command=self.toggle_console_view).pack(side=tk.LEFT, padx=5)
                ttk.Button(control_frame, text="Refresh", 
                         command=self.refresh_geometry_view).pack(side=tk.LEFT, padx=5)
                ttk.Button(control_frame, text="Rotate View", 
                         command=self.rotate_view).pack(side=tk.RIGHT, padx=5)
                
                # Make columns expandable for better layout
                for i in range(1, 5):
                    self.root.columnconfigure(i, weight=1)
            
            # Display the interactive 3D geometry
            self.create_interactive_3d_visualization(file_path)
            
            # Store current view state
            self.current_view = "geometry"
            
        except Exception as e:
            print(f"Error displaying interactive geometry: {e}")
            # Restore text box if display fails
            self.text_box.grid(row=0, column=1, columnspan=4, padx=1, pady=1, sticky="nsew", rowspan=9)
            tk.messagebox.showerror("Visualization Error", f"Could not display geometry: {e}")
    def create_interactive_3d_visualization(self, file_path):
        """Create interactive 3D visualization using matplotlib with proper mouse controls"""
        try:
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            
            # Read STL file safely
            reader = vtk.vtkSTLReader()
            reader.SetFileName(file_path)
            reader.Update()
            polydata = reader.GetOutput()
            
            # Get geometry statistics
            num_points = polydata.GetNumberOfPoints()
            num_cells = polydata.GetNumberOfCells()
            bounds = polydata.GetBounds()
            x_size = bounds[1] - bounds[0]
            y_size = bounds[3] - bounds[2]
            z_size = bounds[5] - bounds[4]
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Clear and create interactive 3D subplot
            self.main_vtk_figure.clear()
            self.ax3d = self.main_vtk_figure.add_subplot(111, projection='3d')
            self.ax3d.set_facecolor('black')
            
            filename = os.path.basename(file_path)
            
            # Extract points and triangles for display
            points = polydata.GetPoints()
            if points:
                # Sample points for performance (but show more than preview)
                num_display_points = min(5000, num_points)
                step = max(1, num_points // num_display_points)
                
                x_coords = []
                y_coords = []
                z_coords = []
                
                for i in range(0, num_points, step):
                    point = points.GetPoint(i)
                    x_coords.append(point[0])
                    y_coords.append(point[1])
                    z_coords.append(point[2])
                
                # Create the 3D scatter plot with better styling
                self.current_plot = self.ax3d.scatter(x_coords, y_coords, z_coords, 
                                                    c='cyan', s=1.0, alpha=0.7, edgecolors='none')
                
                # Set equal aspect ratio
                max_range = max(x_size, y_size, z_size) / 2.0
                mid_x = (min(x_coords) + max(x_coords)) * 0.5
                mid_y = (min(y_coords) + max(y_coords)) * 0.5
                mid_z = (min(z_coords) + max(z_coords)) * 0.5
                
                self.ax3d.set_xlim(mid_x - max_range, mid_x + max_range)
                self.ax3d.set_ylim(mid_y - max_range, mid_y + max_range)
                self.ax3d.set_zlim(mid_z - max_range, mid_z + max_range)
                
                # Style the 3D plot for dark theme
                self.ax3d.set_xlabel('X', color='white', fontsize=10)
                self.ax3d.set_ylabel('Y', color='white', fontsize=10)
                self.ax3d.set_zlabel('Z', color='white', fontsize=10)
                self.ax3d.tick_params(colors='white', labelsize=8)
                
                # Set dark grid
                self.ax3d.xaxis.pane.fill = False
                self.ax3d.yaxis.pane.fill = False
                self.ax3d.zaxis.pane.fill = False
                self.ax3d.xaxis.pane.set_edgecolor('gray')
                self.ax3d.yaxis.pane.set_edgecolor('gray')
                self.ax3d.zaxis.pane.set_edgecolor('gray')
                self.ax3d.xaxis.pane.set_alpha(0.1)
                self.ax3d.yaxis.pane.set_alpha(0.1)
                self.ax3d.zaxis.pane.set_alpha(0.1)
                
                # Set initial viewing angle
                self.ax3d.view_init(elev=20, azim=45)
                
                # Store data for wireframe toggle
                self.current_coords = (x_coords, y_coords, z_coords)
                self.is_wireframe = False
                
            # Add comprehensive title and info
            self.main_vtk_figure.suptitle(f"Interactive 3D: {filename}", color='white', fontsize=14, y=0.95)
            
            # Add detailed info panel
            info_text = (f"📊 {num_points:,} vertices | {num_cells:,} triangles | {file_size_mb:.1f}MB\n"
                        f"📐 {x_size:.1f} × {y_size:.1f} × {z_size:.1f}\n"
                        f"🖱️ Use toolbar below for pan/zoom/rotate | Mouse for 3D navigation")
            
            self.main_vtk_figure.text(0.02, 0.02, info_text, 
                                    transform=self.main_vtk_figure.transFigure,
                                    fontsize=9, color='yellow', 
                                    verticalalignment='bottom',
                                    bbox=dict(boxstyle='round,pad=0.5', 
                                            facecolor='black', alpha=0.8))
            
            # Set dark background
            self.main_vtk_figure.patch.set_facecolor('black')
            
            # Draw the canvas
            self.main_vtk_canvas.draw()
            
            # Update status
            self.status_label.config(text=f"Interactive 3D loaded: {filename} | Use mouse + toolbar for navigation")
            
        except Exception as e:
            print(f"Error creating interactive 3D visualization: {e}")
            # Fallback to enhanced preview
            self.display_safe_geometry_info(file_path)
    
    def reset_3d_view(self):
        """Reset 3D view to default angle"""
        try:
            if hasattr(self, 'ax3d'):
                self.ax3d.view_init(elev=20, azim=45)
                self.main_vtk_canvas.draw()
        except Exception as e:
            print(f"Error resetting view: {e}")
    
    def toggle_wireframe_view(self):
        """Toggle between scatter plot and wireframe view"""
        try:
            if hasattr(self, 'ax3d') and hasattr(self, 'current_coords'):
                x_coords, y_coords, z_coords = self.current_coords
                
                # Clear current plot
                self.ax3d.clear()
                self.ax3d.set_facecolor('black')
                
                if not self.is_wireframe:
                    # Switch to wireframe-style view
                    self.ax3d.plot_wireframe(
                        np.array([x_coords[::50]]), 
                        np.array([y_coords[::50]]), 
                        np.array([z_coords[::50]]), 
                        color='cyan', alpha=0.6, linewidth=0.5
                    )
                    self.is_wireframe = True
                else:
                    # Switch back to scatter plot
                    self.ax3d.scatter(x_coords, y_coords, z_coords, 
                                    c='cyan', s=1.0, alpha=0.7, edgecolors='none')
                    self.is_wireframe = False
                
                # Restore styling
                self.ax3d.set_xlabel('X', color='white', fontsize=10)
                self.ax3d.set_ylabel('Y', color='white', fontsize=10)
                self.ax3d.set_zlabel('Z', color='white', fontsize=10)
                self.ax3d.tick_params(colors='white', labelsize=8)
                
                # Restore limits
                max_range = max(max(x_coords) - min(x_coords), 
                              max(y_coords) - min(y_coords), 
                              max(z_coords) - min(z_coords)) / 2.0
                mid_x = (min(x_coords) + max(x_coords)) * 0.5
                mid_y = (min(y_coords) + max(y_coords)) * 0.5
                mid_z = (min(z_coords) + max(z_coords)) * 0.5
                
                self.ax3d.set_xlim(mid_x - max_range, mid_x + max_range)
                self.ax3d.set_ylim(mid_y - max_range, mid_y + max_range)
                self.ax3d.set_zlim(mid_z - max_range, mid_z + max_range)
                
                self.main_vtk_canvas.draw()
                
        except Exception as e:
            print(f"Error toggling wireframe: {e}")
    
    def open_with_external_viewer(self, file_path):
        """Fallback method to open STL with system default application"""
        try:
            import subprocess
            subprocess.run(["open", file_path], check=True)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not open file with external viewer: {e}")
        """
        Open the 3D VTK viewer in a separate window with crash protection
        """
        try:
            # Use current geometry file if available, otherwise fall back to selected_file_path
            file_path = None
            if hasattr(self, 'current_geometry_file') and self.current_geometry_file:
                file_path = self.current_geometry_file
            elif hasattr(self, 'selected_file_path') and self.selected_file_path:
                file_path = self.selected_file_path
            
            if not file_path:
                tk.messagebox.showerror("Error", "No geometry file selected for visualization.")
                return

            # Check if file exists and is STL
            if not os.path.exists(file_path):
                tk.messagebox.showerror("Error", f"File not found: {file_path}")
                return
                
            if not file_path.lower().endswith(".stl"):
                tk.messagebox.showerror("Error", "Splash Visualizer currently supports only STL files.")
                return

            # Create VTK viewer window
            self.create_vtk_viewer_window(file_path)
                
        except Exception as e:
            print(f"Error opening 3D viewer: {e}")
            tk.messagebox.showerror("3D Viewer Error", f"Could not open 3D viewer: {e}")
    
    def create_vtk_viewer_window(self, file_path):
        """Create VTK viewer using separate process approach (most stable)"""
        try:
            # Create a standalone VTK viewer script and launch as separate process
            self.launch_standalone_vtk_viewer(file_path)
            
        except Exception as e:
            print(f"Error creating VTK viewer: {e}")
            # Fallback to info window
            self.show_geometry_info_window(file_path)
    
    def launch_standalone_vtk_viewer(self, file_path):
        """Launch VTK viewer in completely separate process to avoid crashes"""
        try:
            import subprocess
            import sys
            import tempfile
            
            # Create standalone VTK viewer script
            viewer_script_content = '''
import vtk
import sys
import os

def create_standalone_viewer(stl_file):
    """Create standalone VTK viewer window"""
    try:
        # Read STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_file)
        reader.Update()
        
        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        
        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.8, 0.9, 1.0)  # Light blue
        
        # Create renderer
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(0.1, 0.1, 0.2)  # Dark background
        
        # Add lighting
        light1 = vtk.vtkLight()
        light1.SetPosition(1, 1, 1)
        light1.SetIntensity(0.8)
        renderer.AddLight(light1)
        
        light2 = vtk.vtkLight()
        light2.SetPosition(-1, -1, 1)
        light2.SetIntensity(0.4)
        renderer.AddLight(light2)
        
        # Create render window
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(900, 700)
        render_window.SetWindowName(f"Splash 3D Viewer - {os.path.basename(stl_file)}")
        
        # Create interactor
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)
        
        # Set trackball camera style
        style = vtk.vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(style)
        
        # Add keyboard shortcuts
        def keypress_callback(obj, event):
            key = obj.GetKeySym().lower()
            if key == 'r':
                renderer.ResetCamera()
                render_window.Render()
            elif key == 'w':
                prop = actor.GetProperty()
                if prop.GetRepresentation() == vtk.VTK_SURFACE:
                    prop.SetRepresentation(vtk.VTK_WIREFRAME)
                    prop.SetLineWidth(1)
                else:
                    prop.SetRepresentation(vtk.VTK_SURFACE)
                render_window.Render()
            elif key == 'q' or key == 'escape':
                interactor.TerminateApp()
        
        interactor.AddObserver("KeyPressEvent", keypress_callback)
        
        # Reset camera and start
        renderer.ResetCamera()
        render_window.Render()
        
        print(f"3D Viewer opened for {stl_file}")
        print("Controls:")
        print("  Mouse left: Rotate")
        print("  Mouse right: Zoom") 
        print("  Mouse middle: Pan")
        print("  'R' key: Reset camera")
        print("  'W' key: Toggle wireframe")
        print("  'Q' or 'Esc': Close viewer")
        
        # Start interaction
        interactor.Start()
        
    except Exception as e:
        print(f"VTK Viewer Error: {e}")
        input("Press Enter to close...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_standalone_viewer(sys.argv[1])
    else:
        print("No STL file specified")
        input("Press Enter to close...")
'''
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(viewer_script_content)
                script_path = f.name
            
            # Get Python executable from current virtual environment
            python_exe = sys.executable
            
            # Launch viewer in separate process (non-blocking)
            try:
                process = subprocess.Popen([python_exe, script_path, file_path],
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         start_new_session=True)  # Fully detached process
                
                self.status_label.config(text=f"3D Viewer launched: {os.path.basename(file_path)} (separate window)")
                
                # Clean up script file after a delay
                def cleanup_script():
                    try:
                        import time
                        time.sleep(2)  # Give time for process to start
                        os.unlink(script_path)
                    except:
                        pass
                
                import threading
                threading.Thread(target=cleanup_script, daemon=True).start()
                
            except Exception as launch_error:
                print(f"Failed to launch VTK viewer: {launch_error}")
                # Clean up script file
                try:
                    os.unlink(script_path)
                except:
                    pass
                # Show info window instead
                self.show_geometry_info_window(file_path)
                
        except Exception as e:
            print(f"Error creating VTK viewer script: {e}")
            self.show_geometry_info_window(file_path)
    
    def show_geometry_info_window(self, file_path):
        """Show geometry information in a Tkinter window when VTK fails"""
        try:
            # Create info window
            info_window = tk.Toplevel(self.root)
            info_window.title(f"Geometry Info - {os.path.basename(file_path)}")
            info_window.geometry("500x400")
            info_window.configure(bg='black')
            
            # Create main frame
            main_frame = tk.Frame(info_window, bg='black')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Get STL information
            try:
                reader = vtk.vtkSTLReader()
                reader.SetFileName(file_path)
                reader.Update()
                polydata = reader.GetOutput()
                
                num_points = polydata.GetNumberOfPoints()
                num_cells = polydata.GetNumberOfCells()
                bounds = polydata.GetBounds()
                x_size = bounds[1] - bounds[0]
                y_size = bounds[3] - bounds[2]
                z_size = bounds[5] - bounds[4]
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                
                info_text = f"""STL Geometry Information

File: {os.path.basename(file_path)}
Path: {file_path}

Geometry Statistics:
• Vertices: {num_points:,}
• Triangles: {num_cells:,}
• File Size: {file_size:.2f} MB

Dimensions:
• X: {x_size:.3f}
• Y: {y_size:.3f}
• Z: {z_size:.3f}
• Bounding Box: {x_size:.2f} × {y_size:.2f} × {z_size:.2f}

Complexity: {'High' if num_cells > 100000 else 'Medium' if num_cells > 10000 else 'Low'}

VTK Viewer Status:
Native VTK 3D viewer should have opened in a separate window.
If you don't see it, check your dock or window manager.

The main SplashFOAM window shows a 3D point cloud preview."""
                
            except Exception as e:
                info_text = f"""STL Geometry Information

File: {os.path.basename(file_path)}
Path: {file_path}

Error reading geometry details: {e}

VTK visualization is not available on this system.
The main window shows available geometry information."""
            
            # Create text widget with scrollbar
            text_frame = tk.Frame(main_frame, bg='black')
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            text_widget = tk.Text(text_frame, bg='black', fg='white', 
                                font=('Consolas', 11), wrap=tk.WORD, padx=10, pady=10)
            scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Insert text and make read-only
            text_widget.insert(tk.END, info_text)
            text_widget.configure(state='disabled')
            
            # Add close button
            button_frame = tk.Frame(main_frame, bg='black')
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(button_frame, text="Close", 
                     command=info_window.destroy).pack(side=tk.RIGHT)
            
            # Update status
            self.status_label.config(text=f"Geometry info displayed: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Error creating info window: {e}")
            tk.messagebox.showerror("Error", f"Could not display geometry information: {e}")
    
    def setup_vtk_visualization(self, parent_frame, file_path):
        """Simple VTK test - not used in main implementation"""
        # This function is kept for compatibility but not used
        # The main viewer uses subprocess approach for stability
        return False
    

    def reset_vtk_camera(self):
        """Reset VTK camera view - handled by subprocess viewer"""
        # Camera controls are handled in the separate VTK process
        # Use 'R' key in the VTK viewer window
        pass
    
    def toggle_wireframe(self):
        """Toggle wireframe display - handled by subprocess viewer"""
        # Wireframe toggle is handled in the separate VTK process
        # Use 'W' key in the VTK viewer window
        pass
    
    def close_vtk_viewer(self):
        """Close the VTK viewer - handled by subprocess"""
        # VTK viewer runs in separate process and closes independently
        # Use 'Q' or 'Esc' key in the VTK viewer window
        pass

# -------------------------------- Mesh Construction ------------------------------>
    def create_mesh(self):
        # Check if geometry is loaded
        if not self.geometry_loaded:
            messagebox.showinfo("Geometry Not Loaded", "Please load a geometry before creating the mesh.")
            return

        # Ask the user for mesh type using clickable buttons
        self.mesh_type = self.ask_mesh_type()

        if self.mesh_type is not None:

            # Define the source directory for Allmesh* files and "system" directory
            # Get the script's directory (Source) and go up one level to Splash root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            splash_root = os.path.dirname(script_dir)
            meshing_directory = os.path.join(splash_root, "Meshing")


            # Check if the destination path is the same as the meshing directory
            if os.path.normpath(self.geometry_dest_path) != os.path.normpath(meshing_directory):
                all_mesh_files = glob.glob(os.path.join(meshing_directory, "Allmesh*"))
                
                for file_path in all_mesh_files:
                    try:
                        # Copy each Allmesh* file to the geometry destination path
                        shutil.copy(file_path, self.geometry_dest_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to copy {file_path}: {e}")
                
                # Define the source and destination paths for the "system" directory
                source_system_directory = os.path.join(meshing_directory, "system")
                dest_system_directory = os.path.join(self.geometry_dest_path, "system")
                
                # Remove the existing "system" directory in the destination if it exists
                if os.path.exists(dest_system_directory):
                    shutil.rmtree(dest_system_directory)
                
                try:
                    # Copy the "system" directory to the geometry destination path
                    shutil.copytree(source_system_directory, dest_system_directory)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy 'system' directory: {e}")

            # Read the content of the "meshDict" file
            self.mesh_dict_file_path = os.path.join(self.geometry_dest_path, "system", "meshDict")

            try:
                with open(self.mesh_dict_file_path, "r") as mesh_dict_file:
                    file_content = mesh_dict_file.read()
                    self.selected_mesh_file_content = file_content

                old_values_mesh = {param: match.group(1) for param in self.mesh_params
                                   for match in re.finditer(f'{param}\\s+(\\S+)(;|;//.*)', file_content)}

                # Open a popup to replace mesh parameters
                self.open_replace_mesh_parameters_popup(old_values_mesh)

            except FileNotFoundError:
                tk.messagebox.showerror("Error", f"File not found - {self.mesh_dict_file_path}")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error reading mesh parameters: {e}")  
                             
    def open_replace_mesh_parameters_popup(self, old_values_mesh):
        if old_values_mesh:
            # Open a popup to replace mesh parameters
            ReplaceMeshParameters(self, self.mesh_params, old_values_mesh)
        else:
            tk.messagebox.showerror("Error", "No mesh parameters found in the 'meshDict' file!")

    def start_meshing(self):
    
        # Choosing the right Docker-based script based on the selected mesh type
        if self.mesh_type == "Cartesian":
            script_name = "AllmeshCartesian_Docker"
        elif self.mesh_type == "Polyhedral":
            script_name = "AllmeshPolyhedral_Docker"
        elif self.mesh_type == "Tetrahedral":
            script_name = "AllmeshTetrahedral_Docker"
        else:
            tk.messagebox.showerror("Error", f"Unsupported mesh type: {self.mesh_type_var}")
            return

        # Create the full path to the meshing script
        cartMesh_script = os.path.join(self.geometry_dest_path, script_name)
        
        # Clear and prepare terminal output
        self.clear_terminal_output()
        self.add_terminal_output(f"Starting {self.mesh_type} mesh generation...\n")
        self.add_terminal_output(f"Using Docker script: {script_name}\n")
        self.add_terminal_output("=" * 50 + "\n")
        
        # Initiate the text_box with a nice mesh representation! 
        self.generate_mesh_visual()

        # Running mesh script 
        if os.path.exists(cartMesh_script):
            chmod_command = ["chmod", "+x", cartMesh_script]
            subprocess.run(chmod_command, check=True)

            try:
                # Activating the progress bar "again" - to be on the safe side
                self.progress_bar_canvas_flag = True
                self.start_progress_bar()
                
                self.add_terminal_output("Docker container starting...\n")
                
                # Use Popen to capture real-time output
                command = [f"./{os.path.basename(cartMesh_script)}"]
                process = subprocess.Popen(command, cwd=self.geometry_dest_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

                # Continuously read and insert output into both Text widgets
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break    
                    # Add to both terminal output and main console
                    self.add_terminal_output(line, also_main_console=True)

                # Wait for the process to complete
                process.communicate()
                
                # Enable the load_meshChecked function
                self.separateMeshLogFile = True 
                
                self.add_terminal_output("\n" + "=" * 50 + "\n")
                self.add_terminal_output("Mesh generation process completed!\n")
                
                # Update the status label 
                self.status_label.config(text="Meshing process is finished!")

                # Check the return code and display appropriate messages
                if process.returncode == 0:
                    self.add_terminal_output("✅ Mesh generated successfully!\n")
                    tk.messagebox.showinfo("Mesh is ready", "Mesh is generated successfully!")
                else:
                    self.add_terminal_output("❌ Error during meshing process\n")
                    tk.messagebox.showerror("Meshing Error", "There was an error during meshing. Check the console output.")

            except subprocess.CalledProcessError as e:
                error_msg = f"Error running Docker-based meshing script: {e}\n"
                self.add_terminal_output(error_msg)
                tk.messagebox.showerror("Error", f"Error running Docker-based meshing script: {e}")
            finally:
                self.progress_bar_canvas_flag = False
        else:
            error_msg = "Docker-based meshing script not found!\n"
            self.add_terminal_output(error_msg)
            tk.messagebox.showerror("Error", "Docker-based meshing script not found!")

    # ______Craft your own mesh with the desired type _______

    def ask_mesh_type(self):
        # Create a popup to ask the user for mesh type
        popup = tk.Toplevel(self.root)
        popup.geometry("250x130")

        # Add clickable buttons for mesh type
        ttk.Radiobutton(popup, text="Cartesian", variable=self.mesh_type_var, value="Cartesian").pack()
        ttk.Radiobutton(popup, text="Polyhedral", variable=self.mesh_type_var, value="Polyhedral").pack()
        ttk.Radiobutton(popup, text="Tetrahedral", variable=self.mesh_type_var, value="Tetrahedral").pack()

        # Add a button to confirm the selection
        ttk.Button(popup, text="OK", command=popup.destroy).pack()

        # Wait for the popup to be closed
        self.root.wait_window(popup)

        # Return the selected mesh type
        return self.mesh_type_var.get()
        
    # Decoration function for CAD import  
    def generate_cad_visual(self):
        cad_representation = self.create_cad_visual()
        self.text_box.delete(1.0, tk.END)  # Clear existing content
        self.text_box.insert(tk.END, cad_representation)

    def create_cad_visual(self):
        cad = ""
        cad += "+-----------+\n"
        cad += f"|           |\n"
        cad += "+           +\n"
        cad += f"|           |\n"
        cad += "+           +\n"
        cad += f"|           |\n"
        cad += "+-----------+"
        
         # Add the decorative pattern below the mesh
        pattern = """ 
 ____        _           _        ____    _    ____  
/ ___| _ __ | | __ _ ___| |__    / ___|  / \\  |  _ \\ 
\\___ \\| '_ \\| |/ _` / __| '_ \\  | |     / _ \\ | | | |
 ___) | |_) | | (_| \\__ \\ | | | | |___ / ___ \\| |_| |
|____/| .__/|_|\\__,_|___/_| |_|  \\____/_/   \\_\\____/ 
      |_|                                                                          
_____________________________________________________
\n"""
        return pattern + cad
            
        
    # Decoration function for meshing process    
    def generate_mesh_visual(self):
        mesh_representation = self.create_mesh_visual()
        self.text_box.delete(1.0, tk.END)  # Clear existing content
        self.text_box.insert(tk.END, mesh_representation)

    def create_mesh_visual(self):
        mesh = ""
        mesh += "+---+---+---+\n"
        mesh += f"| 1 | 2 | 3 |\n"
        mesh += "+---+---+---+\n"
        mesh += f"| 6 | 5 | 4 |\n"
        mesh += "+---+---+---+\n"
        mesh += f"| 7 | 8 | 9 |\n"
        mesh += "+---+---+---+\n"
        
         # Add the decorative pattern below the mesh
        pattern = """
 ____        _           _       __  __           _               
/ ___| _ __ | | __ _ ___| |__   |  \\/  | ___  ___| |__   ___ _ __ 
\\___ \\| '_ \\| |/ _` / __| '_ \\  | |\\/| |/ _ \\/ __| '_ \\ / _ \\ '__|
 ___) | |_) | | (_| \\__ \\ | | | | |  | |  __/\\__ \\ | | |  __/ |   
|____/| .__/|_|\\__,_|___/_| |_| |_|  |_|\\___||___/_| |_|\\___|_|   
      |_|                                                         
__________________________________________________________________
\n"""
        return pattern + mesh

          
    # Decoration function for Simulation Run  
    def generate_run_visual(self):
        cad_representation = self.create_run_visual()
        self.text_box.delete(1.0, tk.END)  # Clear existing content
        self.text_box.insert(tk.END, cad_representation)

    def create_run_visual(self):
        run = ""
        run += "+-----------+\n"
        run += f"|           |\n"
        run += "+           +\n"
        run += f"|           |\n"
        run += "+           +\n"
        run += f"|           |\n"
        run += "+-----------+\n"
        
         # Add the decorative pattern below the mesh
        pattern = """   
 ____        _           _       ____  _   _ _   _ 
/ ___| _ __ | | __ _ ___| |__   |  _ \\| | | | \\ | |
\\___ \\| '_ \\| |/ _` / __| '_ \\  | |_) | | | |  \\| |
 ___) | |_) | | (_| \\__ \\ | | | |  _ <| |_| | |\\  |
|____/| .__/|_|\\\\__,_|___/_| |_| |_| \\_\\\\\\____/|_| \\_|
      |_|                                            
_____________________________________________________
\n"""
        return pattern + run
        
    # # Loading an existing OpenFOAM case
    # def load_case(self):
    #     self.selected_directory = filedialog.askdirectory()
    #     if self.selected_directory:
    #         # Check if the selected directory contains the necessary OpenFOAM folders
    #         base_folders = ["constant", "system"]
    #         time_folders = ["0", "0.orig"]  # Check for either '0' or '0.orig'

    #         # Check if 'constant' and 'system' folders exist
    #         base_folders_exist = all(os.path.isdir(os.path.join(self.selected_directory, d)) for d in base_folders)
    #         # Check if either '0' or '0.orig' exists
    #         time_folder_exists = any(os.path.isdir(os.path.join(self.selected_directory, t)) for t in time_folders)

    #         if base_folders_exist and time_folder_exists:
    #             self.selected_file_path = self.selected_directory
    #             self.status_label.config(text=f"Case directory identified: {self.selected_directory}", foreground="darkblue")
    #             self.run_simulation_button["state"] = tk.NORMAL  # Enable the "Run Simulation" button
    #             self.initialize_simulation_button["state"] = tk.NORMAL  
    #             self.configure_simulation_button["state"] = tk.NORMAL  
    #             self.stop_simulation_button["state"] = tk.NORMAL 
                
    #             # Create a dummy 'splash.foam' file in the selected directory
    #             try:
    #                 dummy_file_path = os.path.join(self.selected_directory, "splash.foam")
    #                 with open(dummy_file_path, 'w') as dummy_file:
    #                     dummy_file.write('')  # Write an empty string to create an empty file
    #             except Exception as e:
    #                 self.status_label.config(text=f"Error creating 'splash.foam': {e}", foreground="red")
                    
    #             # Check for constant/polyMesh directory
    #             polyMesh_path = os.path.join(self.selected_directory, "constant", "polyMesh")
    #             if os.path.isdir(polyMesh_path):
    #                 # Prompt the user
    #                 response = messagebox.askyesno("Mesh Confirmation", "This case seems to have a mesh, do you want to load it?")
    #                 if response:
    #                     self.paraview_application()  # Call the function to load the mesh

    #             # Additional OpenFOAM-related checks can be added here
                
    #         else:
    #             messagebox.showerror("Invalid OpenFOAM Case", "The selected folder does not represent a valid OpenFOAM case. ")
    #             self.status_label.config(text="Invalid OpenFOAM case selected!", foreground="red")
    #             self.run_simulation_button["state"] = tk.DISABLED  # Disable the "Run Simulation" button
    #             self.initialize_simulation_button["state"] = tk.DISABLED  
    #             self.configure_simulation_button["state"] = tk.DISABLED  
    #             self.stop_simulation_button["state"] = tk.DISABLED  
    #     else:
    #         self.status_label.config(text="No case directory selected!", foreground="darkblue")
    #         self.run_simulation_button["state"] = tk.DISABLED  # Disable the "Run Simulation" button
    #         self.initialize_simulation_button["state"] = tk.DISABLED  
    #         self.configure_simulation_button["state"] = tk.DISABLED  
    #         self.stop_simulation_button["state"] = tk.DISABLED  

    def load_case(self):
        self.selected_directory = filedialog.askdirectory()
        
        if self.selected_directory:
            # Check if the selected directory contains the necessary OpenFOAM folders
            base_folders = ["constant", "system"]
            time_folders = ["0", "0.orig"]  # Check for either '0' or '0.orig'

            # Validate OpenFOAM case structure
            base_folders_exist = all(os.path.isdir(os.path.join(self.selected_directory, d)) for d in base_folders)
            time_folder_exists = any(os.path.isdir(os.path.join(self.selected_directory, t)) for t in time_folders)

            if base_folders_exist and time_folder_exists:
                self.selected_file_path = self.selected_directory
                self.status_label.config(text=f"Case directory identified: {self.selected_directory}", foreground="darkblue")
                self.run_simulation_button["state"] = tk.NORMAL  
                self.initialize_simulation_button["state"] = tk.NORMAL  
                self.configure_simulation_button["state"] = tk.NORMAL  
                self.stop_simulation_button["state"] = tk.NORMAL  

                # Check for 'mesh' or 'Allmesh' files and execute them
                mesh_script_path = None
                for script_name in ["mesh", "Allmesh"]:
                    script_path = os.path.join(self.selected_directory, script_name)
                    if os.path.isfile(script_path) and os.access(script_path, os.X_OK):  # Ensure it's executable
                        mesh_script_path = script_path
                        break  # Stop searching after the first match

                if mesh_script_path:
                    # Run the meshing script
                    self.status_label.config(text="Executing meshing script, please wait...", foreground="orange")
                    self.text_box.update_idletasks()  # Update_idletasks() 
                    
                    try:
                        subprocess.run(mesh_script_path, shell=True, check=True, cwd=self.selected_directory)
                        self.status_label.config(text="Meshing completed successfully!", foreground="green")
                    except subprocess.CalledProcessError as e:
                        self.status_label.config(text=f"Error executing meshing script: {e}", foreground="red")
                        return  # Stop execution if meshing fails

                # Create a dummy 'splash.foam' file
                try:
                    dummy_file_path = os.path.join(self.selected_directory, "splash.foam")
                    with open(dummy_file_path, 'w') as dummy_file:
                        dummy_file.write('')  # Create an empty file
                except Exception as e:
                    self.status_label.config(text=f"Error creating 'splash.foam': {e}", foreground="red")
                    return

                # Check for existing mesh
                polyMesh_path = os.path.join(self.selected_directory, "constant", "polyMesh")
                if os.path.isdir(polyMesh_path):
                    response = messagebox.askyesno("Mesh Confirmation", "This case has a mesh. Do you want to visualize it in ParaView?")
                    if response:
                        self.launch_paraview_with_case()  # Open ParaView with the case file

            else:
                messagebox.showerror("Invalid OpenFOAM Case", "The selected folder does not represent a valid OpenFOAM case.")
                self.status_label.config(text="Invalid OpenFOAM case selected!", foreground="red")
                self.run_simulation_button["state"] = tk.DISABLED  
                self.initialize_simulation_button["state"] = tk.DISABLED  
                self.configure_simulation_button["state"] = tk.DISABLED  
                self.stop_simulation_button["state"] = tk.DISABLED  
        else:
            self.status_label.config(text="No case directory selected!", foreground="darkblue")
            self.run_simulation_button["state"] = tk.DISABLED  
            self.initialize_simulation_button["state"] = tk.DISABLED  
            self.configure_simulation_button["state"] = tk.DISABLED  
            self.stop_simulation_button["state"] = tk.DISABLED  

    # Function to launch ParaView with splash.foam
    def launch_paraview_with_case(self):
        splash_foam_path = os.path.join(self.selected_directory, "splash.foam")

        if os.path.exists(splash_foam_path):
            self.status_label.config(text="Launching ParaView...", foreground="blue")
            try:
                subprocess.Popen(["paraview", splash_foam_path], cwd=self.selected_directory)
            except Exception as e:
                self.status_label.config(text=f"Error launching ParaView: {e}", foreground="red")
        else:
            messagebox.showerror("File Not Found", "The splash.foam file could not be found.")

    def initialize_simulation(self):
        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was identified. Please make sure your case is loaded properly.")
            return

        allclean_script = os.path.join(self.selected_file_path, "Allclean")
        if os.path.exists(allclean_script):
            chmod_command = ["chmod", "+x", allclean_script]
            subprocess.run(chmod_command, check=True)

            try:
                self.start_progress_bar()
                
                # Use Popen to capture real-time output
                process = subprocess.Popen(["./Allclean"], cwd=self.selected_file_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                
                # Clear previous content from the text box
                self.text_box.delete(1.0, "end")

                # Continuously read and insert output into the Text widget
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    self.text_box.insert("end", line)
                    self.text_box.see("end")  # Scroll to the end to show real-time updates
                    self.text_box.update_idletasks()  # Update the widget
                   
                # Wait for the process to complete
                process.communicate()

                # Check the return code and display appropriate messages
                if process.returncode == 0:
                    tk.messagebox.showinfo("Simulation Initialized", "Simulation directory has been reset to default!")
                    
                else:
                    pass # FLAG! must check what openfoam "returns" in case of a successful operation
                    #tk.messagebox.showerror("Simulation Error", "There was an error during simulation. Check the console output.")
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("Error", f"Error running Allclean script: {e.stderr}")
            finally:
                self.stop_progress_bar()
        else:
        # tk.messagebox.showerror("Error", "Allclean script not found!")
            # Allclean script not found, creating a temporary script to clean the case
            temp_clean_script_path = os.path.join(self.selected_file_path, "temp_clean.sh")
            try:
                with open(temp_clean_script_path, 'w') as temp_script:
                    temp_script.write("#!/bin/bash\n")
                    if hasattr(self, 'selected_openfoam_path') and self.selected_openfoam_path:
                        temp_script.write(f". {self.selected_openfoam_path}\n")  # Source the selected version
                    else:
                        raise Exception("OpenFOAM path is not set. Please select an OpenFOAM version first.")
                    temp_script.write("cd ${0%/*} || exit 1\n")  # Go to the directory
                    temp_script.write(". ${WM_PROJECT_DIR:?}/bin/tools/CleanFunctions\n")  # Tutorial clean functions
                    
                    if 'openfoam' in self.selected_openfoam_path:
                        if '/opt/openfoam' in self.selected_openfoam_path:
                            temp_script.write("foamCleanCase\n")  # Foundation version command
                        elif '/usr/lib/openfoam' in self.selected_openfoam_path:
                            temp_script.write("foamCleanTutorials\n")  # ESI version command
                    else:
                        raise Exception("Unknown OpenFOAM path, no cleaning command executed.")

                chmod_command = ["chmod", "+x", temp_clean_script_path]
                self.text_box.delete(1.0, tk.END)  # Clear existing content
                subprocess.run(chmod_command, check=True)

                self.start_progress_bar()
                # Use Popen to capture real-time output and run the temporary clean script
                process = subprocess.Popen(["./temp_clean.sh"], cwd=self.selected_file_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    self.text_box.insert("end", line)
                    self.text_box.see("end")  # Scroll to the end to show real-time updates
                    self.text_box.update_idletasks()  # Update the widget
                   
                process.communicate()

                if process.returncode == 0:
                    tk.messagebox.showinfo("Simulation Initialized", "Simulation directory has been reset to default!")
                else:
                    raise Exception("Temporary clean script failed to run successfully.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to initialize simulation: {e}")
            finally:
                self.stop_progress_bar()
                if os.path.exists(temp_clean_script_path):
                    os.remove(temp_clean_script_path)
                         
    #+++++++++++++++++++++++++++++++++ Sim Setup ++++++++++++++++++++++++++++++++++++++++           
    # Define this method to read existing parameter values
    def read_simulation_setup_existing_values(self, directory, file_name, param_list):
        file_path = os.path.join(self.selected_file_path, directory, file_name)
        try:
            with open(file_path, "r") as file:
                file_content = file.read()
                existing_values = {
                    param: match.group(1).strip() for param in param_list
                    for match in re.finditer(f'{param}[ \\t]+([^;]+?)(;|[ \\t]*//.*)', file_content)
                }
            
            return existing_values
        except FileNotFoundError:
            #tk.messagebox.showerror("Error", f"File not found - {file_path}")
            self.simulation_running = False  # Let the user try again
            return {}
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading {directory} parameters: {e}")
            return {}

    # Modify open_simulation_setup_popup
    def open_simulation_setup_popup(self):
    
        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was identified. Please make sure your case is loaded properly.")
            return
            
        # Specify the list of parameters for each file
        constant_params = {
            "transportProperties": ["transportModel", "nu"],
            "thermophysicalProperties": ["equationOfState", "molWeight", "Cp", "Hf", "mu", "Pr"],
            "turbulenceProperties": ["simulationType", "RASModel", "printCoeffs"]
            # more files can be added in a similar fashion
        }
        system_params = {
            #"fvSchemes": ["div(phi,U)", "div(phi,k)", "div(phi,epsilon)", "div(phi,omega)", "turbulence", "energy", "method"],
            "fvSchemes": ["turbulence", "energy", "method"],
            "fvSolution": ["nOuterCorrectors", "nCorrectors", "nNonOrthogonalCorrectors", "pMinFactor", "pMaxFactor"],
            "snappyHexMeshDict": ["castellatedMesh", "snap", "addLayers", "maxLocalCells", "maxGlobalCells", "minRefinementCells", "maxLoadUnbalance", "nCellsBetweenLevels", "nSmoothPatch", "tolerance", "nSolveIter", "nRelaxIter", "nFeatureSnapIter", "implicitFeatureSnap", "explicitFeatureSnap", "multiRegionFeatureSnap"]
        }

        # Read existing values for constant parameters
        existing_values_constant = {}
        for file_name, param_list in constant_params.items():
            existing_values_constant.update(self.read_simulation_setup_existing_values("constant", file_name, param_list))

        # Read existing values for system parameters
        existing_values_system = {}
        for file_name, param_list in system_params.items():
            existing_values_system.update(self.read_simulation_setup_existing_values("system", file_name, param_list))

        # Combine existing values for both constant and system parameters
        existing_values = {**existing_values_constant, **existing_values_system}

        # Open a popup to replace simulation setup parameters
        ReplaceSimulationSetupParameters(self, constant_params, system_params, existing_values)
    # ++++++++++++++++++++++++++++++++ Sim Setup ++++++++++++++++++++++++++++++++++++++++

    def update_control_dict_parameters(self):
        # Read the content of the "controlDict" file
        self.control_dict_file_path = os.path.join(self.selected_file_path, "system", "controlDict")

        try:
            with open(self.control_dict_file_path, "r") as control_dict_file:
                file_content = control_dict_file.read()
                self.selected_control_file_content = file_content
                existing_values_control_dict = {
                    param: match.group(1) for param in self.control_dict_params
                    for match in re.finditer(f'{param}\\s+([^;]+)(;|;//.*)', file_content)
                }

            # Open a popup to replace controlDict parameters
            self.open_replace_control_dict_parameters_popup(existing_values_control_dict)

        except FileNotFoundError:
            tk.messagebox.showerror("Error", f"File not found - {self.control_dict_file_path}")
            self.simulation_running = False # Let the user try again 
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading controlDict parameters: {e}")
            
    def open_replace_control_dict_parameters_popup(self, existing_values):
        if existing_values:
            # Open a popup to replace controlDict parameters
            ReplaceControlDictParameters(self, self.control_dict_params, existing_values)
        else:
            tk.messagebox.showerror("Error", "No controlDict parameters found in the 'controlDict' file!")

    # --------------------------- Running the simulation --------------------------------->
    def run_simulation(self):

        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was identified. Please make sure your case is loaded properly.")
            return

        # FLAG! In case the controlDict still has more than 1 instance of "writeNow"
        control_dict_path = os.path.join(self.selected_file_path, "system", "controlDict")
        self.replace_write_now_with_end_time(control_dict_path)
                
        if not self.simulation_running:
            #self.simulation_thread = threading.Thread(target=self.run_openfoam_simulation)
            self.simulation_thread = threading.Thread(target=self.update_control_dict_parameters)
            self.simulation_thread.start()
            self.simulation_running = True
            self.stop_simulation_button["state"] = tk.NORMAL
        else:
            tk.messagebox.showinfo("Simulation Running", "Simulation is already running.")

    def run_openfoam_simulation(self):
        allrun_script = os.path.join(self.selected_file_path, "Allrun")
        if os.path.exists(allrun_script):

            #_____________________________________________________________________________
            # Important FLAG! to run an existing script we need 2 things; 
            # 1- header must be bin/bash
            # 2- sourcing the openfoam version chosen by the user
            
            # Read the current content of the Allrun script
            print(f"Selected OpenFOAM path: {self.selected_openfoam_path}")  # Debug print
            with open(allrun_script, "r") as file:
                lines = file.readlines()

            # Ensure the first line is '#!/bin/bash'
            if not lines[0].startswith("#!/bin/bash"):
                lines[0] = "#!/bin/bash\n"

            source_command = f". {self.selected_openfoam_path}\n" if self.selected_openfoam_path else ""

            # Insert or replace source command after the first line
            if len(lines) > 1 and lines[1].strip().startswith('. '):
                lines[1] = source_command  # Replace the existing source command
            else:
                lines.insert(1, source_command)  # Insert a new source command after the shebang line

            # Write the modified content back to the Allrun script
            with open(allrun_script, "w") as file:
                file.writelines(lines)
            #_____________________________________________________________________________

            chmod_command = ["chmod", "+x", allrun_script]
            subprocess.run(chmod_command, check=True)

            try:
                self.start_progress_bar()

                # Initiate the text_box with a nice mesh representation! 
                self.generate_run_visual()

                # Use Popen to capture real-time output
                process = subprocess.Popen(["./Allrun"], cwd=self.selected_file_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

                # Continuously read and insert output into the Text widget
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    self.text_box.insert("end", line)
                    self.text_box.see("end")  # Scroll to the end to show real-time updates
                    self.text_box.update_idletasks()  # Update the widget
                   
                # Wait for the process to complete
                process.communicate()
                
                # Enable the load_meshChecked function (to allow checking the mesh stats; also while sim is running)
                self.caseMeshLogFile = True
                
                # Enable the load_log_file function (even if the simulation was not terminated gracefully!)
                self.solverLogFile = True 

                # Check the return code and display appropriate messages
                if process.returncode == 0:
                    tk.messagebox.showinfo("Simulation Finished", "Simulation completed successfully.")
                    
                    # Giving the user the possibility to re-run the simulation
                    self.simulation_running = False
                else:
                    pass # FLAG! must check what openfoam "returns" in case of a successful operation
                    #tk.messagebox.showerror("Simulation Error", "There was an error during simulation. Check the console output.")
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("Error", f"Error running Allrun script: {e.stderr}")
            finally:
                self.stop_progress_bar()
                self.stop_simulation_button["state"] = tk.DISABLED
        else:
            tk.messagebox.showerror("Error", "Allrun script not found!")
        
    # --------------------------- Running the simulation ---------------------------------<
        
    def stop_simulation(self): # FLAG! at the moment, the controlDict file needs to be open and saved and closed, for the function to work :/
        if not self.simulation_running:
            tk.messagebox.showinfo("Nothing to Stop", "There's no simulation currently running to stop.")
            return

        control_dict_path = os.path.join(self.selected_file_path, "system", "controlDict")  # FLAG! Duplication..
        if os.path.exists(control_dict_path):
            try:
                subprocess.run(["sed", "-i", '0,/endTime/s//writeNow/', control_dict_path], check=True)
                print(control_dict_path) # FLAG! DEBUGGING        
                tk.messagebox.showinfo("Stop Simulation", "Simulation stopped successfully.")
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("Error", f"Error stopping simulation: {e.stderr}")
        else:
            tk.messagebox.showerror("Error", "controlDict file not found!")

        self.stop_simulation_button["state"] = tk.DISABLED  # FLAG - is that really needed?! 
        
        # Enable the user to user "run simulation" button again
        self.simulation_running = False
        
        # Disable the button until a new sim is launched
        self.stop_simulation_button["state"] = tk.DISABLED

    
    def replace_write_now_with_end_time(self, control_dict_path):
        subprocess.run(["sed", "-i", 's/writeNow/endTime/g', control_dict_path], check=True)
                
    def start_progress_bar(self):
        self.root.after(100, self.update_progress)

    def update_progress(self):
        # Update the progress bar value
        self.progress_bar_canvas.step(5)

        # Check if the flag is activated to stop the progress bar
        if not self.progress_bar_canvas_flag:
            self.stop_progress_bar()
            return  # Exit the method to prevent further updates

        # Schedule the update_progress method to be called after 100 milliseconds
        self.root.after(100, self.update_progress)

    def stop_progress_bar(self):
        # Stop the progress bar
        self.progress_bar_canvas.stop()

        # Set the mode to 'determinate' to reset the progress bar
        self.progress_bar_canvas.configure(mode="determinate")
        self.progress_bar_canvas["value"] = 0
#______________________________________________________________________
    # FLAG: essentially intended to be dedicated for checkMesh script****
    def load_meshChecked(self): # Important, implement an error handling mechanism where the it spits useful info in case no mesh was created yet!
   
        # Check if the file exists
        if self.geometry_dest_path and os.path.exists(self.geometry_dest_path):  # If mesh was created stand alone 
            # Specify the path to the "AllmeshCartesian" file
            allmesh_cartesian_path1 = os.path.join(self.geometry_dest_path, "log.checkMesh")  # Meshing dir.

            # Read the content of the file
            with open(allmesh_cartesian_path1, "r") as file:
                content = file.read()

            # Insert the content into the Text widget
            self.text_box.delete(1.0, "end")  # Clear previous content
            self.text_box.insert("end", content)
        elif self.selected_file_path and os.path.exists(self.selected_file_path):  # If mesh was created stand alone 
            # Specify the path to the "Allrun" file
            allmesh_cartesian_path2 = os.path.join(self.selected_file_path, "log.checkMesh")  # Case dir.

            # Read the content of the file
            with open(allmesh_cartesian_path2, "r") as file:
                content = file.read()

            # Insert the content into the Text widget
            self.text_box.delete(1.0, "end")  # Clear previous content
            self.text_box.insert("end", content)
        else:
            # If the file doesn't exist, display a message in the Text widget
            self.text_box.delete(1.0, "end")  # Clear previous content
            self.text_box.insert("end", "log.checkMesh file not found.")
            messagebox.showinfo("No Mesh Log-File Found!", "Please make sure a mesh is generated first then load its log file.")
#__________________________________________________________________           
    def load_log_file(self):
    
        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was found to be tracked. Please make sure your case is loaded/run properly.")
            return

        # List of identifiable "solver" names 
        solver_names = ["simpleFoam", "pimpleFoam", "icoFoam", "sonicFoam", "compressibleInterFoam", "foamRun"]  # Add more solver names...

        # Check each solver log file
        for solver_name in solver_names:
            log_file_path = os.path.join(self.selected_file_path, f"log.{solver_name}")

            # Check if the file exists
            if os.path.exists(log_file_path):
                # Read the content of the file
                with open(log_file_path, "r") as file:
                    content = file.read()

                # Insert the content into the Text widget
                self.text_box.delete(1.0, "end")  # Clear previous content
                self.text_box.insert("end", content)

                # Break the loop once a log file is found
                break
        else:
            # If none of the log files exist, display a message in the Text widget
            self.text_box.delete(1.0, "end")  # Clear previous content
            self.text_box.insert("end", "No log file found.")
             
# -------------------------------- Plot results ------------------------------  
    # Function to plot results using xmgrace
    def plot_results_xmgrace(self):
    
        xmgrace_sample_file = os.path.join(os.path.pardir, "Resources", "Sample_Results", "stresses.agr")
        try:
            # Check if xmgrace is installed
            subprocess.run(["xmgrace", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Run xmgrace in the same terminal window
            subprocess.run(["xmgrace", xmgrace_sample_file])
        except subprocess.CalledProcessError:
            tk.messagebox.showerror("Error", "xmgrace is not installed or not in the system's PATH.")
# -------------------------------- Plot results ------------------------------  
    #=============================================================================
    def execute_command(self):
        #command = "source ~/.bashrc"; self.entry.get()
        command = self.entry.get()
        
        # Add command info to terminal output
        self.add_terminal_output(f"\n>>> Executing: {command}\n", also_main_console=False)

        # Create a new terminal window and execute the command
        self.terminal_process = subprocess.Popen(
            #f"gnome-terminal -- bash -c 'source ~/.bashrc'",
            f"gnome-terminal -- bash -c '{command}; exec bash'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid,  # Create a new process group
        )
        
        # Disable the execute button
        self.execute_button.config(state=tk.DISABLED)

        # Monitor the terminal process and display the output
        self.monitor_terminal()

    def monitor_terminal(self):
        if self.terminal_process:
            try:
                # Read the standard output and standard error of the terminal
                output, _ = self.terminal_process.communicate(timeout=0.1)
                if output:
                    # Add to both terminal output and main console if output_text exists
                    self.add_terminal_output(output, also_main_console=False)
                    if hasattr(self, 'output_text'):
                        self.output_text.insert(tk.END, output)
                        self.output_text.see(tk.END)
            except subprocess.TimeoutExpired:
                # The terminal process is still running
                self.root.after(100, self.monitor_terminal)
            else:
                # The terminal process has completed
                self.execute_button.config(state=tk.NORMAL)
                self.add_terminal_output("Command completed.\n", also_main_console=False)
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="Command executed successfully")
                
    # ===================Tool tip (hover over the button)=============================================
    def add_tooltip(self, widget, text):
        widget.bind("<Enter>", lambda event: self.show_tooltip_right(widget, text))
        widget.bind("<Leave>", lambda event: self.hide_tooltip())
        
    def show_tooltip_right(self, widget, text):
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 150  # Adjust 25 as needed for the desired distance
        y += widget.winfo_rooty()
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=text, justify='left', background='#ffffe0', relief='solid', borderwidth=1)
        label.pack(ipadx=1)
        
    def hide_tooltip(self):
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            del self.tooltip
                
        
    def setup_ui(self):
        # Create the Text widget
        self.text_box = tk.Text(self.root, wrap=tk.WORD, height=30, width=100)
        self.text_box.grid(row=0, column=1, columnspan=4, padx=1, pady=1, sticky="nsew", rowspan=9)  # Changed columnspan to 4 for better layout
        self.text_box.configure(foreground="lightblue", background="black", font=("courier", 10, "bold"))

        splash_welcome_msg = """
        
        
        
        
        
        
                       __        __   _                            _           
                       \\ \\      / /__| | ___ ___  _ __ ___   ___  | |_ ___     
                        \\ \\ /\\ / / _ \\ |/ __/ _ \\| '_ ` _ \\ / _ \\ | __/ _ \\    
                         \\ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |   
                          \\_/\\_/ \\___|_|\\___\\___/|_| |_| |_|\\___|  \\__\\___/    
                                                                                 
                        ____        _           _     _____ ___    _    __  __ 
                       / ___| _ __ | | __ _ ___| |__ |  ___/ _ \\  / \\  |  \\/  |
                       \\___ \\| '_ \\| |/ _` / __| '_ \\| |_ | | | |/ _ \\ | |\\/| |
                        ___) | |_) | | (_| \\__ \\ | | |  _|| |_| / ___ \\| |  | |
                       |____/| .__/|_|\\__,_|___/_| |_|_|   \\___/_/   \\_\\_|  |_|
                             |_|                                               
             

                                 Your gate to efficient CFD production! 
                                 ______________________________________
        """
        self.text_box.insert(tk.END, splash_welcome_msg)
        
        # Make the Text widget read-only (for now it's "normal", can be "disabled" if needed)
        self.text_box.configure(state="normal")

        # Create a vertical scrollbar for the Text widget
        self.text_box_scrollbar = tk.Scrollbar(self.root, command=self.text_box.yview)
        self.text_box_scrollbar.grid(row=0, column=5, padx=1, pady=1, sticky='nsw', rowspan=9)  # Ensure it sticks to "nsw" for proper resizing
        self.text_box['yscrollcommand'] = self.text_box_scrollbar.set

        # Add Docker/Terminal Output section below CLI and search components
        self.terminal_output_label = tk.Label(self.root, text="Docker/Terminal Output", 
                                            font=("Arial", 11, "bold"), 
                                            bg="white", fg="darkblue")
        self.terminal_output_label.grid(row=13, column=1, columnspan=4, pady=(15,5), padx=5, sticky="ew")

        # Create a dedicated terminal output text widget in main area
        self.terminal_output = scrolledtext.ScrolledText(self.root, 
                                                       height=12, 
                                                       width=100,
                                                       wrap=tk.WORD,
                                                       font=("Courier", 9),
                                                       bg="black",
                                                       fg="lightgreen",
                                                       insertbackground="white")
        self.terminal_output.grid(row=14, column=1, columnspan=4, rowspan=3, pady=5, padx=5, sticky="nsew")
        
        # Add initial message to terminal output
        self.terminal_output.insert(tk.END, "Docker/Terminal Output Console\n")
        self.terminal_output.insert(tk.END, "=" * 50 + "\n")
        self.terminal_output.insert(tk.END, "Ready for mesh generation commands...\n\n")
        self.terminal_output.config(state=tk.DISABLED)  # Make it read-only initially

        # Configure row and column weights for proper resizing
        self.root.grid_rowconfigure(0, weight=1)   # Ensures the row where the text box is resizable
        self.root.grid_rowconfigure(8, weight=1)   # Ensures the row for the scrollbar is resizable
        self.root.grid_rowconfigure(14, weight=1)  # Ensure terminal output row is resizable
        self.root.grid_columnconfigure(1, weight=1)  # Ensures the column where the text box is located resizes
        self.root.grid_columnconfigure(5, weight=0)  # Ensures the scrollbar column doesn't resize excessively    

    def change_theme(self):
        # Ask for font
        current_font = self.text_box.cget("font")
        new_font = simpledialog.askstring("Font", "Enter font (e.g., Arial 12 bold)", initialvalue=current_font)
        if new_font:
            self.text_box.configure(font=new_font)

        # Ask for text color
        text_color = colorchooser.askcolor(color=self.text_box.cget("foreground"))[1]
        if text_color:
            self.text_box.configure(foreground=text_color)

        # Ask for background color
        bg_color = colorchooser.askcolor(color=self.text_box.cget("background"))[1]
        if bg_color:
            self.text_box.configure(background=bg_color)

        # Reset if the Reset checkbox is selected
        if self.reset_var.get():
            self.reset_theme()

    def toggle_reset(self):
        # Toggle between the Reset and user-chosen themes
        if self.reset_var.get():
            self.reset_theme()
        else:
            self.text_box.configure(font=self.initial_font)
            self.text_box.configure(foreground=self.initial_foreground)
            self.text_box.configure(background=self.initial_background)

    def reset_theme(self):
        # Reset to initial values
        self.text_box.configure(font=self.initial_font)
        self.text_box.configure(foreground=self.initial_foreground)
        self.text_box.configure(background=self.initial_background)
        
    def toggle_monitor_simulation(self):
        if self.monitor_simulation_var.get():
            # Call your monitor_simulation function here
            self.monitor_simulation()
        else:
            # Handle the case when the Checkbutton is unchecked (if needed)
            pass
            
    def toggle_simulation_results(self):
        if self.monitor_simulationLog_var.get():
            # Call your simulation_results function here [showing the log file - no more.]
            self.load_log_file()
        else:
            # Handle the case when the Checkbutton is unchecked (if needed)
            pass
                    
    def monitor_simulation(self):
    
        if self.selected_file_path is None:
            tk.messagebox.showerror("Error", "No case was found to be monitored. Please make sure your case is loaded properly.")
            return
            
        # Get the path to solverInfo.dat
        solver_info_file = os.path.join(self.selected_file_path, "postProcessing", "residuals", "0", "solverInfo.dat")
        #solver_info_file = os.path.join(self.selected_file_path, "postProcessing", "residuals", "0", "residuals.dat")

        # Check if the solverInfo file exists
        if not os.path.exists(solver_info_file):
            messagebox.showerror("Error", "SolverInfo file not found!")
            return
        
        # Get the absolute path to the SplashMonitor binary
        splash_monitor_path = os.path.abspath("../Resources/Utilities/SplashMonitor")

        # Construct the SplashMonitor command with the given arguments
        splash_monitor_command = [splash_monitor_path, "-l", "-i", "2", "-r", "1", solver_info_file]

        # Run SplashMonitor in a subprocess, capturing the standard output
        process = subprocess.Popen(splash_monitor_command, stdout=subprocess.PIPE, universal_newlines=True)

        # Check if Gnuplot is installed
        try:
            subprocess.run(["gnuplot", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Gnuplot is not installed. Please install Gnuplot.")
            return

        # Run Gnuplot with the output stream
        gnuplot_command = ["gnuplot", "-persist"]
        gnuplot_process = subprocess.Popen(gnuplot_command, stdin=subprocess.PIPE, universal_newlines=True)

        # Pass the data to Gnuplot
        for line in process.stdout:
            gnuplot_process.stdin.write(line)

        # Close the stdin of the Gnuplot process
        gnuplot_process.stdin.close()

        # Wait for Gnuplot to finish
        gnuplot_process.wait()
        
    #____________________________________________ sourcing OF __________________________________________________    
    # Sourcing openfoam (version option)
    def source_openfoam(self, version, popup):
        paths = {
            "8": "/opt/openfoam8/etc/bashrc",
            "9": "/opt/openfoam9/etc/bashrc",
            "10": "/opt/openfoam10/etc/bashrc",
            "11": "/opt/openfoam11/etc/bashrc",
            "12": "/opt/openfoam12/etc/bashrc",
            "2212": "/usr/lib/openfoam/openfoam2212/etc/bashrc",
            "2306": "/usr/lib/openfoam/openfoam2306/etc/bashrc",
            "2312": "/usr/lib/openfoam/openfoam2312/etc/bashrc",
            "2406": "/usr/lib/openfoam/openfoam2406/etc/bashrc"
        }
        bashrc_path = paths.get(version)
        if not bashrc_path:
            messagebox.showerror("Error", "Unsupported OpenFOAM version specified.")
            popup.destroy()
            return  

        command = f'source {bashrc_path}'
        #command = f'source {bashrc_path} && env'
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable="/bin/bash")
        output, errors = process.communicate()

        if errors:
            error_message = errors.decode()
            messagebox.showerror("Error Sourcing OpenFOAM", f"Failed to source OpenFOAM version {version}. Please make sure the chosen version is pre-installed on your system!")
            self.openfoam_sourced = False
            popup.destroy()
            return
        else: 
            self.selected_openfoam_path = bashrc_path  # Update the path
        
        # Decode the output and split it into lines
        env_vars = output.decode().split('\n')
    
        # Set each environment variable in the current Python process
        for var in env_vars:
            parts = var.split('=', 1)
            if len(parts) == 2:
                os.environ[parts[0]] = parts[1]
                
        # If you reach this point, sourcing was successful
        print(f"Sourced OpenFOAM version {version}!") 
        messagebox.showinfo("Success", f"Sourced OpenFOAM version {version} successfully!")
        self.openfoam_sourced = True
        return True
        popup.destroy()

    def select_openfoam_version(self):
        # Create a popup window
        popup = tk.Toplevel(self.root)
        popup.title("Select OpenFOAM Version")
        popup.geometry("350x450")
        selected_version = tk.StringVar(value="2306")  # Set the default version to v2306

        # Create a style object for custom styling
        style = ttk.Style()

        # Configure radiobutton padding
        style.configure("TRadiobutton", padding=5)

        # Custom style for section titles
        style.configure("Title.TLabel", font=("TkDefaultFont", 12, "bold"), foreground="darkblue")

        # OpenFOAM Foundation Versions
        foundation_frame = ttk.LabelFrame(popup, text="OpenFOAM Foundation", padding=(10, 5))
        foundation_frame.pack(side='top', padx=10, pady=10, fill='both', expand=True)

        # Foundation versions
        foundation_versions = [("v8", "8"), ("v9", "9"), ("v10", "10"), ("v11", "11"), ("v12", "12")]
        for text, version in foundation_versions:
            ttk.Radiobutton(foundation_frame, text=text, variable=selected_version, value=version, style="TRadiobutton").pack(anchor='w')

        # OpenFOAM ESI Versions
        extended_frame = ttk.LabelFrame(popup, text="OpenFOAM ESI", padding=(10, 5))
        extended_frame.pack(side='top', padx=10, pady=10, fill='both', expand=True)

        # ESI versions (default selected is v2306)
        extended_versions = [("v2212", "2212"), ("v2306", "2306"), ("v2312", "2312"), ("v2406", "2406")]
        for text, version in extended_versions:
            ttk.Radiobutton(extended_frame, text=text, variable=selected_version, value=version, style="TRadiobutton").pack(anchor='w')

        # Activate button
        def activate_and_close():
            version = selected_version.get()
            if version:
                self.source_openfoam(version, popup)
                popup.destroy()

        ttk.Button(popup, text="Activate", command=activate_and_close).pack(pady=10)

        # Ensure popup is modal
        popup.transient(self.root)
        popup.grab_set()
        self.root.wait_window(popup)
        
    #____________________________________________ sourcing OF __________________________________________________    
             
    def open_contact_page(self, event=None):
        webbrowser.open_new("https://www.simulitica.com/contact")
    def support_Splash(self, event=None):
        webbrowser.open_new("https://www.buymeacoffee.com/simulitica")
    def splash_online_manual(self, event=None):
        webbrowser.open_new("https://github.com/mohamedalysayed/Splash/tree/main")
    def splash_GPT_page(self, event=None):
        webbrowser.open_new("https://chat.openai.com/g/g-RGYvE3TsL-splash-gpt")
    def cloud_HPC(self, event=None):
        webbrowser.open_new("https://cfddose.substack.com/p/cfd-free-from-complexity")

    # Splash Timer (license related)
    def update_timer(self):
        current_time = time.time()

        # Calculate elapsed time since the app was opened
        app_elapsed_time = current_time - self.start_time
        hours, remainder = divmod(int(app_elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        tenths_of_second = int((app_elapsed_time - int(app_elapsed_time)) * 10)

        # Update the elapsed time label (minutes only)
        self.timer_label.config(text=f"{hours:02d}:{minutes:02d}")
    
        # Load or set the license start date
        if not os.path.exists(self.license_start_date_file):
            with open(self.license_start_date_file, "w") as file:
                file.write(str(current_time))
            license_start_date = current_time
        else:
            with open(self.license_start_date_file, "r") as file:
                license_start_date = float(file.read())

        # Calculate remaining license duration
        elapsed_time_since_start = current_time - license_start_date
        remaining_time = self.license_duration - elapsed_time_since_start

        # Check if it's time to notify about the license expiration
        if 0 < remaining_time <= self.notice_period_before_end:
            self.notify_license_expiration(remaining_time, expiring_soon=True)
        elif remaining_time <= 0:
            self.notify_license_expiration(remaining_time, expiring_soon=False)

        # Schedule the next update if license has not expired (every minute)
        if remaining_time > 0:
            self.root.after(60000, self.update_timer)
        else:
            # Optionally delay closing to allow the user to read the message
            self.root.after(10000, self.root.destroy)  # Closes the app after 10 seconds

    def notify_license_expiration(self, remaining_time, expiring_soon=True):
        # Prevent multiple notifications
        if not hasattr(self, 'license_expiration_notified'):
            self.license_expiration_notified = True  # Set the flag immediately

            if expiring_soon:
                remaining_days = remaining_time / (3600 * 24)  # Convert remaining time in seconds to days
                if remaining_days < 1:
                    # For less than 1 day, show the remaining hours
                    remaining_hours = remaining_time / 3600
                    message = f"License Expiring Soon!\nYour license will expire in less than {remaining_hours:.0f} hours. Please save your work."
                else:
                    # For 1 day or more, show the remaining days
                    message = f"License Expiring Soon!\nYour license will expire in less than {remaining_days:.0f} days. Please save your work."
            else:
                message = "License Expired!\nYour license has already expired. Please renew your license to continue using Splash."

            license_message = (
                "\n"
                f"{message}\n\n"
                "_____________________________________________________________________________\n"
                "\n"
                "Copyright (C) Simulitica Ltd. [now CFD Dose] - All Rights Reserved.\n"
                "This program is licensed under the GNU Lesser General Public License (LGPL) 3.0.\n"
                "You may redistribute and/or modify this software under the terms of the LGPL.\n"
                "For full license details, please refer to the LICENSE file provided with this software.\n"
                "Written by Mohamed Aly SAYED (mohamed.sayed@simulitica.com), November 2023.\n"
                "_____________________________________________________________________________"
            )

            # Create a Toplevel window for the message
            popup = tk.Toplevel(self.root)
            popup.title("Splash v0.2")
            popup.geometry("800x600")  # Adjust the size as needed

            # Create a Label in the Toplevel window to display the message
            license_message_label = tk.Label(popup, text=license_message, font=("Helvetica", 14, "bold"), fg="darkblue", justify='center')
            license_message_label.pack(padx=10, pady=10)

            # Create a PhotoImage object and set it to the Label
            base_path = os.path.dirname(os.path.abspath(__file__))
            welcome_image = tk.PhotoImage(file=os.path.join(base_path, "../Resources/Logos/simulitica_icon_logo.png"))
            #welcome_image = tk.PhotoImage(file="../Resources/Logos/simulitica_icon_logo.png")  
            welcome_image = welcome_image.subsample(4, 4)  # Adjust subsampling as needed
            license_message_label.config(image=welcome_image, compound="top")
            license_message_label.image = welcome_image  # Keep a reference

            # Create a "Renew License Now" button inside the popup
            renew_button = ttk.Button(popup, text="Renew License Now", command=lambda: webbrowser.open_new_tab("https://www.simulitica.com/splash-v1"))
            renew_button.pack(pady=20)  # Adjust padding as needed

# ---------------------------------------------------------------------------<
# Hot links
# https://www.simulitica.com/splash-v10
# https://www.buymeacoffee.com/simulitica # poor simulitica :( 
# https://www.udemy.com/course/t-flows-crash-course-cfd/ -> T-Flows on Udemy
# ---------------------------------------------------------------------------<
    def load_last_recorded_time(self):
        if os.path.exists(self.elapsed_time_file):
            with open(self.elapsed_time_file, "r") as file:
                try:
                    last_time = float(file.read())
                    return time.time() - last_time
                except ValueError:   
                    return time.time()
        else:
            return time.time()

    def save_elapsed_time(self):
        with open(self.elapsed_time_file, "w") as file:
            elapsed_time = time.time() - self.start_time
            file.write(str(elapsed_time))

        # Make the file hidden on Windows
        if os.name == 'nt':  # Checking if the OS is Windows
            os.system(f'attrib +h {self.elapsed_time_file}')
     
    # Saving elapsed time on closing the app (now ignored!)
    def on_closing(self):
        self.save_elapsed_time()
        self.root.destroy()
    
    # === PyVista 3D Visualization Methods ===
    def create_pyvista_controls(self):
        """Create control buttons for PyVista visualization"""
        try:
            control_frame = tk.Frame(self.root, bg='lightgray')
            control_frame.grid(row=10, column=1, columnspan=4, pady=5, sticky="ew")
            
            ttk.Button(control_frame, text="Reset View", 
                     command=self.reset_pyvista_view).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Wireframe", 
                     command=self.toggle_pyvista_wireframe).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Web 3D", 
                     command=lambda: self.create_web_based_3d_visualization(self.current_geometry_file)).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Show Console", 
                     command=self.toggle_console_view).pack(side=tk.LEFT, padx=5)
            
            # Add help text
            help_label = tk.Label(control_frame, 
                                text="PyVista: Full 3D interaction | Right-click for options",
                                fg='#80d0ff', bg='#1a1a1a', font=('Arial', 9))
            help_label.pack(side=tk.RIGHT, padx=10)
            
        except Exception as e:
            print(f"Error creating PyVista controls: {e}")
    
    def reset_pyvista_view(self):
        """Reset PyVista camera view"""
        try:
            if hasattr(self, 'pv_plotter'):
                self.pv_plotter.reset_camera()
                self.pv_plotter.camera.azimuth = 45
                self.pv_plotter.camera.elevation = 25
        except Exception as e:
            print(f"Error resetting PyVista view: {e}")
    
    def toggle_pyvista_wireframe(self):
        """Toggle wireframe mode in PyVista"""
        try:
            if hasattr(self, 'pv_plotter') and hasattr(self, 'current_geometry_file'):
                import pyvista as pv
                self.pv_plotter.clear()
                mesh = pv.read(self.current_geometry_file)
                
                # Toggle between surface and wireframe
                if not hasattr(self, 'wireframe_mode'):
                    self.wireframe_mode = False
                    
                self.wireframe_mode = not self.wireframe_mode
                
                if self.wireframe_mode:
                    self.pv_plotter.add_mesh(mesh, style='wireframe', color='cyan')
                    self.status_label.config(text="Wireframe mode enabled")
                else:
                    self.pv_plotter.add_mesh(mesh, color='lightblue', show_edges=True)
                    self.status_label.config(text="Surface mode enabled")
                    
        except Exception as e:
            print(f"Error toggling wireframe: {e}")
    
    def create_fallback_info_display(self, file_path, message="Visualization failed"):
        """Fallback display when visualization fails"""
        try:
            # Create a simple info display in the main window
            info_frame = tk.Frame(self.root, bg='lightgray')
            info_frame.grid(row=0, column=1, columnspan=4, padx=1, pady=1, sticky="nsew", rowspan=9)
            
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            
            # Create info display
            info_text = f"""STL File Information
            
File: {filename}
Size: {file_size:.2f} MB

{message}

Alternative visualization options:
• Web-based 3D viewer (Plotly)
• External applications (ParaView, Blender)
• Console information display"""
            
            info_label = tk.Label(info_frame, 
                                text=info_text,
                                fg='white', bg='#1a1a1a', 
                                font=('Arial', 12), justify='left')
            info_label.pack(expand=True, fill='both', padx=20, pady=20)
            
            # Add web viewer button
            web_btn = ttk.Button(info_frame, text="Open Web 3D Viewer", 
                               command=lambda: self.create_web_based_3d_visualization(file_path))
            web_btn.pack(pady=10)
            
        except Exception as e:
            print(f"Error creating fallback display: {e}")
        
if __name__ == "__main__":
    root = tk.Tk()
    root.option_add('*tearOff', False)  # Disable menu tear-off
    root.title("Splash v0.2")
    root.wm_title("Splash v0.2")  # Window manager title
    app = Splash(root)
    root.mainloop()
