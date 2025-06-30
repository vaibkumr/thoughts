import argparse
import json
import sys
from typing import Optional

# Add the project root to the Python path to allow imports from other packages
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from sqlalchemy.orm import Session
from thoughts.api.database import SessionLocal, Thought

def dump_thoughts(output_file: Optional[str] = None):
    """
    Dumps all thoughts from the database to stdout or a file in JSON format.
    """
    db = SessionLocal()
    try:
        thoughts = db.query(Thought).order_by(Thought.timestamp).all()
        
        thoughts_list = [
            {
                "id": thought.id,
                "content": thought.content,
                "timestamp": thought.timestamp.isoformat(),
            }
            for thought in thoughts
        ]
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(thoughts_list, f, indent=4)
            print(f"Successfully dumped {len(thoughts_list)} thoughts to {output_file}", file=sys.stderr)
        else:
            json.dump(thoughts_list, sys.stdout, indent=4)
            
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dump all thoughts from the database to JSON format.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the output file. If not provided, dumps to stdout.",
        type=str,
        default=None
    )
    args = parser.parse_args()
    
    # This is needed to run the script standalone and allow it to find the 'thoughts' module
    original_cwd = os.getcwd()
    try:
        # We need to run this from the project root for the imports to work correctly
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        os.chdir(project_root)
        
        # Now that we're in the right directory, we can call the function
        # But first, let's make sure we have the correct modules.
        from thoughts.api.database import SessionLocal, Thought
        dump_thoughts(output_file=args.output)
    finally:
        os.chdir(original_cwd) 