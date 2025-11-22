#!/usr/bin/env python3
"""
Simple mesh generator for testing purposes
Creates a basic rectangular mesh around the cylinder STL
"""

import vtk
import os
import numpy as np

def create_test_mesh():
    """Create a simple test mesh for visualization"""
    
    # Create a structured grid
    dims = [21, 11, 6]  # nx, ny, nz
    points = vtk.vtkPoints()
    
    # Define domain bounds around the cylinder
    x_range = np.linspace(-2, 8, dims[0])
    y_range = np.linspace(-2, 2, dims[1]) 
    z_range = np.linspace(-1, 1, dims[2])
    
    # Create points
    for k in range(dims[2]):
        for j in range(dims[1]):
            for i in range(dims[0]):
                x = x_range[i]
                y = y_range[j]
                z = z_range[k]
                points.InsertNextPoint(x, y, z)
    
    # Create structured grid
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(dims)
    grid.SetPoints(points)
    
    # Add some scalar data (pressure field simulation)
    pressure = vtk.vtkFloatArray()
    pressure.SetName("Pressure")
    pressure.SetNumberOfComponents(1)
    
    for k in range(dims[2]):
        for j in range(dims[1]):
            for i in range(dims[0]):
                x = x_range[i]
                y = y_range[j]
                # Simple pressure field - higher at inlet, lower at outlet
                p = 100.0 - 10.0 * x + 5.0 * np.sin(y)
                pressure.InsertNextValue(p)
    
    grid.GetPointData().SetScalars(pressure)
    
    # Write to VTK format
    writer = vtk.vtkStructuredGridWriter()
    writer.SetFileName("test_mesh.vtk")
    writer.SetInputData(grid)
    writer.Write()
    
    print(f"✅ Test mesh created with {points.GetNumberOfPoints()} points")
    print(f"✅ Mesh saved as test_mesh.vtk")
    
    return "test_mesh.vtk"

if __name__ == "__main__":
    # Change to the meshing directory
    os.chdir("/Users/david.standingford/Documents/Splash/Resources/Geometry/Meshing")
    
    # Create test mesh
    mesh_file = create_test_mesh()
    
    print(f"🎉 Test mesh generation complete!")
    print(f"You can now load '{mesh_file}' in the VTK viewer.")