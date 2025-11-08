from visualization import save_luck_indices_to_file_v3
from legacy_functions import save_luck_indices_to_file_v1, save_luck_indices_to_file_v2
from api_client import fetch_league_data
from analysis import get_luck_index_v3
from dotenv import load_dotenv
import os
import time
from espn_api.football import League

# Load environment variables from .env file
load_dotenv()

# Fetch credentials from environment variables
LEAGUE_ID = int(os.getenv('LEAGUE_ID'))
SWID = os.getenv('SWID')
ESPN_S2 = os.getenv('ESPN_S2')

def benchmark_comparison(league):
    # Time the original function
    print("Timing save_luck_indices_to_file_v1...")
    start_time = time.time()
    save_luck_indices_to_file_v1(league)
    end_time = time.time()
    original_time = end_time - start_time
    print(f"save_luck_indices_to_file_v1 runtime: {original_time:.2f} seconds")


    print("\nTiming save_luck_indices_to_file_v2...")
    # Time the v2 function, which is algorithmically optimized
    start_time = time.time()
    save_luck_indices_to_file_v2(league)
    end_time = time.time()
    optimized_time = end_time - start_time
    print(f"save_luck_indices_to_file_v2 runtime: {optimized_time:.2f} seconds")

    print("\nTiming save_luck_indices_to_file_v3...")
    # Time the v3 function, which also prefetches league data
    start_time = time.time()
    league_data = fetch_league_data(league)
    luck_indices_3 = get_luck_index_v3(league_data)
    save_luck_indices_to_file_v3(league_data, luck_indices_3, None)
    end_time = time.time()
    new_time = end_time - start_time
    print(f"save_luck_indices_to_file_v3 runtime: {new_time:.2f} seconds")

    # Compare the three runtimes
    print("\nComparison of runtimes:")
    print(f"Original function runtime: {original_time:.2f} seconds")
    print(f"Optimized function runtime: {optimized_time:.2f} seconds")
    print(f"New function runtime: {new_time:.2f} seconds")
    print(f"Performance improvement (2 vs 1): {((original_time - optimized_time) / original_time) * 100:.2f}% faster")
    print(f"Performance improvement (3 vs 1): {((original_time - new_time) / original_time) * 100:.2f}% faster")
    print(f"Performance improvement (3 vs 2): {((optimized_time - new_time) / optimized_time) * 100:.2f}% faster")

def main():
    # Use environment variables to initialize the League object
    league = League(league_id=LEAGUE_ID, year=2024, espn_s2=ESPN_S2, swid=SWID)
    benchmark_comparison(league)

if __name__ == "__main__":
    main()
