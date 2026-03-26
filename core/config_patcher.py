"""Configuration Patcher - AST-based source code hot-patching with isolation safety."""

import ast
import pathlib
from typing import Any


class ConfigPatcher:
    """Safe configuration hot-patcher using AST manipulation."""

    @staticmethod
    def patch_constant(file_path: pathlib.Path, target_name: str, new_value: Any) -> bool:
        """Patch a top-level constant value in a Python source file using AST.

        Args:
            file_path: Path to the Python source file
            target_name: Name of the constant variable (e.g., 'TARGET_DEVICE_ID')
            new_value: New value to assign (int, float, str, bool)

        Returns:
            True if patching succeeded

        Raises:
            ValueError: If target constant not found in file
            RuntimeError: If patching fails due to other errors
        """
        try:
            source_code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source_code)

            found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == target_name:
                            found = True
                            node.value = ast.Constant(value=new_value)

            if not found:
                raise ValueError(f"Constant '{target_name}' not found in file")

            modified_code = ast.unparse(tree)
            file_path.write_text(modified_code, encoding="utf-8")
            return True
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to patch constant: {str(e)}")

    @staticmethod
    def patch_dict_constant(
        file_path: pathlib.Path,
        dict_name: str,
        key_name: str,
        new_value: Any
    ) -> bool:
        """Patch a value inside a dictionary constant in a Python source file using AST.

        Args:
            file_path: Path to the Python source file
            dict_name: Name of the dictionary variable (e.g., 'PYO_CONFIG')
            key_name: Key name inside the dictionary (e.g., 'device')
            new_value: New value to assign to the key

        Returns:
            True if patching succeeded

        Raises:
            ValueError: If dictionary or key not found
            RuntimeError: If patching fails
        """
        try:
            source_code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source_code)

            found_dict = False
            found_key = False

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == dict_name:
                            found_dict = True
                            if isinstance(node.value, ast.Dict):
                                for i, key in enumerate(node.value.keys):
                                    key_value = None
                                    if isinstance(key, ast.Constant):
                                        key_value = key.value

                                    if key_value == key_name:
                                        found_key = True
                                        node.value.values[i] = ast.Constant(value=new_value)
                                        break

            if not found_dict:
                raise ValueError(f"Dictionary '{dict_name}' not found in file")
            if not found_key:
                raise ValueError(f"Key '{key_name}' not found in dictionary '{dict_name}'")

            modified_code = ast.unparse(tree)
            file_path.write_text(modified_code, encoding="utf-8")
            return True
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to patch dictionary: {str(e)}")

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

    @staticmethod
    def read_dict_constant(file_path: pathlib.Path, dict_name: str, key_name: str) -> Any:
        """Read a value from a dictionary constant in a Python source file using AST.

        Args:
            file_path: Path to the Python source file
            dict_name: Name of the dictionary variable
            key_name: Key name inside the dictionary

        Returns:
            The value if found, None otherwise
        """
        try:
            source_code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source_code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == dict_name:
                            if isinstance(node.value, ast.Dict):
                                for i, key in enumerate(node.value.keys):
                                    if isinstance(key, ast.Constant) and key.value == key_name:
                                        value_node = node.value.values[i]
                                        if isinstance(value_node, ast.Constant):
                                            return value_node.value
                                        elif isinstance(value_node, ast.Num):
                                            return value_node.n
            return None
        except Exception:
            return None

    @staticmethod
    def validate_syntax(file_path: pathlib.Path) -> bool:
        """Validate Python source file syntax."""
        try:
            source_code = file_path.read_text(encoding="utf-8")
            ast.parse(source_code)
            return True
        except SyntaxError:
            return False
