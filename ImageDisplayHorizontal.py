import numpy as np
import napari
from tifffile import imread, imwrite
import os

# Load the 3D+t image stack from the TIFF file
image_stack = imread('C2-mitosis.tif')

# Initialize napari viewer
viewer = napari.Viewer()

# Add the 3D+t image stack to the viewer
viewer.add_image(image_stack, name='3D+t Stack')

# Define the points to display in the viewer
points = np.array([[2, 65, 70], [5, 140, 95]])  # Points at z=2 and z=5

viewer.add_points(points, name='Points', size=10, face_color='red')
viewer.dims.ndisplay = 3  # Set the viewer to 3D mode

# Calculate yaw and pitch to align the points horizontally
# Find the direction vector from point 1 to point 2
point1 = points[0] 
point2 = points[1]
direction_vector = point2 - point1

# Normalize the direction vector to get the angle of rotation
# Project this onto the x-y plane for rotation
dx, dy = direction_vector[1], direction_vector[2]

# Calculate yaw: the angle to rotate the direction vector onto the x-axis in the xy-plane
yaw = np.degrees(np.arctan2(dy, dx))  # atan2 gives the angle between the vector and the x-axis

# Now, we calculate the pitch: the angle between the direction vector and the horizontal plane.
# This is the angle between the direction vector's projection onto the xy-plane and the vector's magnitude
dz = direction_vector[0]
pitch = np.degrees(np.arctan2(dz, np.linalg.norm([dx, dy])))  # Pitch is the angle from the xy-plane

# We don't need a roll since we're just rotating to align the points, so we can set roll to zero
roll = 0

# Apply the calculated yaw and pitch to the camera's angles (we don't use roll in this case)
viewer.camera.angles = (pitch, yaw, roll)

# Set the camera position to focus on the center of the image stack
viewer.camera.center =  (point1 + point2) / 2  # Center the camera on the midpoint of the two points

# Optionally, you can also zoom in or adjust the field of view using viewer.camera.zoom
viewer.camera.zoom = 4.0  # You can adjust this zoom value based on the stack size

# Save the perpendicular view (xy-plane) of the rotated stack as a time-lapse of 2D images
output_dir = './output_images/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Save each frame as a 2D image
for t in range(image_stack.shape[0]):
    #viewer.layers[0].data = image_stack[t, :, :]  # Set the current time point (2D slice)
    viewer.dims.set_point(0, t)

    # Capture the screenshot of the current viewer state
    screenshot = viewer.screenshot()  # Capture the current viewer frame

    # Save the screenshot as a TIFF file
    file_path = os.path.join(output_dir, f'time_{t:03d}.tif')
    imwrite(file_path, screenshot)  # Save as TIFF using tifffile
    print(f'Saved frame at time {t} to {file_path}')

# Start the napari viewer
napari.run()
