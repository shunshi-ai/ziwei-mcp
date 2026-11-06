"""让 `pytest packages/ziwei/tests` 不用设 PYTHONPATH 就能 import ziwei。

同 repo 根 conftest.py 的做法：包还没 pip install 时也要能跑。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
