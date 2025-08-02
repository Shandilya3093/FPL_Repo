import requests
import pandas as pd
from datetime import datetime
import glob
import os

def get_fpl_player_data():
    """
    Fetch FPL player data including names, values, and clubs from bootstrap-static endpoint
    and save to Excel file
    """
    try:
        # FPL API base URL
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        
        # Make request to FPL API
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract teams data for club names
        teams = {team['id']: team['name'] for team in data['teams']}
        
        # Extract player data
        players = []
        for player in data['elements']:
            players.append({
                'id': player['id'],
                'name': f"{player['first_name']} {player['second_name']}",
                'web_name': player['web_name'],
                'club': teams[player['team']],
                'position': player['element_type'],
                'current_price': player['now_cost'] / 10,  # Price is in tenths
                'total_points': player['total_points'],
                'form': player['form'],
                'points_per_game': player['points_per_game']
            })
        
        # Create DataFrame
        df = pd.DataFrame(players)
        
        # Delete previous player files
        if os.path.exists("fpl_players.xlsx"):
            try:
                os.remove("fpl_players.xlsx")
            except OSError:
                pass  # Skip if file is in use
        
        # Generate filename
        filename = "fpl_players.xlsx"
        
        # Save to Excel
        df.to_excel(filename, index=False)
        
        print(f"Player data saved to {filename}")
        print(f"Total players: {len(players)}")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FPL API: {e}")
        return None
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def get_fpl_fixtures(event_id=None):
    """
    Fetch FPL fixtures data (without difficulty ratings)
    
    Args:
        event_id (int, optional): Specific gameweek number. If None, gets all fixtures.
    """
    try:
        # FPL API fixtures URL
        if event_id:
            url = f"https://fantasy.premierleague.com/api/fixtures/?event={event_id}"
        else:
            url = "https://fantasy.premierleague.com/api/fixtures/"
        
        # Get teams data for team names
        bootstrap_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        bootstrap_response = requests.get(bootstrap_url)
        bootstrap_response.raise_for_status()
        bootstrap_data = bootstrap_response.json()
        
        teams = {team['id']: team['name'] for team in bootstrap_data['teams']}
        
        # Make request to fixtures API
        response = requests.get(url)
        response.raise_for_status()
        
        fixtures_data = response.json()
        
        # Extract fixtures data (without difficulty ratings)
        fixtures = []
        for fixture in fixtures_data:
            fixtures.append({
                'fixture_id': fixture['id'],
                'gameweek': fixture['event'],
                'kickoff_time': fixture['kickoff_time'],
                'home_team': teams[fixture['team_h']],
                'away_team': teams[fixture['team_a']],
                'finished': fixture['finished'],
                'home_score': fixture['team_h_score'],
                'away_score': fixture['team_a_score'],
                'minutes': fixture['minutes'],
                'provisional_start_time': fixture['provisional_start_time']
            })
        
        # Create DataFrame
        df = pd.DataFrame(fixtures)
        
        # Delete previous fixture files
        if event_id:
            filename_to_delete = f"fpl_fixtures_gw{event_id}.xlsx"
        else:
            filename_to_delete = "fpl_fixtures_all.xlsx"
        
        if os.path.exists(filename_to_delete):
            try:
                os.remove(filename_to_delete)
            except OSError:
                pass  # Skip if file is in use
        
        # Generate filename
        if event_id:
            filename = f"fpl_fixtures_gw{event_id}.xlsx"
        else:
            filename = "fpl_fixtures_all.xlsx"
        
        # Save to Excel
        df.to_excel(filename, index=False)
        
        print(f"Fixtures data saved to {filename}")
        print(f"Total fixtures: {len(fixtures)}")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching fixtures data from FPL API: {e}")
        return None
    except Exception as e:
        print(f"Error processing fixtures data: {e}")
        return None

def get_fpl_fdr(event_id=None):
    """
    Fetch FPL Fixture Difficulty Ratings (FDR) data
    
    Args:
        event_id (int, optional): Specific gameweek number. If None, gets all FDR data.
    """
    try:
        # FPL API fixtures URL
        if event_id:
            url = f"https://fantasy.premierleague.com/api/fixtures/?event={event_id}"
        else:
            url = "https://fantasy.premierleague.com/api/fixtures/"
        
        # Get teams data for team names
        bootstrap_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        bootstrap_response = requests.get(bootstrap_url)
        bootstrap_response.raise_for_status()
        bootstrap_data = bootstrap_response.json()
        
        teams = {team['id']: team['name'] for team in bootstrap_data['teams']}
        
        # Make request to fixtures API
        response = requests.get(url)
        response.raise_for_status()
        
        fixtures_data = response.json()
        
        # Extract FDR data
        fdr_data = []
        for fixture in fixtures_data:
            # Add home team FDR
            fdr_data.append({
                'fixture_id': fixture['id'],
                'gameweek': fixture['event'],
                'team': teams[fixture['team_h']],
                'opponent': teams[fixture['team_a']],
                'home_away': 'Home',
                'difficulty_rating': fixture['team_h_difficulty'],
                'kickoff_time': fixture['kickoff_time'],
                'finished': fixture['finished']
            })
            
            # Add away team FDR
            fdr_data.append({
                'fixture_id': fixture['id'],
                'gameweek': fixture['event'],
                'team': teams[fixture['team_a']],
                'opponent': teams[fixture['team_h']],
                'home_away': 'Away',
                'difficulty_rating': fixture['team_a_difficulty'],
                'kickoff_time': fixture['kickoff_time'],
                'finished': fixture['finished']
            })
        
        # Create DataFrame
        df = pd.DataFrame(fdr_data)
        
        # Delete previous FDR files
        if event_id:
            filename_to_delete = f"fpl_fdr_gw{event_id}.xlsx"
        else:
            filename_to_delete = "fpl_fdr_all.xlsx"
        
        if os.path.exists(filename_to_delete):
            try:
                os.remove(filename_to_delete)
            except OSError:
                pass  # Skip if file is in use
        
        # Generate filename
        if event_id:
            filename = f"fpl_fdr_gw{event_id}.xlsx"
        else:
            filename = "fpl_fdr_all.xlsx"
        
        # Save to Excel
        df.to_excel(filename, index=False)
        
        print(f"FDR data saved to {filename}")
        print(f"Total FDR entries: {len(fdr_data)}")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching FDR data from FPL API: {e}")
        return None
    except Exception as e:
        print(f"Error processing FDR data: {e}")
        return None

def analyze_next_5_fixtures_fdr(start_gameweek):
    """
    Analyze the next 5 fixtures for each club starting from a given gameweek
    and rank clubs by their average FDR (1=easiest, 5=hardest)
    
    Args:
        start_gameweek (int): Starting gameweek number
    """
    try:
        # Read the FDR data
        if not os.path.exists("fpl_fdr_all.xlsx"):
            print("Error: fpl_fdr_all.xlsx not found. Please run get_fpl_fdr() first.")
            return None
        
        df = pd.read_excel("fpl_fdr_all.xlsx")
        
        # Filter for next 5 gameweeks starting from start_gameweek
        end_gameweek = start_gameweek + 4
        next_5_df = df[(df['gameweek'] >= start_gameweek) & (df['gameweek'] <= end_gameweek)]
        
        # Group by team and calculate stats for next 5 fixtures
        team_analysis = []
        for team in next_5_df['team'].unique():
            team_data = next_5_df[next_5_df['team'] == team].sort_values('gameweek')
            
            if len(team_data) > 0:
                fixtures = team_data.head(5)  # Get up to 5 fixtures
                
                team_analysis.append({
                    'team': team,
                    'fixtures_analyzed': len(fixtures),
                    'average_fdr': fixtures['difficulty_rating'].mean(),
                    'total_fdr': fixtures['difficulty_rating'].sum(),
                    'gw1_opponent': fixtures.iloc[0]['opponent'] if len(fixtures) > 0 else '',
                    'gw1_fdr': fixtures.iloc[0]['difficulty_rating'] if len(fixtures) > 0 else '',
                    'gw1_home_away': fixtures.iloc[0]['home_away'] if len(fixtures) > 0 else '',
                    'gw2_opponent': fixtures.iloc[1]['opponent'] if len(fixtures) > 1 else '',
                    'gw2_fdr': fixtures.iloc[1]['difficulty_rating'] if len(fixtures) > 1 else '',
                    'gw2_home_away': fixtures.iloc[1]['home_away'] if len(fixtures) > 1 else '',
                    'gw3_opponent': fixtures.iloc[2]['opponent'] if len(fixtures) > 2 else '',
                    'gw3_fdr': fixtures.iloc[2]['difficulty_rating'] if len(fixtures) > 2 else '',
                    'gw3_home_away': fixtures.iloc[2]['home_away'] if len(fixtures) > 2 else '',
                    'gw4_opponent': fixtures.iloc[3]['opponent'] if len(fixtures) > 3 else '',
                    'gw4_fdr': fixtures.iloc[3]['difficulty_rating'] if len(fixtures) > 3 else '',
                    'gw4_home_away': fixtures.iloc[3]['home_away'] if len(fixtures) > 3 else '',
                    'gw5_opponent': fixtures.iloc[4]['opponent'] if len(fixtures) > 4 else '',
                    'gw5_fdr': fixtures.iloc[4]['difficulty_rating'] if len(fixtures) > 4 else '',
                    'gw5_home_away': fixtures.iloc[4]['home_away'] if len(fixtures) > 4 else ''
                })
        
        # Create DataFrame and sort by average FDR (lowest to highest)
        analysis_df = pd.DataFrame(team_analysis)
        analysis_df = analysis_df.sort_values('average_fdr')
        
        # Add ranking
        analysis_df['fdr_rank'] = range(1, len(analysis_df) + 1)
        
        # Reorder columns
        column_order = ['fdr_rank', 'team', 'average_fdr', 'total_fdr', 'fixtures_analyzed',
                       'gw1_opponent', 'gw1_fdr', 'gw1_home_away',
                       'gw2_opponent', 'gw2_fdr', 'gw2_home_away',
                       'gw3_opponent', 'gw3_fdr', 'gw3_home_away',
                       'gw4_opponent', 'gw4_fdr', 'gw4_home_away',
                       'gw5_opponent', 'gw5_fdr', 'gw5_home_away']
        
        analysis_df = analysis_df[column_order]
        
        # Delete previous analysis file
        filename = f"fpl_next5_fdr_analysis_gw{start_gameweek}.xlsx"
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError:
                pass
        
        # Save to Excel
        analysis_df.to_excel(filename, index=False)
        
        print(f"Next 5 fixtures FDR analysis saved to {filename}")
        print(f"Starting from gameweek {start_gameweek} to {end_gameweek}")
        print(f"Teams analyzed: {len(analysis_df)}")
        print(f"\nEasiest 5 teams (lowest FDR):")
        for i, row in analysis_df.head(5).iterrows():
            print(f"{row['fdr_rank']}. {row['team']} (Avg FDR: {row['average_fdr']:.2f})")
        
        return analysis_df
        
    except Exception as e:
        print(f"Error analyzing FDR data: {e}")
        return None

if __name__ == "__main__":
    # Get player data
    print("Fetching player data...")
    get_fpl_player_data()
    
    # Get all fixtures data
    print("\nFetching all fixtures data...")
    get_fpl_fixtures()
    
    # Get all FDR data
    print("\nFetching all FDR data...")
    get_fpl_fdr()
    
    # Get current gameweek fixtures (example - gameweek 1)
    print("\nFetching gameweek 1 fixtures...")
    get_fpl_fixtures(event_id=1)
    
    # Get current gameweek FDR (example - gameweek 1)
    print("\nFetching gameweek 1 FDR...")
    get_fpl_fdr(event_id=1)