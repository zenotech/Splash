#!/usr/bin/env python3
"""
Test script to verify the VTK-free geometry loading works
"""
import sys
import os
import tkinter as tk
sys.path.append('/Users/david.standingford/Documents/Splash/Source')

# Import the main application
from Splash import Splash

def test_geometry_loading():
    """Test loading an STL file directly"""
    print("Testing VTK-free geometry loading...")
    
    # Create the main window
    root = tk.Tk()
    root.withdraw()  # Hide the main window for testing
    
    # Create application instance
    app = Splash(root)
    
    # Test STL file path
    test_stl = "/Users/david.standingford/Documents/Splash/Resources/Geometry/cylinder.stl"
    
    if os.path.exists(test_stl):
        print(f"Testing with: {test_stl}")
        try:
            # Test the VTK-free visualization directly
            app.visualize_stl(test_stl)
            print("✅ VTK-free geometry loading successful!")
            return True
        except Exception as e:
            print(f"❌ Error during geometry loading: {e}")
            return False
    else:
        print(f"❌ Test file not found: {test_stl}")
        return False

if __name__ == "__main__":
    success = test_geometry_loading()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")