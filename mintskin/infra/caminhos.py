"""Onde o MintSkin le e grava as coisas."""
from pathlib import Path

HOME = str(Path.home())
DADOS = Path(HOME, ".local/share/mintskin")
SKINS_USUARIO = DADOS / "skins"
INSTALADOS = DADOS / "instalados"
DESFAZER = DADOS / "desfazer"
NUVEM_LOCAL = DADOS / "nuvem"
CONFIG = Path(HOME, ".config/mintskin")
CACHE = Path(HOME, ".cache/mintskin")

SPICES = Path(HOME, ".config/cinnamon/spices")
PLANK_CFG = Path(HOME, ".config/plank")
AUTOSTART = Path(HOME, ".config/autostart")

_REPO = Path(__file__).resolve().parents[2]
SKINS_MINTSKIN = [p for p in (Path("/usr/share/mintskin/skins"), _REPO / "skins") if p.is_dir()]
LOGIN_HELPER = next((p for p in (Path("/usr/lib/mintskin/mintskin-login-helper"),
                                 _REPO / "helpers/mintskin-login-helper") if p.exists()),
                    Path("/usr/lib/mintskin/mintskin-login-helper"))

MAC_SH_BACKUP = Path(HOME, ".config/ativar_mac_automatico/backup")
MAC_SH_ATIVO = Path(HOME, ".config/ativar_mac_automatico/ativo")
