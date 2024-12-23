import streamlit as st
import pandas as pd
import altair as alt
import asyncio
from datetime import datetime

# Initialize session state to hold athletes
if "athletes" not in st.session_state:
    st.session_state.athletes = []


# Function to add athlete to the list
def add_athlete():
    athlete = st.session_state.athlete_input.strip()
    if athlete and athlete not in st.session_state.athletes:
        st.session_state.athletes.append(athlete)
        st.session_state.athlete_input = ""  # Clear input after adding


# Layout with two columns
col1, col2 = st.columns([3, 1])  # Adjust the column widths as needed

with col1:
    # Display entered athletes as a numbered list
    st.write("### Entered Athletes:")
    for i, athlete in enumerate(st.session_state.athletes, start=1):
        st.write(f"{i}. {athlete}")

    # Input field for entering an athlete
    st.text_input(
        "Enter an athlete's name:", key="athlete_input", on_change=add_athlete
    )

    # Show total entered athletes
    total_athletes = len(st.session_state.athletes)
    st.write(f"Total athletes entered: {total_athletes}")

    # Validate input
    if total_athletes == 0:
        st.write("Please enter at least one athlete")
    else:
        # Import list of athletes from all_players.csv
        all_players = pd.read_csv("./data/all_players.csv", index_col="id")

        # Drop api_id column
        all_players.drop(columns=["api_id"], inplace=True)

        # Get the athletes that are in the list
        athletes_in_list = all_players[
            all_players["full_name"].isin(st.session_state.athletes)
        ]

        # Calculate percentage of verified athletes
        pct_verified = round((len(athletes_in_list) / total_athletes) * 100, 2)
        st.write(
            f"We could verify {len(athletes_in_list)}, or {pct_verified}% athletes in the list"
        )

        # Print the athletes that are in the list
        st.write("Verified athletes:")
        st.write(athletes_in_list)

        # Identify unverified athletes
        unverified_athletes = [
            athlete
            for athlete in st.session_state.athletes
            if athlete not in athletes_in_list["full_name"].values
        ]

        # Add unverified athletes to a dataframe with a league of "Unverified"
        unverified_df = pd.DataFrame(
            {"full_name": unverified_athletes, "league": "Unverified"}
        )

        # Combine verified and unverified athletes
        named_athletes = pd.concat([athletes_in_list, unverified_df], ignore_index=True)

        # Print the athletes that are not in the list
        st.write("Unverified athletes:")
        st.write(unverified_athletes)

        # Get league counts and sort by counts in descending order
        league_counts = named_athletes["league"].value_counts().reset_index()
        league_counts.columns = ["league", "count"]
        league_counts.sort_values(
            by="count", ascending=False, inplace=True
        )  # Sort by count

        # Define colors for each league
        league_colors = {
            "NFL": "#0000FF",  # blue
            "NBA": "#FF0000",  # red
            "MLB": "#008000",  # green
            "WNBA": "#800080",  # purple
            "Unverified": "#808080",  # gray
        }

        # Map colors to league_counts
        league_counts["color"] = league_counts["league"].map(league_colors)

        # Create a larger bar chart with the league counts
        bar_chart = (
            alt.Chart(league_counts)
            .mark_bar()
            .encode(
                x=alt.X("count:Q", title="Count"),  # X-axis is counts
                y=alt.Y(
                    "league:N",
                    title="League",
                    sort="-x",
                ),  # Y-axis is leagues sorted by count
                color=alt.Color("color", scale=None),  # Keep color for bars
                tooltip=[
                    alt.Tooltip("league:N", title="League:"),
                    alt.Tooltip("count:Q", title="Count:"),
                ],
            )
            .properties(
                title="Athlete Counts by League",
                width=800,  # Set the width of the chart
                height=400,  # Set the height of the chart
            )
        )

        st.altair_chart(bar_chart)

with col2:
    st.markdown(
        """
    <style>
    .time {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #ec5953 !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Create timer options
    time_limit = st.slider("Set Timer (minutes):", 0, 120, 60)

    # Add a start button
    if st.button("Start Timer"):
        current_time = datetime.now()

        # Get only the hour and minute HH:MM with no date
        time_display = current_time.strftime("%H:%M")

        st.write(f"Timer started at: {time_display}")
        test = st.empty()

        end_time = current_time + pd.Timedelta(minutes=time_limit)

        async def watch(test):
            while True:
                test.markdown(
                    f"""
                    <p class="time">
                        Time remaining: {str(end_time - datetime.now()).split('.')[0]}
                    </p>
                    """,
                    unsafe_allow_html=True,
                )
                r = await asyncio.sleep(1)

        asyncio.run(watch(test))
