    # === PyVista 3D Visualization Methods ===
    def create_pyvista_controls(self):
        """Create control buttons for PyVista visualization"""
        try:
            control_frame = tk.Frame(self.root, bg='#1a1a1a')
            control_frame.grid(row=10, column=1, columnspan=4, pady=5, sticky="ew")
            
            reset_btn = ttk.Button(control_frame, text="Reset View", command=self.reset_pyvista_view)
            reset_btn.pack(side=tk.LEFT, padx=5)
            
            wireframe_btn = ttk.Button(control_frame, text="Wireframe", command=self.toggle_pyvista_wireframe) 
            wireframe_btn.pack(side=tk.LEFT, padx=5)
            
            web_btn = ttk.Button(control_frame, text="Web 3D", command=self.create_web_viewer)
            web_btn.pack(side=tk.LEFT, padx=5)
            
            console_btn = ttk.Button(control_frame, text="Show Console", command=self.toggle_console_view)
            console_btn.pack(side=tk.LEFT, padx=5)
            
            # Add help text
            help_text = "PyVista: Full 3D interaction enabled"
            help_label = tk.Label(control_frame, text=help_text, fg='#80d0ff', bg='#1a1a1a', font=('Arial', 9))
            help_label.pack(side=tk.RIGHT, padx=10)
            
        except Exception as e:
            print(f"Error creating PyVista controls: {e}")
    
    def create_web_viewer(self):
        """Launch web-based 3D viewer"""
        if hasattr(self, 'current_geometry_file'):
            self.create_web_based_3d_visualization(self.current_geometry_file)
    
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
            info_frame = tk.Frame(self.root, bg='#1a1a1a')
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