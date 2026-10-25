# -*- coding: utf-8 -*-
"""把凭据写到仓库外的本地文件（不进 git），供 CAS 探测/登录使用。"""
import json
from pathlib import Path

p = Path.home() / ".hfutknow_creds.json"
p.write_text(json.dumps({"user": "2026214874", "pwd": "Cfl6159130171"}), encoding="utf-8")
print("written:", p)
