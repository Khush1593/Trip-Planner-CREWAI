from flask import Flask, render_template, request, jsonify
import json
import os
import markdown2
import requests
from flask_cors import CORS
from src.trip_planner_flow.main import run
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

# Function that handle the modification of the place list created by the first Agent
@app.route('/modify_place_list', methods=['GET', 'POST'])
def modify_place_list_route():
    """
    Route to modify the place list created by the first Agent.
    """
    try:
        if request.method == 'POST':
            # Handle the text update
            text_data = request.get_data(as_text=True)
            
            # Write the modified text to file
            with open('temp_places.txt', 'w', encoding='utf-8') as f:
                f.write(text_data)
            
            # Signal completion
            with open('modification_complete.flag', 'w') as f:
                f.write('done')
                
            return jsonify({'success': True}), 200
        
        # For GET request, read from temporary file
        try:
            with open('temp_places.txt', 'r', encoding='utf-8') as f:
                text_data = f.read()
        except FileNotFoundError:
            text_data = "No place selection data available"
        
        return render_template('modify_text.html', text_data=text_data)
    except Exception as e:
        app.logger.error(f"Error in modify_place_list_route: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
# Function to get flight information from Amadeus API
def get_flight_information(curernt_code, destination_code, date, number_of_members):
    """
    Fetch flight information from Amadeus API based on provided parameters.
    """
    
    token_response = requests.post("https://test.api.amadeus.com/v1/security/oauth2/token",data={
    "grant_type": "client_credentials",
    "client_id": os.environ.get("CLIENT_ID"),
    "client_secret": os.environ.get("CLIENT_SECRET")
    })
    result_to_return = f"https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={curernt_code}&destinationLocationCode={destination_code}&departureDate={date}&adults={number_of_members}"
    headers = {
        'Authorization': 'Bearer ' + token_response.json()['access_token']
    }
    flight_data = requests.get(result_to_return, headers=headers)
    data = flight_data.json()        
    if len(data['data']) == 0:
        return "No direct flight available so do not try again"
    else:
        return data

# Load IATA data
def load_iata_data():
    """
    Load IATA data from a JSON file.
    """
    with open('iata.json', 'r') as file:
        return json.load(file)

# Endpoint to get airports by country
@app.route('/get_airports/<country>')
def get_airports(country):
    """
    Get a list of airports in a specified country.
    """
    iata_data = load_iata_data()
    if country in iata_data:
        airports_dict = iata_data[country][0]
        return jsonify({
            'airports': [
                {'city': city, 'code': code} 
                for city, code in airports_dict.items()
            ]
        })
    return jsonify({'airports': []})

# Endpoint to search flights
@app.route('/search_flights', methods=['POST'])
def search_flights():
    """
    Search for flights based on user input and save the data to a JSON file.
    """ 
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['origin_airport', 'destination_airport',
                         'travel_start_date', 'travel_end_date', 'number_of_members']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Initialize flight_data with default values
        flight_data = {
            'origin_airport': data.get('origin_airport'),
            'destination_airport': data.get('destination_airport'),
            'destination_location': data.get('destination_location', ''),
            'travel_start_date': data.get('travel_start_date'),
            'travel_end_date': data.get('travel_end_date'),
            'number_of_members': data.get('number_of_members'),
            'hotel_location_preference': data.get('hotel_location_preference', ''),
            'hotel_rating': data.get('hotel_rating', ''),
            'hotel_accomodation_type': data.get('hotel_accomodation_type', ''),
            'interest': data.get('interest', ''),
            'food_preferences': data.get('food_preferences', ''),
            'budget': data.get('budget', '')
        }

        # Save to JSON file
        try:
            with open("user_inputs.json", "w") as file:
                json.dump(flight_data, file)
        except IOError as e:
            app.logger.error(f"Failed to save user inputs: {str(e)}")

        # Get flight information with error handling
        try:
            origin = data['origin_airport']
            destination = data['destination_airport']
            departure_date = data['travel_start_date']
            return_date = data['travel_end_date']
            adults = int(data['number_of_members'])

            outbound_flights = get_flight_information(origin, destination, departure_date, adults)
            return_flights = get_flight_information(destination, origin, return_date, adults)

            if not outbound_flights or not return_flights:
                return jsonify({'error': 'No flights found'}), 404

            return jsonify({
                'outbound': outbound_flights,
                'return': return_flights,
                'preferences': {
                    'hotel': {
                        'location': flight_data['hotel_location_preference'],
                        'rating': flight_data['hotel_rating'],
                        'type': flight_data['hotel_accomodation_type']
                    },
                    'food': flight_data['food_preferences'],
                    'budget': flight_data['budget'],
                    'interest': flight_data['interest']
                }
            }), 200

        except ValueError as e:
            app.logger.error(f"Value error in flight search: {str(e)}")
            return jsonify({'error': 'Invalid input data'}), 400
        except Exception as e:
            app.logger.error(f"Error in flight search: {str(e)}")
            return jsonify({'error': 'Failed to search flights'}), 500

    except Exception as e:
        app.logger.error(f"General error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Endpoint to book flights
@app.route('/book_flight', methods=['POST'])
def book_flight():
    """
    Book flights based on user input and save the booking details to a JSON file.
    """
    try:
        data = request.get_json()
        outbound_flight = data['outbound_flight']
        return_flight = data['return_flight']
        
        # Extract detailed flight information
        booking_details = {
            'outbound': {
                'flight_id': outbound_flight['id'],
                'price': outbound_flight['price'],
                'departure': outbound_flight['itineraries'][0]['segments'][0]['departure'],
                'arrival': outbound_flight['itineraries'][0]['segments'][-1]['arrival'],
                'segments': outbound_flight['itineraries'][0]['segments']
            },
            'return': {
                'flight_id': return_flight['id'],
                'price': return_flight['price'],
                'departure': return_flight['itineraries'][0]['segments'][0]['departure'],
                'arrival': return_flight['itineraries'][0]['segments'][-1]['arrival'],
                'segments': return_flight['itineraries'][0]['segments']
            },
            'total_price': {
                'currency': outbound_flight['price']['currency'],
                'amount': float(outbound_flight['price']['total']) + float(return_flight['price']['total'])
            }
        }
                
        with open('flight_booking_details.json', 'w') as file:
            json.dump(booking_details, file)

        return jsonify({
            'success': True,
            'booking_details': booking_details,
            'message': 'Flights booked successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# Endpoint to render the index page with country list
@app.route('/')
def index():
    """
    Render the index page with a list of countries.
    """
    iata_data = load_iata_data()
    countries = list(iata_data.keys())
    return render_template('index.html', countries=countries)

# Endpoint to handle the CREWAI flow run
@app.route('/run', methods=['POST'])
def ai_run():
    """
    Endpoint to run the CREWAI flow and generate a trip planning report.
    """
    try:            
        run()

        # Read the generated report.md file
        try:
            with open('report.md', 'r', encoding='utf-8') as file:
                md_content = file.read()
                # Convert markdown to HTML
                html_content = markdown2.markdown(md_content)
                os.remove('flight_booking_details.json')
                os.remove('user_inputs.json')

                return jsonify({
                    'success': True,
                    'message': 'Trip planning completed successfully',
                    'report': html_content
                })
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'Report file not found'
            }), 404
            
    except Exception as e:
        app.logger.error(f"Error in AI run: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port='2021')