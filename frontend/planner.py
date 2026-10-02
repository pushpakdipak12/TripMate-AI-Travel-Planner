import streamlit as st

import api_client
import components as ui


TABS = [
    ("full_trip", "Full trip",
     "From [city] to [city], from [date], [days] days, [people] people, budget ₹[amount], [interests]",
     "Pune to Varanasi from 10 October, 4 days, 2 people, budget ₹40,000, temples and street food",
     "Transport, stay, weather, budget and a day-by-day plan for your trip."),
    ("transport", "Transport",
     "From [city] to [city] on [date], [people] people",
     "Mumbai to Jaipur on 15 December, 3 people",
     "Compare trains, buses, cabs, self-drive and flights with estimated fares."),
    ("hotels", "Hotels",
     "Hotels in [city] from [date], [nights] nights, [people] people, cheap / mid-range / luxury",
     "Hotels in Manali from 12 October, 3 nights, 2 people, cheap",
     "Hotels that match your style, with prices for your whole stay."),
    ("weather", "Weather",
     "Weather in [city] from [date], [days] days",
     "Weather in Munnar from 8 October, 5 days",
     "Daily forecast with temperature and chance of rain."),
    ("activities", "Places to visit",
     "Things to do in [city], [days] days, [interests]",
     "Things to do in Udaipur, 2 days, palaces and lakes",
     "Famous sights and local favourites for your destination."),
    ("budget", "Budget",
     "[days] days in [city] from [city], from [date], [people] people, budget ₹[amount]",
     "3 days in Rishikesh from Delhi, from 20 October, 2 people, budget ₹15,000",
     "A full cost breakdown and ways to save if you are over budget."),
]


@st.cache_data(ttl=30, show_spinner=False)
def backend_status():
    return api_client.health()


def run_plan(mode: str, query: str):
    with st.spinner("Planning your trip. The first search for a city can take up to a minute."):
        try:
            st.session_state[f"result_{mode}"] = api_client.plan(mode, query)
        except api_client.ApiError as e:
            ui.callout(str(e), "warn")


def run_replan(mode: str, result: dict, option: str):
    with st.spinner(f"Updating your plan for {option}"):
        try:
            st.session_state[f"result_{mode}"] = api_client.replan(result["thread_id"], option)
        except api_client.ApiError as e:
            ui.callout(str(e), "warn")
            return
    st.rerun()


def transport_picker(mode: str, result: dict):
    options = (result.get("transport") or {}).get("options", [])
    if not options:
        return
    names = [o["name"] for o in options]
    current = ui.current_transport(result)
    recommended = (result.get("recommended_transport") or {}).get("option_name")
    choice = st.selectbox(
        "Change how you travel",
        names,
        index=names.index(current) if current in names else 0,
        format_func=lambda n: f"{n}  (recommended)" if n == recommended else n,
        key=f"pick_{mode}_{result['thread_id']}",
    )
    if choice != current:
        run_replan(mode, result, choice)


def show_full_trip(mode: str, result: dict):
    ui.summary_strip(result)

    left, right = st.columns([3, 2], gap="large")
    with left:
        ui.section("How to get there")
        ui.transport_table(result)
        transport_picker(mode, result)
        ui.recommendation(result)
    with right:
        ui.section("Budget")
        ui.budget_panel(result.get("budget"))

    ui.section("Weather during your trip")
    ui.weather_strip(result.get("weather"))

    left, right = st.columns([3, 2], gap="large")
    with left:
        ui.section("Where to stay")
        ui.hotels_table(result.get("hotels"), result.get("chosen_hotel"))
    with right:
        ui.section("Places to visit")
        ui.places_chips(result.get("activities"))

    left, right = st.columns([3, 2], gap="large")
    with left:
        ui.section("Day-by-day plan")
        ui.itinerary_timeline(result.get("itinerary"), result["trip"])
    with right:
        ui.section("Notes")
        ui.trip_notes(result)


def show_budget(mode: str, result: dict):
    left, right = st.columns([3, 2], gap="large")
    with left:
        ui.section("How to get there")
        ui.transport_table(result)
        transport_picker(mode, result)
        ui.section("Where to stay")
        ui.hotels_table(result.get("hotels"), result.get("chosen_hotel"))
    with right:
        ui.section("Cost breakdown")
        ui.budget_panel(result.get("budget"))


def show_result(mode: str, result: dict):
    if result.get("needs_clarification"):
        ui.callout(result["question"])
        return
    ui.ticket(mode, result)

    if mode == "full_trip":
        show_full_trip(mode, result)
    elif mode == "budget":
        show_budget(mode, result)
    elif mode == "transport":
        ui.section("Your options")
        ui.transport_table(result)
        ui.recommendation(result)
    elif mode == "hotels":
        ui.section("Hotels")
        ui.hotels_table(result.get("hotels"), result.get("chosen_hotel"))
    elif mode == "weather":
        ui.section("Forecast")
        ui.weather_strip(result.get("weather"))
    elif mode == "activities":
        ui.section("Places to visit")
        ui.places_chips(result.get("activities"))

    for warning in (result.get("warnings") or []) if mode != "full_trip" else []:
        ui.callout(warning, "warn")


def planner_page():
    ui.brand(backend_status())
    tabs = st.tabs([tab[1] for tab in TABS])

    for tab, (mode, label, query_format, example, empty_text) in zip(tabs, TABS):
        with tab:
            ui.hint(query_format, example)
            box, button = st.columns([6, 1], vertical_alignment="bottom")
            with box:
                query = st.text_input("Your trip", placeholder=query_format, key=f"query_{mode}",
                                      label_visibility="collapsed")
            with button:
                clicked = st.button("Plan trip", key=f"button_{mode}", type="primary", use_container_width=True)
            if clicked:
                if query.strip():
                    run_plan(mode, query)
                else:
                    ui.callout("Type your trip in the box first, following the format above.", "warn")

            result = st.session_state.get(f"result_{mode}")
            if result:
                show_result(mode, result)
            else:
                ui.empty_state(empty_text)

    ui.footer()
