from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import requests
import json
from collections import Counter
from ai_helper import (
    generate_travel_tips,
    generate_itinerary_suggestions,
    analyze_review_sentiment,
    generate_destination_description,
    suggest_similar_destinations,
    generate_packing_list
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_guide.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    profile_picture = db.Column(db.String(200))
    bio = db.Column(db.Text)
    destinations = db.relationship('Destination', backref='author', lazy=True)
    reviews = db.relationship('Review', backref='author', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Categories: Beach, Mountain, Cities, Cultural, Nature, Historical, Landmarks
    image = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviews = db.relationship('Review', backref='destination', lazy=True)
    favorites = db.relationship('Favorite', backref='destination', lazy=True)
    
    CATEGORIES = ['Beach', 'Mountain', 'Cities', 'Cultural', 'Natural', 'Historical', 'Landmarks']

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    sentiment_analysis = db.Column(db.Text)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destinations = db.relationship('ItineraryDestination', backref='itinerary', lazy=True)

class ItineraryDestination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itinerary.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def get_weather_forecast(location):
    """Get weather forecast for a location using OpenWeatherMap API"""
    API_KEY = 'YOUR_OPENWEATHER_API_KEY'  # You'll need to sign up for a free API key
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    try:
        params = {
            'q': location,
            'appid': API_KEY,
            'units': 'metric'
        }
        response = requests.get(base_url, params=params)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_destination_recommendations(user_id):
    """Get personalized destination recommendations based on user preferences"""
    # Get user's favorite destinations
    user_favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorite_destinations = [fav.destination for fav in user_favorites]
    
    # Analyze user preferences
    categories = Counter([dest.category for dest in favorite_destinations])
    locations = Counter([dest.location.split(',')[-1].strip() for dest in favorite_destinations])
    
    # Find similar destinations
    recommended = Destination.query.filter(
        (Destination.category.in_(categories.keys()) |
         Destination.location.like(f"%{list(locations.keys())[0] if locations else ''}%")) &
        (Destination.id.notin_([d.id for d in favorite_destinations]))
    ).limit(5).all()
    
    return recommended

# Routes
@app.route('/')
def index():
    featured_destinations = Destination.query.order_by(Destination.created_at.desc()).limit(6).all()
    return render_template('index.html', destinations=featured_destinations)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/destination/new', methods=['GET', 'POST'])
@login_required
def new_destination():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        category = request.form.get('category')
        
        # Generate AI description if none provided
        description = request.form.get('description')
        if not description.strip():
            description = generate_destination_description(name, location)
        
        image = request.files.get('image')
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None
        
        destination = Destination(
            name=name,
            description=description,
            location=location,
            category=category,
            image=filename,
            user_id=current_user.id
        )
        
        db.session.add(destination)
        db.session.commit()
        
        return redirect(url_for('destination_detail', id=destination.id))
    
    return render_template('new_destination.html')

@app.route('/destination/<int:id>')
def destination_detail(id):
    destination = Destination.query.get_or_404(id)
    reviews = Review.query.filter_by(destination_id=id).order_by(Review.created_at.desc()).all()
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(
            user_id=current_user.id, 
            destination_id=id
        ).first() is not None
    
    # Get weather forecast
    weather_data = get_weather_forecast(destination.location)
    
    # Get similar destinations
    similar_destinations = Destination.query.filter_by(
        category=destination.category
    ).filter(Destination.id != id).limit(3).all()
    
    return render_template('destination_detail.html',
                         destination=destination,
                         reviews=reviews,
                         is_favorite=is_favorite,
                         weather_data=weather_data,
                         similar_destinations=similar_destinations)

@app.route('/destination/<int:id>/review', methods=['POST'])
@login_required
def add_review(id):
    content = request.form.get('content')
    rating = request.form.get('rating')
    
    # Analyze review sentiment
    sentiment_analysis = analyze_review_sentiment(content)
    
    review = Review(
        content=content,
        rating=rating,
        destination_id=id,
        user_id=current_user.id,
        sentiment_analysis=str(sentiment_analysis)  # Store the analysis
    )
    
    db.session.add(review)
    db.session.commit()
    
    return redirect(url_for('destination_detail', id=id))

@app.route('/destination/<int:id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(id):
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        destination_id=id
    ).first()
    
    if favorite:
        db.session.delete(favorite)
        message = 'Removed from favorites'
    else:
        favorite = Favorite(user_id=current_user.id, destination_id=id)
        db.session.add(favorite)
        message = 'Added to favorites'
    
    db.session.commit()
    return jsonify({'message': message})

@app.route('/destination/<int:id>/weather')
@login_required
def destination_weather(id):
    destination = Destination.query.get_or_404(id)
    weather_data = get_weather_forecast(destination.location)
    return jsonify(weather_data)

@app.route('/destination/<int:id>/ai-tips')
@login_required
def get_ai_travel_tips(id):
    destination = Destination.query.get_or_404(id)
    tips = generate_travel_tips(destination.name, 7)  # Default 7-day trip
    return jsonify(tips)

@app.route('/destination/<int:id>/ai-itinerary')
@login_required
def get_ai_itinerary(id):
    destination = Destination.query.get_or_404(id)
    duration_type = request.args.get('duration_type', 'days')  # 'days' or 'months'
    duration = int(request.args.get('duration', '7'))
    
    # Apply limits based on duration type
    if duration_type == 'days':
        duration = min(duration, 15)  # Max 15 days
    else:  # months
        duration = min(duration, 2)  # Max 2 months
        duration = duration * 30  # Convert months to days
    
    # Get user's interests from their favorite destinations
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    interests = list(set([fav.destination.category for fav in user_favorites]))
    
    itinerary = generate_itinerary_suggestions(destination.name, duration, interests)
    return jsonify(itinerary)

@app.route('/destination/<int:id>/packing-list')
@login_required
def get_packing_list(id):
    destination = Destination.query.get_or_404(id)
    # You might want to determine the season based on travel dates
    season = "summer"  # This could be dynamic based on planned travel dates
    packing_list = generate_packing_list(destination.name, 7, season)
    return jsonify(packing_list)

@app.route('/profile')
@login_required
def profile():
    user_reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()
    return render_template('profile.html', 
                         user=current_user, 
                         reviews=user_reviews,
                         favorites=user_favorites)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    destinations = Destination.query
    if query:
        destinations = destinations.filter(
            db.or_(
                Destination.name.ilike(f'%{query}%'),
                Destination.description.ilike(f'%{query}%'),
                Destination.location.ilike(f'%{query}%')
            )
        )
    if category:
        destinations = destinations.filter_by(category=category)
    
    destinations = destinations.order_by(Destination.created_at.desc()).all()
    return render_template('search.html', destinations=destinations, query=query, category=category)

@app.route('/recommendations')
@login_required
def recommendations():
    recommended_destinations = get_destination_recommendations(current_user.id)
    return render_template('recommendations.html', 
                         destinations=recommended_destinations)

@app.route('/destination/<int:id>/remove', methods=['POST'])
@login_required
def remove_destination(id):
    destination = Destination.query.get_or_404(id)
    if destination.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Remove associated records
    Review.query.filter_by(destination_id=id).delete()
    Favorite.query.filter_by(destination_id=id).delete()
    ItineraryDestination.query.filter_by(destination_id=id).delete()
    
    # Remove image file if it exists
    if destination.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], destination.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(destination)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/itinerary/new', methods=['GET', 'POST'])
@login_required
def new_itinerary():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            if not title:
                flash('Please enter a title for the itinerary.', 'error')
                return redirect(url_for('new_itinerary'))

            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            
            if not start_date_str or not end_date_str:
                flash('Please select both start and end dates.', 'error')
                return redirect(url_for('new_itinerary'))
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            if start_date > end_date:
                flash('End date must be after start date.', 'error')
                return redirect(url_for('new_itinerary'))
            
            itinerary = Itinerary(
                title=title,
                start_date=start_date,
                end_date=end_date,
                user_id=current_user.id
            )
            
            db.session.add(itinerary)
            db.session.commit()
            flash('Itinerary created successfully!', 'success')
            return redirect(url_for('edit_itinerary', id=itinerary.id))
            
        except ValueError as e:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
            return redirect(url_for('new_itinerary'))
        except Exception as e:
            flash('An error occurred while creating the itinerary.', 'error')
            return redirect(url_for('new_itinerary'))
    
    return render_template('new_itinerary.html')

@app.route('/itinerary/<int:id>')
@login_required
def edit_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        flash('You do not have permission to view this itinerary.', 'error')
        return redirect(url_for('index'))
    
    destinations = Destination.query.all()
    return render_template('edit_itinerary.html', 
                         itinerary=itinerary,
                         destinations=destinations,
                         timedelta=timedelta)  

@app.route('/itinerary/<int:id>/add_destination', methods=['POST'])
@login_required
def add_destination_to_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    destination_id = request.form.get('destination_id')
    day_number = request.form.get('day_number')
    notes = request.form.get('notes')
    
    itinerary_dest = ItineraryDestination(
        itinerary_id=id,
        destination_id=destination_id,
        day_number=day_number,
        notes=notes
    )
    
    db.session.add(itinerary_dest)
    db.session.commit()
    
    return jsonify({'message': 'Destination added successfully'})

@app.route('/itinerary/<int:id>/remove_destination/<int:dest_id>', methods=['POST'])
@login_required
def remove_destination_from_itinerary(id, dest_id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    itinerary_dest = ItineraryDestination.query.get_or_404(dest_id)
    if itinerary_dest.itinerary_id != id:
        return jsonify({'error': 'Invalid destination'}), 400
    
    db.session.delete(itinerary_dest)
    db.session.commit()
    
    return jsonify({'message': 'Destination removed successfully'})

@app.route('/itinerary/<int:id>/update_notes/<int:dest_id>', methods=['POST'])
@login_required
def update_destination_notes(id, dest_id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    itinerary_dest = ItineraryDestination.query.get_or_404(dest_id)
    if itinerary_dest.itinerary_id != id:
        return jsonify({'error': 'Invalid destination'}), 400
    
    notes = request.form.get('notes')
    itinerary_dest.notes = notes
    db.session.commit()
    
    return jsonify({'message': 'Notes updated successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
