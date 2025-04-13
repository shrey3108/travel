import os
import shutil
from app import app, db, Destination
from werkzeug.utils import secure_filename

# Dictionary mapping destinations to their local image paths and coordinates
DESTINATION_DATA = {
    "Taj Mahal": {
        "image": "taj_mahal.jpg",
        "latitude": 27.1751,
        "longitude": 78.0421
    },
    "Eiffel Tower": {
        "image": "eiffel_tower.jpg",
        "latitude": 48.8584,
        "longitude": 2.2945
    },
    "Venice": {
        "image": "venice.jpg",
        "latitude": 45.4408,
        "longitude": 12.3155
    },
    "Grand Canyon": {
        "image": "grand_canyon.jpg",
        "latitude": 36.0544,
        "longitude": -112.1401
    },
    "Great Barrier Reef": {
        "image": "great_barrier_reef.jpg",
        "latitude": -18.2871,
        "longitude": 147.6992
    },
    "Mount Fuji": {
        "image": "mount_fuji.jpg",
        "latitude": 35.3606,
        "longitude": 138.7274
    },
    "Dubai": {
        "image": "dubai.jpg",
        "latitude": 25.2048,
        "longitude": 55.2708
    }
}

# Source directory for images
SOURCE_IMAGE_DIR = r"C:\Users\VISHRUTI\Desktop\res\drawable"

def copy_and_save_image(source_image, destination_name):
    """Copy image from source directory and save it to uploads folder"""
    try:
        # Create a filename from the destination name
        filename = secure_filename(f"{destination_name.lower().replace(' ', '_')}.jpg")
        source_path = os.path.join(SOURCE_IMAGE_DIR, source_image)
        dest_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Copy the image
        shutil.copy2(source_path, dest_path)
        return filename
    except Exception as e:
        print(f"Error copying image for {destination_name}: {str(e)}")
    return None

def add_photos_and_location_to_destinations():
    """Add photos and location data to existing destinations"""
    with app.app_context():
        for destination in Destination.query.all():
            if destination.name in DESTINATION_DATA:
                data = DESTINATION_DATA[destination.name]
                # Copy and save the image
                image_filename = copy_and_save_image(
                    data['image'],
                    destination.name
                )
                
                if image_filename:
                    # Update the destination with the image filename and coordinates
                    destination.image = image_filename
                    destination.latitude = data['latitude']
                    destination.longitude = data['longitude']
                    db.session.commit()
                    print(f"Added image and location for {destination.name}")
                else:
                    print(f"Failed to add image for {destination.name}")

if __name__ == "__main__":
    # Ensure the uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Add photos and location data to destinations
    add_photos_and_location_to_destinations()
    print("Photo and location update completed!")
