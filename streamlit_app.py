import streamlit as st
from espn_api.football import League
from api_client import fetch_league_data
from visualization import generate_opponent_underperformance_chart, plot_pythagorean_expectation_luck, save_luck_indices_to_file_v3, \
create_scheduling_luck_dataframe, create_scatterplot_luck_figure
from analysis import calculate_pythagorean_expectation_luck, calculate_scatterplot_luck, get_luck_index_v3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEBUG_MODE = False
LEAGUE_ID = os.getenv('LEAGUE_ID')
SWID = os.getenv('SWID')
ESPN_S2 = os.getenv('ESPN_S2')

# Custom CSS for fixed width buttons
st.markdown("""
    <style>
    .stButton button {
        width: 80%;
        max-width: 300px;
        display: block;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

def log_in():
    st.title("ESPN Fantasy Football Luck Analyzer")
    st.write("Welcome to the Fantasy Football Luck Analyzer!")
    st.write("This tool will help you determine how lucky or unlucky you've been in your fantasy football league.") 

    if 'league' not in st.session_state:
        st.session_state['league'] = None
    if 'league_data' not in st.session_state:
        st.session_state['league_data'] = None

    if DEBUG_MODE:
        st.session_state['logged_in'] = True
        st.session_state['league_id'] = LEAGUE_ID
        st.session_state['swid'] = SWID
        st.session_state['espn_s2'] = ESPN_S2
        # Fetch league data and store in session state
        with st.spinner('Just a moment. Fetching your custom league data...'):
            league = League(league_id=LEAGUE_ID, year=2024, espn_s2=ESPN_S2, swid=SWID)
            st.session_state['league'] = league
            st.session_state['league_data'] = fetch_league_data(league)
        st.rerun()
    else:
        # Input Fields
        st.header("Enter Your League Information")
        league_id = st.text_input("League ID", help="Your ESPN Fantasy Football League ID")
        swid = st.text_input("SWID", help="Find this in your browser cookies for ESPN.")
        espn_s2 = st.text_input("ESPN_S2", help="Find this in your browser cookies for ESPN.", type="password")

        with st.expander("How to find your SWID and ESPN_S2 tokens"):
            st.write("""
                1. Open your web browser and go to the ESPN Fantasy Football website.
                2. Log in to your account.
                3. Open the developer tools (usually by right-clicking on the page and selecting "Inspect" or pressing F12).
                4. Go to the "Application" tab.
                5. Under "Cookies", find the cookies for `espn.com`.
                6. Look for the `SWID` and `ESPN_S2` cookies and copy their values.
            """)

        # Submit Button
        if st.button("Submit"):
            if not league_id or not swid or not espn_s2:
                st.error("Please fill in all fields.")
            else:
                st.success("Credentials submitted! Fetching data...")
                st.session_state['logged_in'] = True
                st.session_state['league_id'] = league_id
                st.session_state['swid'] = swid
                st.session_state['espn_s2'] = espn_s2

                # Fetch league data and store in session state
                with st.spinner('Just a moment. Fetching your custom league data...'):
                    league = League(league_id=league_id, year=2024, espn_s2=espn_s2, swid=swid)
                    st.session_state['league'] = league
                    st.session_state['league_data'] = fetch_league_data(league)

                st.rerun()

def display_visualizations():
    if 'league_data' not in st.session_state or st.session_state['league_data'] is None:
            st.error("League data not found. Please log in.")
            st.session_state['logged_in'] = False
            st.rerun()
            return  # Stop execution of this function

    st.title(f"{st.session_state['league_data']['league_name']}: Luck Analysis")

    st.write("Here are some visualizations to help you analyze your luck in the league. Postseason fantasy weeks are omitted.")

    # Create a 2x2 grid for the buttons
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        if st.button("Opponent Underperformance"):
            st.session_state['metric'] = 'opponent_underperformance'
    with col2:
        if st.button("Pythagorean Expectation"):
            st.session_state['metric'] = 'pythagorean_expectation'
    with col3:
        if st.button("Scatterplot Luck"):
            st.session_state['metric'] = 'scatterplot_luck'
    with col4:
        if st.button("Scheduling Luck"):
            st.session_state['metric'] = 'scheduling_luck'

    # Display the selected metric
    if 'metric' in st.session_state:
        if 'league_data' not in st.session_state or 'league' not in st.session_state:
            st.error("League data not found. Please log in again.")
            st.session_state['logged_in'] = False
            st.rerun()
        else:
            league_data = st.session_state['league_data']
            league = st.session_state['league']

            if st.session_state['metric'] == 'opponent_underperformance':
                
                st.subheader("Opponent Underperformance")
                st.write("""
                    This visualization shows how much your opponents underperformed or overperformed 
                    compared to their projected scores. Positive values indicate that your opponents 
                    scored less than expected, while negative values indicate they scored more than expected.
                         
                    e.g. If your opponent was projected to score 100 points but only scored 80,
                    your luck index is +20. Conversely, if they were projected to score 100
                    points but scored 120, your luck index is -20 (unlucky for you!).
                """)
                
                luck_indices = get_luck_index_v3(league_data)
                luck_indices_df = save_luck_indices_to_file_v3(league_data, luck_indices)
                st.dataframe(luck_indices_df, hide_index=True)
                plot = generate_opponent_underperformance_chart(luck_indices_df)
                st.pyplot(plot)
            elif st.session_state['metric'] == 'pythagorean_expectation':
                
                st.subheader("Pythagorean Expectation")
                st.write("""
                    This visualization compares your actual wins to your expected wins based on the 
                    Pythagorean Expectation formula. Here, teams with a positive Luck Index have won more games 
                    than expected, while teams with a negative Luck Index have won fewer games than expected.
                """)
                
                pythagorean_luck_data = calculate_pythagorean_expectation_luck(league_data)
                fig = plot_pythagorean_expectation_luck(pythagorean_luck_data)
                st.pyplot(fig)
            elif st.session_state['metric'] == 'scatterplot_luck':
                
                st.subheader("Scatterplot Luck")
                st.write("""
                    This scatterplot visualizes your team's performance relative to the league average. 
                    The x-axis represents points scored (relative to the league average), and the y-axis 
                    represents points allowed (relative to the league average). 
                    - Blue dots indicate wins, and red dots indicate losses.
                    - The regions highlight "Lucky Wins" and "Unlucky Losses."
                """)
                
                scatterplot_luck_df = calculate_scatterplot_luck(league_data)
                team_names = scatterplot_luck_df["Team Name"].unique()
                selected_team = st.selectbox("Select a team to highlight", options=["All Teams"] + list(team_names))
                if selected_team == "All Teams":
                    selected_team = None
                fig = create_scatterplot_luck_figure(scatterplot_luck_df, selected_team)
                st.plotly_chart(fig)
            elif st.session_state['metric'] == 'scheduling_luck':
                st.subheader("Scheduling Luck")
                st.write("""
                This table shows how each team would have performed if they had played every other team’s schedule. 
                Think of each **row** as the **team being simulated**, and each **column** as the **schedule being tested**. 
                So, the cell at `[i][j]` tells you what **Team i’s** record would have been if they had played **Team j’s** 
                actual opponents week to week. This is a way to simulate schedule difficulty and see how much a team’s record 
                might be inflated or deflated by luck of the draw.

                Let’s say Team A thinks Team B had a much easier path. You can use the table to test that idea: 
                compare `[A][A]` (Team A’s actual record) with `[A][B]` (Team A on Team B’s schedule), and compare 
                `[B][B]` to `[B][A]`. If Team A does a lot better on B’s schedule, and Team B does worse on A’s, 
                that might mean A was right to feel a little unlucky.
                         
                NOTE: Mirror matchups are not included in this simulation (if you were an opponent of team B
                and wanted to simulate your team on their schedule, the week(s) you face "yourself" would be
                excluded from the simulation).
                """)
                
                scheduling_luck_df = create_scheduling_luck_dataframe(league_data)
                st.dataframe(scheduling_luck_df)

    # Back Button
    if st.button("Back"):
        st.session_state['logged_in'] = False
        st.rerun()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in'] == True:
        display_visualizations()
    else:
        log_in()

if __name__ == "__main__":
    main()
