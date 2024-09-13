import argparse

import sys
sys.path.append('./scripts')

from scripts.headline_analyzer import HeadlineAnalyzer
from scripts.headline_main import HeadlineMain
from scripts.headline_manager import HeadlineManager
from scripts.helpers.config import Config
from scripts.helpers.supabase_db import SupabaseDB

def initialize():
    config = Config('./config.yaml')
    db = SupabaseDB(config.get('supabase_url'), config.get('supabase_key'))
    manager = HeadlineManager(db)
    
    analyzer = HeadlineAnalyzer(
        api_key=config.get('openai_key'),
        base_url="https://api.openai.com/v1/",
        model="gpt-4o-mini"
    )
    # analyzer = HeadlineAnalyzer(
    #     model="gemma2-9b"
    # )

    return config, db, manager, analyzer

def main():
    parser = argparse.ArgumentParser(description="Analyze headlines for misogynistic content.")
    parser.add_argument("--media", nargs='+', help="List of media URLs to analyze")
    args = parser.parse_args()

    config, _, manager, analyzer = initialize()

    analysis_manager = HeadlineMain(config, manager, analyzer)

    def progress_callback(current, total, url):
        if not current:
            print(f"Fetching headline from {url}")
        else:
            print(f"Processing link {current}/{total}")

    medias = args.media if args.media else config.get('medias', [])
    if not medias:
        print("No media sources provided. Please specify media sources using --media or add them to the config file.")
        return
    
    results = analysis_manager.analyze_headlines(medias, progress_callback)

    print(f"{len(results)} headlines analyzed and saved!")

if __name__ == "__main__":
    main()