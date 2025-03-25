import os
import requests
from app import app, db, Destination
from werkzeug.utils import secure_filename

# Dictionary mapping destinations to their image URLs
DESTINATION_IMAGES = {
    "Taj Mahal": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=1600",
    "Eiffel Tower": "https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?w=1600",
    "Santorini": "https://images.unsplash.com/photo-1570077188670-6a96fe40e681?w=1600",
    "Machu Picchu": "https://images.unsplash.com/photo-1526392060635-9d6019884377?w=1600",
    "Great Barrier Reef": "https://images.unsplash.com/photo-1582967788606-a171c1080cb0?w=1600",
    "Mount Fuji": "https://images.unsplash.com/photo-1570459027562-4a916cc6113f?w=1600",
    "Venice": "https://images.unsplash.com/photo-1514890547357-a9ee288728e0?w=1600",
    "Grand Canyon": "https://images.unsplash.com/photo-1615551043360-33de8b5f410c?w=1600",
    "Dubai": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1600",
    "Maldives": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=1600"
}

def download_and_save_image(url, destination_name):
    """Download image from URL and save it to uploads folder"""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Create a filename from the destination name
            filename = secure_filename(f"{destination_name.lower().replace(' ', '_')}.jpg")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            
            return filename
    except Exception as e:
        print(f"Error downloading image for {destination_name}: {str(e)}")
    return None

def add_photos_to_destinations():
    """Add photos to existing destinations"""
    with app.app_context():
        for destination in Destination.query.all():
            if destination.name in DESTINATION_IMAGES:
                # Download and save the image
                image_filename = download_and_save_image(
                    DESTINATION_IMAGES[destination.name],
                    destination.name
                )
                
                if image_filename:
                    # Update the destination with the image filename
                    destination.image = image_filename
                    db.session.commit()
                    print(f"Added image for {destination.name}")
                else:
                    print(f"Failed to add image for {destination.name}")

if __name__ == "__main__":
    # Ensure the uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Add photos to destinations
    add_photos_to_destinations()
    print("Photo update completed!")
