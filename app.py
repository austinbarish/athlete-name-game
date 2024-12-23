# Imports
import streamlit as st
import pandas as pd
import altair as alt
import time
from datetime import datetime
import matplotlib.pyplot as plt

# Initialize session state to hold athletes
if "athletes" not in st.session_state:
    st.session_state.athletes = []

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

if "end_time" not in st.session_state:
    st.session_state.end_time = None


# Function to add athlete to the list
def add_athlete():
    athlete = st.session_state.athlete_input.strip()
    if athlete and athlete not in st.session_state.athletes:
        st.session_state.athletes.append(athlete)
        st.session_state.athlete_input = ""  # Clear input after adding


# Function to start the timer
def start_timer():
    st.session_state.timer_running = True
    st.session_state.end_time = datetime.now() + pd.Timedelta(
        minutes=st.session_state.time_limit
    )


# Function to create a summary image
def create_summary(time_limit, total_count, league_counts, output_path="summary.png"):
    if not league_counts.empty:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        league_colors = {
            "NFL": "#0000FF",
            "NBA": "#FF0000",
            "MLB": "#008000",
            "WNBA": "#800080",
            "Unverified": "#808080",
        }

        # Top section: Display the time limit and total count
        ax.text(
            0.5,
            1.2,
            f"Time Limit: {time_limit} minutes",
            fontsize=16,
            ha="center",
            transform=ax.transAxes,
            color="blue",
        )
        ax.text(
            0.5,
            1.1,
            f"Total Athletes: {total_count}",
            fontsize=16,
            ha="center",
            transform=ax.transAxes,
            color="green",
        )

        # Bar chart for league counts
        league_counts["color"] = league_counts["league"].map(league_colors)
        ax.barh(
            league_counts["league"],
            league_counts["count"],
            color=league_counts["color"],
        )
        ax.set_xlabel("Count", fontsize=14)
        ax.set_title("Athlete Counts by League", fontsize=16)

        # Make x-axis ticks integers
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

        # Annotate the bars with count values
        for i, value in enumerate(league_counts["count"]):
            ax.text(value + 0.5, i, str(value), va="center", fontsize=12)

        # Adjust layout
        plt.tight_layout()

        # Save the image
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()
    else:
        st.write("No data to create summary")


# Layout with two columns
col1, col2 = st.columns([3, 1])

# Main col
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

    # Display verified and unverified athletes
    if total_athletes > 0:
        # Import list of athletes from all_players.csv
        all_players = pd.read_csv("./data/all_players.csv", index_col="id")
        all_players.drop(columns=["api_id"], inplace=True)

        # Remove duplicates from all_players
        all_players.drop_duplicates(subset="full_name", keep="first", inplace=True)

        # Verified and unverified athletes logic
        athletes_in_list = all_players[
            all_players["full_name"]
            .str.lower()
            .isin([athlete.lower() for athlete in st.session_state.athletes])
        ]
        pct_verified = round((len(athletes_in_list) / total_athletes) * 100, 2)
        st.write(
            f"We could verify {len(athletes_in_list)}, or {pct_verified}% athletes in the list"
        )
        st.write("Verified athletes:")
        st.write(athletes_in_list)

        # Create a DataFrame of unverified athletes
        unverified_athletes = [
            athlete
            for athlete in st.session_state.athletes
            if athlete.lower() not in athletes_in_list["full_name"].str.lower().values
        ]
        unverified_df = pd.DataFrame(
            {"full_name": unverified_athletes, "league": "Unverified"}
        )
        named_athletes = pd.concat([athletes_in_list, unverified_df], ignore_index=True)
        st.write("Unverified athletes:")
        st.write(
            pd.DataFrame(
                unverified_athletes,
                columns=["Guess"],
                index=range(1, len(unverified_athletes) + 1),
            )
        )

        # Create a bar chart of athlete counts by league
        league_counts = named_athletes["league"].value_counts().reset_index()
        league_counts.columns = ["league", "count"]
        league_colors = {
            "NFL": "#0000FF",
            "NBA": "#FF0000",
            "MLB": "#008000",
            "WNBA": "#800080",
            "Unverified": "#808080",
        }
        league_counts["color"] = league_counts["league"].map(league_colors)

        # Create the bar chart
        bar_chart = (
            alt.Chart(league_counts)
            .mark_bar()
            .encode(
                x=alt.X(
                    "count:Q",
                    title="Count",
                    axis=alt.Axis(grid=False, labelAngle=0, tickMinStep=1, tickCount=5),
                ),
                y=alt.Y("league:N", title="League", sort="-x"),
                color=alt.Color("color", scale=None),
                tooltip=[
                    alt.Tooltip("league:N", title="League:"),
                    alt.Tooltip("count:N", title="Count:"),
                ],
            )
            .properties(title="Athlete Counts by League", width=800, height=400)
        )
        st.altair_chart(bar_chart)

with col2:
    # Styling for the timer
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

    # Timer logic
    st.session_state.time_limit = st.slider("Set Timer (minutes):", 0, 120, 60)
    if st.button("Start Timer"):
        start_timer()

    # Where the Timer goes
    timer_placeholder = st.empty()
    if st.session_state.timer_running:
        while datetime.now() < st.session_state.end_time:
            # Calculate time remaining
            remaining_time = str(st.session_state.end_time - datetime.now()).split(".")[
                0
            ]

            # Update the timer
            timer_placeholder.markdown(
                f"""
                <p class="time">
                    Time remaining: {remaining_time}
                </p>
                """,
                unsafe_allow_html=True,
            )
            time.sleep(1)
        st.session_state.timer_running = False
        timer_placeholder.markdown(
            "<p class='time'>Time's up!</p>", unsafe_allow_html=True
        )

        # Create final stats png with button to download
        create_summary(st.session_state.time_limit, total_athletes, league_counts)
        with open("summary.png", "rb") as file:
            btn = st.download_button(
                label="Download Summary",
                data=file,
                file_name="summary.png",
                mime="image/png",
            )
