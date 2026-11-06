"""Verify pinned archive content and compare every available private Git blob."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import history_evidence
if __name__=='__main__':print(json.dumps(history_evidence.verify_all(),sort_keys=True))
