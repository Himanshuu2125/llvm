import subprocess
from pathlib import Path


class LLVMService:
    """
    Service for compiling C files to LLVM bytecode.
    """

    def __init__(self, clang_path: str = "clang"):
        """
        Initialize the service with the path to clang.
        :param clang_path: Path to clang executable. Default assumes it's in PATH.
        """
        self.clang_path = clang_path

    def compile_to_bytecode(self, c_file_path: str, output_bc_path: str = None) -> str:
        """
        Compile a C file to LLVM bytecode (.bc).
        :param c_file_path: Path to the input C file.
        :param output_bc_path: Optional path for output .bc file. Defaults to same as input with .bc extension.
        :return: Path to the generated .bc file.
        """
        c_file = Path(c_file_path)
        if not c_file.exists():
            raise FileNotFoundError(f"C file not found: {c_file_path}")

        if output_bc_path is None:
            output_bc_path = c_file.with_suffix(".bc")

        cmd = [
            self.clang_path,
            "-c",
            "-emit-llvm",
            str(c_file),
            "-o",
            str(output_bc_path),
        ]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to compile {c_file_path} to bytecode. Error: {e}"
            )

        return str(output_bc_path)
