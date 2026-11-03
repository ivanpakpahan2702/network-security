"""Capstone: investigasi & rencana perbaikan: aplikasi Flask mandiri dengan database sendiri (SQLite/MySQL)."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from labcore.factory import create_app as build_app, run_single


def create_app(data_dir=None, testing=False, allow_lan=False, database_settings=None):
    return build_app("40_capstone", data_dir=data_dir, testing=testing, allow_lan=allow_lan, database_settings=database_settings)


if __name__ == "__main__":
    run_single("40_capstone")

