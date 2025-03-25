from app import app, db, Destination, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def add_initial_data():
    with app.app_context():
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()

        # List of destinations
        destinations = [
            {
                "name": "Taj Mahal",
                "location": "Agra, India",
                "category": "Historical",
                "description": "The Taj Mahal is an ivory-white marble mausoleum on the right bank of the river Yamuna in Agra, India. It was commissioned in 1632 by the Mughal emperor Shah Jahan to house the tomb of his favorite wife, Mumtaz Mahal. The Taj Mahal is considered the finest example of Mughal architecture and is widely recognized as 'the jewel of Muslim art in India'."
            },
            {
                "name": "Eiffel Tower",
                "location": "Paris, France",
                "category": "Landmarks",
                "description": "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It is named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889, it was initially criticized by some of France's leading artists and intellectuals for its design but has become a global cultural icon of France."
            },
            {
                "name": "Santorini",
                "location": "Cyclades, Greece",
                "category": "Islands",
                "description": "Santorini is one of the Cyclades islands in the Aegean Sea. It was devastated by a volcanic eruption in the 16th century BC, forever shaping its rugged landscape. The whitewashed, cubiform houses of its 2 principal towns, Fira and Oia, cling to cliffs above an underwater caldera (crater). They overlook the sea, small islands to the west and beaches made up of black, red and white lava pebbles."
            },
            {
                "name": "Machu Picchu",
                "location": "Cusco Region, Peru",
                "category": "Historical",
                "description": "Machu Picchu is an Incan citadel set high in the Andes Mountains in Peru, above the Urubamba River valley. Built in the 15th century and later abandoned, it's renowned for its sophisticated dry-stone walls that fuse huge blocks without the use of mortar, intriguing buildings that play on astronomical alignments and panoramic views."
            },
            {
                "name": "Great Barrier Reef",
                "location": "Queensland, Australia",
                "category": "Natural",
                "description": "The Great Barrier Reef is the world's largest coral reef system composed of over 2,900 individual reefs and 900 islands stretching for over 2,300 kilometers. The reef is located in the Coral Sea, off the coast of Queensland, Australia. The Great Barrier Reef can be seen from outer space and is the world's biggest single structure made by living organisms."
            },
            {
                "name": "Mount Fuji",
                "location": "Honshu, Japan",
                "category": "Natural",
                "description": "Mount Fuji is Japan's tallest peak and most iconic landmark. This active stratovolcano has been sacred to the Japanese for centuries. Its symmetrical cone is snow-capped several months of the year, and it is a popular tourist destination for sightseeing and climbing."
            },
            {
                "name": "Venice",
                "location": "Veneto, Italy",
                "category": "Cities",
                "description": "Venice, the capital of northern Italy's Veneto region, is built on more than 100 small islands in a lagoon in the Adriatic Sea. It has no roads, just canals – including the Grand Canal thoroughfare – lined with Renaissance and Gothic palaces. The central square, Piazza San Marco, contains St. Mark's Basilica, which is tiled with Byzantine mosaics."
            },
            {
                "name": "Grand Canyon",
                "location": "Arizona, USA",
                "category": "Natural",
                "description": "The Grand Canyon is a steep-sided canyon carved by the Colorado River in Arizona, United States. The Grand Canyon is 277 miles long, up to 18 miles wide and attains a depth of over a mile. For thousands of years, the area has been continuously inhabited by Native Americans, who built settlements within the canyon and its many caves."
            },
            {
                "name": "Dubai",
                "location": "United Arab Emirates",
                "category": "Cities",
                "description": "Dubai is a city and emirate in the United Arab Emirates known for luxury shopping, ultramodern architecture and a lively nightlife scene. Burj Khalifa, an 830m-tall tower, dominates the skyscraper-filled skyline. At its foot lies Dubai Fountain, with jets and lights choreographed to music."
            },
            {
                "name": "Maldives",
                "location": "South Asia",
                "category": "Islands",
                "description": "The Maldives is a tropical nation in the Indian Ocean composed of 26 ring-shaped atolls, which are made up of more than 1,000 coral islands. It's known for its beaches, blue lagoons and extensive reefs. The capital, Malé, has a busy fish market, restaurants and shops on the main road, Majeedhee Magu."
            }
        ]

        # Add destinations
        for dest_data in destinations:
            destination = Destination(
                name=dest_data["name"],
                description=dest_data["description"],
                location=dest_data["location"],
                category=dest_data["category"],
                user_id=admin.id,
                created_at=datetime.utcnow()
            )
            db.session.add(destination)

        db.session.commit()
        print("Initial data added successfully!")

if __name__ == "__main__":
    add_initial_data()
