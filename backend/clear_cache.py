#!/usr/bin/env python3
"""
Command-line script to clear expired cache entries
"""

import argparse
import json
from app.core.maintenance import clear_expired_cache

def main():
    """Main entry point for the cache maintenance script"""
    parser = argparse.ArgumentParser(description="Clear expired cache entries from the database")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually delete entries, just report")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()
    
    # Run the cache maintenance
    result = clear_expired_cache(dry_run=args.dry_run)
    
    # Output as JSON if requested
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Print a human-readable summary
        print(f"Cache maintenance summary:")
        print(f"- Total entries: {result['total']['places']} places ({result['total']['size']})")
        
        if 'deleted' in result and result['deleted']:
            print(f"- Deleted: {result['deleted']['places']} places ({result['deleted']['size']})")
        elif args.dry_run:
            print(f"- Would delete: {result['expired']['places']} places ({result['expired']['size']})")
        
        print(f"- Remaining: {result['remaining']['places']} places")
        
        if 'processing_time' in result:
            print(f"- Processing time: {result['processing_time']}")

if __name__ == "__main__":
    main() 