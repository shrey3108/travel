import google.generativeai as genai
from typing import List, Dict

# Configure the Gemini API
genai.configure(api_key='AIzaSyBsglKhEy-zLqdmWP7i8DLojoa-QUdd8Hs')

# Get the model
model = genai.GenerativeModel('gemini-pro')

def generate_travel_tips(destination: str, duration: int) -> Dict:
    """Generate personalized travel tips for a destination."""
    prompt = f"""
    Generate travel tips for a {duration}-day trip to {destination}. Include:
    1. Best time to visit
    2. Must-visit attractions
    3. Local cuisine recommendations
    4. Cultural customs and etiquette
    5. Transportation tips
    6. Safety advice
    Format the response as a JSON with these keys.
    """
    
    try:
        response = model.generate_content(prompt)
        # Convert the response to a structured format
        tips = eval(response.text)  # Note: In production, use proper JSON parsing
        return tips
    except Exception as e:
        return {
            "error": "Could not generate travel tips at this time.",
            "details": str(e)
        }

def generate_itinerary_suggestions(destination: str, duration: int, interests: List[str]) -> Dict:
    """Generate a personalized day-by-day itinerary based on user interests."""
    interests_str = ", ".join(interests)
    prompt = f"""
    Create a detailed {duration}-day itinerary for {destination}, focusing on these interests: {interests_str}.
    For each day, include:
    1. Morning activities
    2. Afternoon activities
    3. Evening activities
    4. Recommended restaurants
    5. Travel time estimates
    Format the response as a JSON with days as keys and activities as nested objects.
    """
    
    try:
        response = model.generate_content(prompt)
        # Convert the response to a structured format
        itinerary = eval(response.text)  # Note: In production, use proper JSON parsing
        return itinerary
    except Exception as e:
        return {
            "error": "Could not generate itinerary at this time.",
            "details": str(e)
        }

def analyze_review_sentiment(review_text: str) -> Dict:
    """Analyze the sentiment and key points of a review."""
    prompt = f"""
    Analyze this travel review: "{review_text}"
    Provide:
    1. Sentiment (positive, negative, or neutral)
    2. Key positive points
    3. Key negative points
    4. Overall rating (1-5)
    Format the response as a JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        # Convert the response to a structured format
        analysis = eval(response.text)  # Note: In production, use proper JSON parsing
        return analysis
    except Exception as e:
        return {
            "error": "Could not analyze review at this time.",
            "details": str(e)
        }

def generate_destination_description(destination_name: str, location: str) -> str:
    """Generate an engaging description for a destination."""
    prompt = f"""
    Write an engaging and informative travel description for {destination_name} located in {location}.
    Include:
    1. Brief historical context
    2. Main attractions
    3. Unique features
    4. Why tourists should visit
    Keep it concise but compelling, around 100-150 words.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Could not generate description at this time. Error: {str(e)}"

def suggest_similar_destinations(destination: str) -> List[str]:
    """Suggest similar destinations based on a given place."""
    prompt = f"""
    Suggest 5 similar travel destinations to {destination} that travelers might enjoy.
    Consider:
    1. Similar attractions
    2. Cultural similarities
    3. Geographic proximity
    4. Similar travel experiences
    Return just the names as a Python list.
    """
    
    try:
        response = model.generate_content(prompt)
        # Convert the response to a list
        suggestions = eval(response.text)
        return suggestions[:5]  # Ensure we only return 5 destinations
    except Exception as e:
        return [str(e)]

def generate_packing_list(destination: str, duration: int, season: str) -> List[str]:
    """Generate a customized packing list based on destination and duration."""
    prompt = f"""
    Create a packing list for a {duration}-day trip to {destination} during {season}.
    Consider:
    1. Weather appropriate clothing
    2. Essential documents
    3. Electronics and adapters
    4. Health and safety items
    5. Destination-specific needs
    Return the items as a Python list.
    """
    
    try:
        response = model.generate_content(prompt)
        # Convert the response to a list
        packing_list = eval(response.text)
        return packing_list
    except Exception as e:
        return [str(e)]
