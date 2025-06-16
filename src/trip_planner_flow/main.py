import json
import os
from pydantic import BaseModel
import time
from .crews.place_selector_crew.place_crew import PlaceCrew
from .crews.trip_planner_crew.planner_crew import PlannerCrew
from crewai.flow.flow import Flow, listen, start

# This class defines the state of the trip planning process.
class TripState(BaseModel):

    origin_airport: str = "" 
    destination_airport: str = ""
    destination_location: str = ""
    travel_start_Date: str = ""
    travel_end_Date: str = ""
    hotel_location_preference: str = ""
    hotel_rating: str = ""
    hotel_accomodation_type: str = ""
    interest: str = ""
    number_of_members: str = ""
    food_preferences: str = ""
    budget: str = ""
    place_selection_op: str = ""
    place_selection_modified_op: str = ""
    going_flight: str = ""
    return_flight: str = ""

# This class defines the flow of the trip planning process.
class TripFlow(Flow[TripState]):
    @start()
    def taking_user_inputs(self):
        """
        This method initializes the trip planning flow by reading user inputs from a JSON file and flight booking details.
        """
        with open("user_inputs.json", "r") as file:
            data = json.load(file)

        with open("flight_booking_details.json", "r") as file:
            flight_data = json.load(file)
            self.state.going_flight = str(flight_data['outbound'])
            self.state.return_flight = str(flight_data['return'])

        self.state.origin_airport = data['origin_airport']
        self.state.destination_airport = data['destination_airport']
        self.state.destination_location = data['destination_location']
        self.state.travel_start_Date = data['travel_start_date']
        self.state.travel_end_Date = data['travel_end_date']
        self.state.hotel_location_preference = data['hotel_location_preference']
        self.state.hotel_rating = data['hotel_rating']
        self.state.hotel_accomodation_type = data['hotel_accomodation_type']
        self.state.interest = data['interest']
        self.state.number_of_members = int(data['number_of_members'])
        self.state.food_preferences = data['food_preferences']
        self.state.budget = data['budget']
        
    # This method listens for the taking_user_inputs event and generates a list of places based on the user inputs using the AI Agent.    
    @listen(taking_user_inputs)
    def generate_place_list(self):
        """
        This method generates a list of places based on user inputs such as destination location, interests, food preferences, and travel dates.
        It uses the PlaceCrew to kick off the place selection process and stores the result in the state.
        """
        result = (
            PlaceCrew()
            .crew()
            .kickoff(inputs={
        "destination_location" : self.state.destination_location,
        "interest" : self.state.interest,
        "food_preferences" : self.state.food_preferences,
        "travel_end_Date" : self.state.travel_end_Date,
        "travel_start_Date" : self.state.travel_start_Date,
    }))
        self.state.place_selection_op = result.raw
        return result.raw
    
    # This method listens for the generate_place_list event and modifies the place list based on user input.
    @listen(generate_place_list)
    def modify_place_list(self):
        """
        This method allows the user to modify the generated list of places by opening a web page for user input.
        It waits for the user to complete the modification and then updates the state with the modified content.
        """
        try:
            original_content = self.state.place_selection_op
            
            # Store initial text for modification
            with open('temp_places.txt', 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Open the modification page in default browser
            import webbrowser
            webbrowser.open('http://localhost:2021/modify_place_list')
            
            # Wait for user modification
            while True:
                if os.path.exists('modification_complete.flag'):
                    # Read the modified content
                    with open('temp_places.txt', 'r', encoding='utf-8') as f:
                        modified_content = f.read()
                        self.state.place_selection_modified_op = modified_content
                    
                    # Clean up temporary files
                    os.remove('modification_complete.flag')
                    os.remove('temp_places.txt')
                    return modified_content
                time.sleep(1)
                
        except Exception as e:
            return self.state.place_selection_modified_op
    
    # This method listens for the modify_place_list event and saves the trip report using the AI Agent.
    @listen(modify_place_list)
    def save_report(self):
        """
        This method saves the trip report by using the PlannerCrew to kick off the trip planning process with the user inputs and modified place selection.
        It returns the result of the trip planning process.
        """
        result = (
            PlannerCrew()
            .crew()
            .kickoff(inputs={
                "destination_location": self.state.destination_location,
                "destination_airport": self.state.destination_airport,
                "interest": self.state.interest,
                "travel_start_Date": self.state.travel_start_Date,
                "travel_end_Date": self.state.travel_end_Date,
                "number_of_members": self.state.number_of_members,
                "budget": self.state.budget,
                "food_preferences": self.state.food_preferences,
                "hotel_location_preference": self.state.hotel_location_preference,
                "hotel_rating": self.state.hotel_rating,
                "hotel_accomodation_type": self.state.hotel_accomodation_type,
                "place_selection_modified_op": self.state.place_selection_modified_op,  
                "going_flight": self.state.going_flight,
                "return_flight": self.state.return_flight,
            }))
        return result.raw

# Run the trip planning flow
def run():
    """
    This function initializes and starts the TripFlow.
    It handles any exceptions that may occur during the flow execution.
    """
    try:
        trip_flow = TripFlow()
        trip_flow.kickoff()
        return True
    except Exception as e:
        raise e
