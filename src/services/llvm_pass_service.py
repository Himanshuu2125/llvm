#!/usr/bin/env python3
"""
llvm_pass_service.py

Usage:
    python llvm_pass_service.py config.json
or import LLVMPassService from this file and call apply_passes_from_json()

The script:
- Builds -mllvm -passes=... and per-pass -mllvm flags from JSON config
- Runs clang again to apply passes and produce an obfuscated .bc output
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.services.llvm_service import LLVMService
from src.utils.stats_parser import parse_llvm_stats


class LLVMPassService:
    def __init__(
        self,
        clang_path: str = "clang",
        work_dir: Optional[str] = None,
    ):
        self.clang = shutil.which(clang_path) or clang_path
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()
        self.stats = {}
        if not shutil.which(self.clang):
            print(
                f"[WARN] clang binary '{clang_path}' not found in PATH. Will try to run '{self.clang}' anyway."
            )

    def _load_json_config(self, json_path: str) -> dict:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def _run_cmd(self, params: List[str]) -> Tuple[bool, str, str]:
        try:
            print("[CMD]", " ".join(params))

            result = subprocess.run(
                params,
                cwd=self.work_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

        except Exception as e:
            print(f"[ERROR] Failed to execute command: {e}")
            return False

    def _build_mllvm_tags(self, pass_name: str, params: Dict[str, Any]) -> List[str]:
        tags = ["-mllvm", f"-passes={pass_name}"]
        if params:
            for key, value in params.items():
                if key != "cycles":
                    if pass_name in ["mba", "bcf"]:
                        tags.extend(["-mllvm", f"-{key}={value}"])
                    else:
                        tags.extend(["-mllvm", f"-{pass_name}-{key}={value}"])
        tags.extend(["-mllvm", "-stats"])
        return tags

    def apply_json_conf(
        self, config: Dict[str, Any], input_file: str, output_file: str
    ):
        passes = config.get("passes", [])

        for obfpass in passes:
            if not obfpass.get("enabled"):
                continue

            pass_name = obfpass.get("name")
            params = obfpass.get("params", {})

            cycles = int(params.get("cycles", 1))

            cmd = [
                self.clang,
                "-c",
                "-emit-llvm",
                *self._build_mllvm_tags(pass_name, params),
                input_file,
                "-o",
                output_file,
            ]

            for _ in range(cycles):
                success, stdout, stderr = self._run_cmd(cmd)

                if stderr:
                    run_stats = parse_llvm_stats(stderr)
                    if not hasattr(self, "stats") or self.stats is None:
                        self.stats = {}
                    for key, metrics in run_stats.items():
                        if key not in self.stats:
                            self.stats[key] = {}
                        for metric_name, value in metrics.items():
                            if metric_name in self.stats[key]:
                                self.stats[key][metric_name] += value
                            else:
                                self.stats[key][metric_name] = value

                if not success:
                    print(f"[ERROR] Pass '{pass_name}' failed.")
                    break
            input_file = output_file

    def apply_passes(
        self, input_file: str, json_file: str, output_file: Optional[str] = None
    ):
        try:
            input_path = Path(input_file)

            if output_file is None:
                output_file = str(input_path.with_name(f"{input_path.stem}_obf.bc"))

            config = self._load_json_config(json_file)

            self.apply_json_conf(config, input_file, output_file)

        except FileNotFoundError:
            print(f"[ERROR] JSON config file not found: {json_file}")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON config: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")


if __name__ == "__main__":
    input_file = r"\path\to\input"
    json_file = r"path\to\json"
    llvm = LLVMService()
    input_bc_file = llvm.compile_to_bytecode(input_file)
    llvmpass = LLVMPassService(r"path\to\clang")
    llvmpass.apply_passes(input_bc_file, json_file)
