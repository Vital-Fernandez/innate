import logging
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# Read lime configuration .toml
_inst_dir = Path(__file__).parent
_conf_path = _inst_dir/'config.toml'
with open(_conf_path, mode="rb") as fp:
    _setup_cfg = tomllib.load(fp)

from .io import save_dataset

from .main import DataSet, Grid