
import os
import html
import time
import folium
import requests
import streamlit as st
from streamlit_folium import st_folium



# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="LocalLore - Travel Guide",
    page_icon="🌍",
    layout="wide"
)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "https://locallore.onrender.com"
).rstrip("/")
API_BASE = f"{BACKEND_URL}/api"

# --------------------------------------------------
# API HELPER FUNCTIONS
# --------------------------------------------------

def get_api_data(endpoint):
    """Retrieve data from the Django REST API."""

    response = requests.get(
        f"{API_BASE}/{endpoint}/",
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    # Support Django REST Framework pagination
    if isinstance(data, dict):
        data = data.get("results", [])

    return data


def display_api_error(error):
    """Display a readable API error."""

    if isinstance(error, requests.HTTPError):
        try:
            details = error.response.json()
            st.error(f"Backend error: {details}")
        except (ValueError, AttributeError):
            st.error(f"Backend error: {error}")

    else:
        st.error(f"Connection error: {error}")


# --------------------------------------------------
# FOREST GREEN + CREAM THEME
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #F7F5ED;
    color: #263D32;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

h1, h2, h3 {
    color: #244C3A !important;
    font-family: Georgia, serif;
}

.stApp p,
.stApp label {
    color: #405347;
}

[data-testid="stSidebar"] {
    background-color: #244C3A;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #F7F5ED !important;
    border-color: #D8B77A !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #244C3A !important;
}

[data-baseweb="popover"] [role="option"] {
    background-color: #FFFFFF !important;
    color: #244C3A !important;
}

[data-baseweb="popover"] [role="option"]:hover {
    background-color: #E7EEE5 !important;
}

.stButton > button {
    background-color: #244C3A;
    color: #FFFFFF !important;
    border: 1px solid #244C3A;
    border-radius: 10px;
    padding: 0.55rem 1.2rem;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #35664D;
    color: #FFFFFF !important;
    border-color: #35664D;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background-color: #FFFFFF !important;
    color: #244C3A !important;
    border-radius: 9px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
}

hr {
    border-color: #D9DFD5;
}

.stButton > button {
    color: #1B4332 !important;
    background-color: #F5F1E8 !important;
    border: 1px solid #1B4332 !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    color: #FFFFFF !important;
    background-color: #1B4332 !important;
}

.stButton > button p {
    color: inherit !important;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("🌍 Welcome to LocalLore")
st.subheader("Discover places through local guides!")

st.write(
    "Explore local attractions, connect with experienced guides, "
    "and plan memorable travel experiences."
)


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("LocalLore Menu")

menu = st.sidebar.selectbox(
    "Choose an option",
    [
        "Home",
        "Explore Attractions",
        "Find Local Guides",
        "Book a Guide",
        "AI Itinerary Planner",
        "Explore Map",
        "About Us"
    ]
)


# --------------------------------------------------
# HOME
# --------------------------------------------------

if menu == "Home":

    st.header("Discover Your Next Destination")

    st.markdown("""
    <div style="
        background-color: #E7EEE5;
        color: #244C3A;
        padding: 18px 22px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 500;
        border-left: 5px solid #244C3A;
    ">
        Your local travel experience starts here!
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# EXPLORE ATTRACTIONS
# --------------------------------------------------


elif menu == "Explore Attractions":

    st.header("Explore Attractions")

    destination = st.text_input(
        "Enter your destination",
        key="attraction_destination"
    )

    if st.button("Search Attractions"):

        if destination.strip():

            try:
                with st.spinner("Finding attractions..."):

                    attractions = get_api_data("attractions")

                matching_attractions = [
                    attraction for attraction in attractions
                    if destination.strip().lower()
                    in attraction.get("location", "").lower()
                ]

                if matching_attractions:

                    st.success(
                        f"Found {len(matching_attractions)} attractions!"
                    )

                    for attraction in matching_attractions:

                        st.subheader(attraction["name"])

                        st.write(attraction["description"])

                        st.write(
                            f"📍 Location: {attraction['location']}"
                        )

                        opening = (
                            attraction.get("opening_time")
                            or "Check locally"
                        )

                        closing = (
                            attraction.get("closing_time")
                            or "Check locally"
                        )

                        st.write(
                            f"Opening: {opening} | "
                            f"Closing: {closing}"
                        )

                        st.divider()

                else:
                    st.warning(
                        "No attractions found for this destination."
                    )

            except requests.RequestException as error:
                display_api_error(error)

        else:
            st.warning("Please enter a destination.")


# --------------------------------------------------
# FIND LOCAL GUIDES
# --------------------------------------------------

elif menu == "Find Local Guides":

    st.header("Find Local Guides")

    st.write("Discover experienced local tour guides.")

    try:
        with st.spinner("Finding local guides..."):

            guides = get_api_data("guides")

        available_guides = [
            guide for guide in guides
            if guide.get("available") is True
        ]

        if available_guides:

            for guide in available_guides:

                with st.container(border=True):

                    st.subheader(guide["name"])

                    st.write(
                        f"📍 Location: {guide['location']}"
                    )

                    st.write(
                        f"🗣️ Languages: {guide['language']}"
                    )

                    st.write(
                        f"⭐ Experience: {guide['experience']} years"
                    )

                    st.write(
                        f"About: {guide['description']}"
                    )

                    st.write(
                        "Maximum group size: "
                        f"{guide['max_group_size']}"
                    )

        else:
            st.info("No available guides found.")

    except requests.RequestException as error:
        display_api_error(error)


# --------------------------------------------------
# BOOK A GUIDE
# --------------------------------------------------

elif menu == "Book a Guide":

    st.header("Book Your Local Guide")

    try:
        guides = get_api_data("guides")

        available_guides = [
            guide for guide in guides
            if guide.get("available") is True
        ]

        if available_guides:

            guide = st.selectbox(
                "Select Your Guide",
                available_guides,
                format_func=lambda g: (
                    f"{g['name']} - {g['location']}"
                ),
                key="selected_guide"
            )

            name = st.text_input(
                "Your Name",
                key="tourist_name"
            )

            date = st.date_input(
                "Travel Date",
                key="booking_date"
            )

            group_size = st.number_input(
                "Number of Tourists",
                min_value=1,
                max_value=max(1, int(guide["max_group_size"])),
                value=1
            )

            if st.button("Submit Booking"):

                if not name.strip():

                    st.warning("Please enter your name.")

                else:

                    booking_data = {
                        "tourist_name": name.strip(),
                        "guide": guide["id"],
                        "booking_date": date.isoformat(),
                        "group_size": int(group_size)
                    }

                    try:
                        with st.spinner("Submitting your booking..."):

                            response = requests.post(
                                f"{API_BASE}/bookings/",
                                json=booking_data,
                                timeout=30
                            )

                            response.raise_for_status()

                        st.success("Booking saved successfully!")

                        st.write("Booking Status: Pending")

                    except requests.RequestException as error:
                        display_api_error(error)

        else:
            st.warning("No available guides found.")

    except requests.RequestException as error:
        display_api_error(error)


# --------------------------------------------------
# AI ITINERARY PLANNER
# --------------------------------------------------

elif menu == "AI Itinerary Planner":

    st.header("AI Itinerary Planner")

    st.write(
        "Create a personalised itinerary using LocalLore AI."
    )

    destination = st.text_input(
        "Enter destination",
        key="itinerary_destination"
    )

    days = st.number_input(
        "Number of days",
        min_value=1,
        max_value=7,
        value=1
    )

    preference = st.selectbox(
        "Travel preference",
        ["heritage", "adventure", "nature", "general"]
    )

    if st.button("Generate Itinerary"):

        if destination.strip():

            with st.spinner("Generating your itinerary..."):

                try:

                    response = requests.post(
                        f"{API_BASE}/itinerary/",
                        json={
                            "destination": destination.strip(),
                            "days": int(days),
                            "preference": preference
                        },
                        timeout=90
                    )

                    response.raise_for_status()

                    result = response.json()

                    st.success("Your itinerary is ready!")

                    st.markdown(result["itinerary"])

                except requests.RequestException as error:
                    display_api_error(error)

                except (ValueError, KeyError):
                    st.error(
                        "The backend returned an unexpected response."
                    )

        else:
            st.warning("Please enter a destination.")


# --------------------------------------------------
# EXPLORE MAP
# --------------------------------------------------

elif menu == "Explore Map":

    st.header("Explore Attractions on Map")

    st.write(
        "Discover attractions, view their locations "
        "and explore driving routes."
    )

    destination = st.text_input(
        "Enter destination for map",
        key="map_destination"
    )

    if "show_map" not in st.session_state:
        st.session_state.show_map = False

    if st.button("Show Map"):
        st.session_state.show_map = True

    if st.session_state.show_map:

        if destination.strip():

            try:

                with st.spinner("Loading attraction locations..."):

                    attractions = get_api_data("attractions")

                selected_city = destination.strip().lower()

                matching_attractions = [
                    attraction for attraction in attractions
                    if selected_city in
                    attraction.get("location", "").strip().lower()
                ]

                if not matching_attractions:

                    st.warning(
                        f"No attractions found for {destination}."
                    )

                else:

                    coordinates = []

                    if "coordinate_cache_v2" not in st.session_state:
                        st.session_state.coordinate_cache_v2 = {}

                    cache = st.session_state.coordinate_cache_v2

                    for attraction in matching_attractions:

                        name = attraction["name"]
                        city = attraction["location"]

                        latitude = attraction.get("latitude")
                        longitude = attraction.get("longitude")

                        if latitude is not None and longitude is not None:

                            coordinates.append({
                                "name": name,
                                "description": attraction["description"],
                                "lat": float(latitude),
                                "lon": float(longitude)
                            })

                            continue

                        # New cache version avoids old incorrect Delhi coordinates
                        cache_key = f"v2_{name}_{city}".lower()

                        if cache_key in cache:

                            result = cache[cache_key]

                            if result:
                                coordinates.append({
                                    "name": name,
                                    "description": attraction["description"],
                                    "lat": result[0],
                                    "lon": result[1]
                                })

                            continue

                        search_name = name
                        
                        try:

                            # Respect Nominatim's public usage rate limit
                            time.sleep(1.1)

                            geo_response = requests.get(
                                "https://nominatim.openstreetmap.org/search",
                                params={
                                    "q": f"{search_name}, {city}, India",
                                    "format": "json",
                                    "limit": 1,
                                    "countrycodes": "in"
                                },
                                headers={
                                    "User-Agent": "LocalLoreTravelApp/1.0"
                                },
                                timeout=20
                            )

                            geo_response.raise_for_status()

                            geo_data = geo_response.json()

                            if geo_data:

                                lat = float(geo_data[0]["lat"])
                                lon = float(geo_data[0]["lon"])

                                cache[cache_key] = (lat, lon)

                                coordinates.append({
                                    "name": name,
                                    "description": attraction["description"],
                                    "lat": lat,
                                    "lon": lon
                                })

                            else:

                                st.warning(
                                    f"Could not locate {name} in {city}."
                                )

                        except requests.RequestException as error:

                            st.warning(
                                f"Location lookup failed for {name}: {error}"
                        )

                    if coordinates:

                        center = [
                            sum(p["lat"] for p in coordinates)
                            / len(coordinates),
                            sum(p["lon"] for p in coordinates)
                            / len(coordinates)
                        ]

                        travel_map = folium.Map(
                            location=center,
                            zoom_start=12
                        )

                        for place in coordinates:

                            popup_name = html.escape(place["name"])

                            popup_description = html.escape(
                                place["description"]
                            )

                            folium.Marker(
                                location=[
                                    place["lat"],
                                    place["lon"]
                                ],
                                popup=folium.Popup(
                                    f"<b>{popup_name}</b><br>"
                                    f"{popup_description}",
                                    max_width=300
                                ),
                                tooltip=place["name"],
                                icon=folium.Icon(
                                    color="green",
                                    icon="info-sign"
                                )
                            ).add_to(travel_map)

                        if len(coordinates) >= 2:

                            route_coordinates = ";".join(
                                f"{p['lon']},{p['lat']}"
                                for p in coordinates
                            )

                            route_url = (
                                "https://router.project-osrm.org/"
                                f"route/v1/driving/{route_coordinates}"
                            )

                            try:

                                route_response = requests.get(
                                    route_url,
                                    params={
                                        "overview": "full",
                                        "geometries": "geojson"
                                    },
                                    timeout=30
                                )

                                route_response.raise_for_status()

                                route_data = route_response.json()

                                if (
                                    route_data.get("code") == "Ok"
                                    and route_data.get("routes")
                                ):

                                    route = route_data["routes"][0]

                                    folium.GeoJson(
                                        route["geometry"],
                                        name="Driving Route",
                                        style_function=lambda feature: {
                                            "color": "#244C3A",
                                            "weight": 5
                                        }
                                    ).add_to(travel_map)

                                    st.success(
                                        "Driving route generated!"
                                    )

                                else:

                                    st.info(
                                        "Driving route unavailable. "
                                        "Showing attraction markers instead."
                                    )

                            except requests.RequestException:

                                st.info(
                                    "Route unavailable. "
                                    "Attraction markers are still displayed."
                                )

                        folium.LayerControl().add_to(travel_map)

                        st_folium(
                            travel_map,
                            width=900,
                            height=600
                        )

                        st.success(
                            f"Located {len(coordinates)} of "
                            f"{len(matching_attractions)} attractions "
                            f"in {destination}."
                        )

                        st.caption(
                            "Location data © OpenStreetMap contributors. "
                            "Driving routes © OSRM."
                        )

                    else:

                        st.warning(
                            f"No attraction coordinates could be found "
                            f"for {destination}."
                        )

            except requests.RequestException as error:

                display_api_error(error)

        else:

            st.warning("Please enter a destination.")


# --------------------------------------------------
# ABOUT US
# --------------------------------------------------

elif menu == "About Us":

    st.header("About LocalLore")

    st.write(
        "LocalLore connects tourists with local guides "
        "and helps them discover interesting destinations."
    )
