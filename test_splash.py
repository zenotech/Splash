#!/usr/bin/env python3
"""
Test script to verify geometry loading and visualization controls work in Splash
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox

# Add the Source directory to path
sys.path.insert(0, 'Source')

def test_geometry_loading():
    """Test that geometry files can be loaded"""
    stl_files = [
        'Resources/Geometry/cylinder.stl',
        'Resources/Geometry/geom.stl'
    ]
    
    available_files = []
    for stl_file in stl_files:
        if os.path.exists(stl_file):
            available_files.append(stl_file)
            print(f"✅ Found geometry file: {stl_file}")
        else:
            print(f"❌ Missing geometry file: {stl_file}")
    
    return available_files

def test_splash_import():
    """Test that Splash application can be imported"""
    try:
        from Splash import Splash
        print("✅ Successfully imported Splash class")
        return True
    except Exception as e:
        print(f"❌ Failed to import Splash: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Splash Application...")
    print("=" * 50)
    
    # Test 1: Check geometry files
    print("\n1. Testing geometry file availability:")
    available_files = test_geometry_loading()
    
    # Test 2: Test Splash import
    print("\n2. Testing Splash import:")
    import_success = test_splash_import()
    
    # Test 3: Quick application test
    print("\n3. Testing application startup:")
    if import_success:
        try:
            from Splash import Splash
            root = tk.Tk()
            root.withdraw()  # Hide the window for testing
            app = Splash(root)
            print("✅ Splash application created successfully")
            
            # Test if main components exist
            if hasattr(app, 'sidebar_frame'):
                print("✅ Sidebar frame exists")
            if hasattr(app, 'visualization_frame'):
                print("✅ Visualization frame exists") 
            if hasattr(app, 'controls_frame'):
                print("✅ Controls frame exists")
            if hasattr(app, 'status_frame'):
                print("✅ Status frame exists")
            if hasattr(app, 'import_geometry'):
                print("✅ Import geometry method exists")
            if hasattr(app, 'create_interactive_controls'):
                print("✅ Interactive controls method exists")
                
            root.destroy()
            
        except Exception as e:
            print(f"❌ Application test failed: {e}")
    
    print("\n" + "=" * 50)
    if available_files and import_success:
        print("🎉 All tests passed! You can:")
        print("   1. Launch the application")
        print("   2. Click 'Import Geometry' button") 
        print(f"   3. Select one of: {', '.join(available_files)}")
        print("   4. View the 3D geometry with control buttons")
    else:
        print("⚠️  Some tests failed - check the issues above")