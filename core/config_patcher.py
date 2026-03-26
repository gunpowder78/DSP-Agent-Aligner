"""Configuration Patcher - AST-based source code hot-patching with isolation safety."""

import ast
import pathlib
from typing import Any


class ConfigPatcher:
    """Safe configuration hot-patcher using AST manipulation."""

    @staticmethod
    def patch_constant(file_path: pathlib.Path, target_name: str, new_value: Any) -> bool:
        """Patch a constant value in a Python source file using AST."""
        try:
            source_code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source_code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == target_name:
                            if isinstance(node.value, ast.Constant):
                                node.value.value = new_value
                            elif isinstance(node.value, ast.Num):
                                node.value.n = new_value

            modified_code = ast.unparse(tree)
            file_path.write_text(modified_code, encoding="utf-8")
            return True
        except Exception:
            return False

    @staticmethod
    def read_constant(file_path: pathlib.Path, target_name: str) -> Any:
        """Read a constant value from a Python source file using AST."""
        try:
            source_code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source_code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == target_name:
                            if isinstance(node.value, ast.Constant):
                                return node.value.value
                            elif isinstance(node.value, ast.Num):
                                return node.value.n
            return None
        except Exception:
            return None

    @staticmethod    def validate_syntax(file_path: pathlib.Path) -> bool:
        """Validate Python source file syntax."""
        try:
            source_code = file_path.read_text(encoding="utf-8")
            ast.parse(source_code)
            return True
        except SyntaxError:
            return False
