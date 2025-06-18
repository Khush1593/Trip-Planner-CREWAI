# ✈️ Smart Travel Planner with CrewAI

## 🧠 Overview

This project is a multi-agent travel planning system powered by CrewAI.  
It uses AI agents to generate personalized, end-to-end travel plans based on user preferences, integrating real-time flight data using Amadeus APIs, and leveraging Google Search and Google Maps tools (via `SERPER_API_KEY`) for place insights.

The system is built using two crews, each with a dedicated agent responsible for a specific task in the pipeline:

- **Crew 1:** Selects travel destinations based on user interests and gathers information about the selected places.
- **Crew 2:** Creates a detailed itinerary based on the destination, flight data, budget, accommodation preferences, food choices, and more.

---

## 📌 Features

- ✅ Selects destinations based on user interests (e.g., beaches, mountains, history, nightlife)
- ✅ Retrieves key travel details and attractions via Google Search and Google Maps
- ✅ Integrates with Amadeus Flight APIs to fetch real-time flight data
- ✅ Builds a complete trip itinerary considering:
  - Budget
  - Group size
  - Travel dates
  - Origin & destination airports
  - Accommodation type & preference
  - Food preferences
- ✅ Modular & extensible architecture using CrewAI’s multi-agent workflow

![Work flow](images/Crewai%20FlowChart.jpg)

---

## 🧩 Crews and Agents

### 🧭 Crew 1: Destination Selection Crew

**Agent:** DestinationSelectorAgent

**Responsibilities:**
- Analyze user interests (nature, adventure, history, etc.)
- Suggest suitable destinations
- Fetch detailed information about each place using:
  - Google Search Tool
  - Google Maps Tool (`SERPER_API_KEY`)
- Pass data to Crew 2

---

### 📅 Crew 2: Itinerary Planning Crew

**Agent:** TripPlannerAgent

**Responsibilities:**
- Accept destination info from Crew 1
- Integrate with Amadeus API for flights
- Build itinerary (day-wise)
- Consider user preferences:
  - Travel dates
  - Group size
  - Budget
  - Accommodation
  - Food
  - Activities

---

## ⚙️ Tools & APIs Used

### 🧰 Agent Tools

- **Google Search Tool** – for researching top places, activities, travel tips
- **Google Maps Tool** – for geo-locating destinations and activities (via `SERPER_API_KEY`)

### 🌐 External APIs

- **Amadeus API** – to fetch live flight data (requires API key)
  - Supports search for:
    - Cheapest flights
    - Specific dates and routes
    - Pricing and availability

---

## 📥 Input Parameters

The user must provide the following input data:

| Parameter               | Description                                  |
|-------------------------|----------------------------------------------|
| `origin_airport`        | IATA code of the departure airport           |
| `destination_airport`   | IATA code of the destination airport         |
| `travel_dates`          | Start and end dates of the trip              |
| `num_members`           | Number of people traveling                   |
| `budget_per_person`     | Budget for each person                       |
| `hotel_preferences`     | Type of hotel (budget, luxury, family, etc.) |
| `food_preferences`      | Veg, Non-Veg, Vegan, etc.                    |
| `interests`             | Nature, adventure, relaxation, culture, etc. |

---

## 🚀 Output

The final output is a personalized, detailed travel itinerary, which includes:

- Suggested places to visit
- Day-wise plan and activity breakdown
- Flight options
- Hotel recommendations (based on preferences)
- Food options (restaurants or local suggestions)
- Estimated total cost per person
- Travel tips

---

## ⚡️ LLM Setup Requirements

This project requires a local LLM setup using [Ollama](https://ollama.com/) with the **Llama 3.2** model.  
Alternatively, you can use cloud-based LLMs (such as OpenAI or Azure OpenAI) if preferred.

**To use Ollama locally:**
1. [Install Ollama](https://ollama.com/download) on your machine.
2. Pull the Llama 3.2 model:
   ```sh
   ollama pull llama3:latest
   ```
3. Ensure Ollama is running before starting the project.

**To use a cloud-based LLM:**  
Provide the appropriate API keys in your `.env` file.

---

## 🔑 Environment Variables

Create a `.env` file in your project root and add the following keys:

```env
OPENAI_API_KEY="Fake API required for OLLAMA"  # Required for Ollama or your cloud LLM
SERPER_API_KEY=your_serper_api_key
CLIENT_ID=your_amadeus_client_id
CLIENT_SECRET=your_amadeus_client_secret
```

> **Note:**  
> - If using Ollama, `OPENAI_API_KEY` can be any fake value (required for compatibility).
> - For cloud LLMs, use your actual API key.
> - All keys are required for full

---

## 📌 Future Enhancements

- **Enhancing the UI:**  
  Improve the user interface for a more interactive and user-friendly experience.

- **Enhancing Agent Prompts:**  
  Refine and optimize the prompts used by agents to generate more accurate and relevant travel plans.

- **Adding New Tools:**  
  Integrate additional tools and APIs that provide more accurate and up-to-date results for hotel recommendations and other.