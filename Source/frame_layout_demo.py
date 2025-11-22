import tkinter as tk
from tkinter import ttk, scrolledtext


class FrameBasedLayout:
    """
    A cleaner layout approach using frames instead of complex grid positioning.
    This will be much easier to manage and debug.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.geometry("1400x1000")
        
        # Create main container frames
        self.setup_main_frames()
        
    def setup_main_frames(self):
        """Set up the main layout using frames for different functional areas"""
        
        # Left sidebar for workflow buttons
        self.sidebar_frame = tk.Frame(self.root, bg="lightgrey", width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.sidebar_frame.pack_propagate(False)  # Maintain fixed width
        
        # Right main area container
        self.main_container = tk.Frame(self.root, bg="white")
        self.main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top area: Visualization + controls (takes most space)
        self.visualization_frame = tk.Frame(self.main_container, bg="white", relief=tk.RAISED, bd=1)
        self.visualization_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Middle area: Search and CLI controls (fixed height)
        self.controls_frame = tk.Frame(self.main_container, bg="lightblue", height=80, relief=tk.RAISED, bd=1)
        self.controls_frame.pack(fill=tk.X, pady=5)
        self.controls_frame.pack_propagate(False)  # Maintain fixed height
        
        # Bottom area: Terminal output (moderate height)
        self.terminal_frame = tk.Frame(self.main_container, bg="black", height=250, relief=tk.RAISED, bd=1)
        self.terminal_frame.pack(fill=tk.BOTH, pady=(5, 0))
        self.terminal_frame.pack_propagate(False)  # Maintain fixed height
        
        # Very bottom: Status bar
        self.status_frame = tk.Frame(self.root, bg="darkblue", height=30)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_frame.pack_propagate(False)
        
    def add_workflow_buttons(self):
        """Add workflow buttons to sidebar"""
        buttons = [
            "Import Geometry", "Create Mesh", "Load Case", 
            "Initialize Simulation", "Configure Simulation", 
            "Run Simulation", "Stop Simulation", "Plot Results"
        ]
        
        for i, button_text in enumerate(buttons):
            btn = tk.Button(self.sidebar_frame, text=button_text, 
                          bg="lightblue", font=("Arial", 10))
            btn.pack(fill=tk.X, padx=5, pady=2)
            
    def add_search_and_cli(self):
        """Add search and CLI components to controls frame"""
        # Search section (left side)
        search_section = tk.Frame(self.controls_frame, bg="lightblue")
        search_section.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(search_section, text="Search:", bg="lightblue", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        search_entry = tk.Entry(search_section, width=20)
        search_entry.pack(pady=2)
        search_btn = tk.Button(search_section, text="Find", bg="white", font=("Arial", 9))
        search_btn.pack(pady=2)
        
        # CLI section (right side)  
        cli_section = tk.Frame(self.controls_frame, bg="lightblue")
        cli_section.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(cli_section, text="CLI:", bg="lightblue", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        cli_entry = tk.Entry(cli_section, width=20)
        cli_entry.pack(pady=2)
        cli_btn = tk.Button(cli_section, text="Execute", bg="white", font=("Arial", 9))
        cli_btn.pack(pady=2)
        
    def add_visualization_area(self):
        """Add main visualization area"""
        # Placeholder for VTK or text widget
        viz_label = tk.Label(self.visualization_frame, 
                           text="Main Visualization Area\n(VTK Widget or Text Console)", 
                           bg="white", font=("Arial", 16))
        viz_label.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
    def add_terminal_output(self):
        """Add terminal output area"""
        terminal_label = tk.Label(self.terminal_frame, text="Docker Terminal Output", 
                                bg="black", fg="green", font=("Arial", 12, "bold"))
        terminal_label.pack(anchor=tk.W, padx=5, pady=2)
        
        terminal_text = scrolledtext.ScrolledText(self.terminal_frame, 
                                                bg="black", fg="lightgreen",
                                                font=("Courier", 10))
        terminal_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def add_status_bar(self):
        """Add status bar"""
        status_label = tk.Label(self.status_frame, text="Ready to import geometry", 
                              bg="darkblue", fg="white", font=("Arial", 12))
        status_label.pack(side=tk.LEFT, padx=10)


# Test the layout
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Splash - Frame-Based Layout Demo")
    
    app = FrameBasedLayout(root)
    app.add_workflow_buttons()
    app.add_search_and_cli() 
    app.add_visualization_area()
    app.add_terminal_output()
    app.add_status_bar()
    
    root.mainloop()