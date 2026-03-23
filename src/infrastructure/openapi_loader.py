"""
OpenAPI specification loader service.
"""

import copy
import tempfile
import time
from pathlib import Path
from typing import Any

import httpx
import yaml

from ..domain.config import CacheConfig


class OpenApiSpecLoader:
    """Service for loading and caching OpenAPI specifications."""

    def __init__(self, cache_config: CacheConfig):
        self._cache_config = cache_config
        self._spec_url = "https://storage.googleapis.com/fc-freepik-pro-rev1-eu-api-specs/freepik-api-v1-openapi.yaml"

    def load_spec(self) -> dict[str, Any]:
        """
        Load OpenAPI spec with caching.

        Returns:
            Dict containing the OpenAPI specification.

        Raises:
            Exception: If unable to load the specification.
        """
        cached_spec = self._load_from_cache()
        if cached_spec is not None:
            return self._optimize_spec(cached_spec)

        return self._optimize_spec(self._download_and_cache_spec())

    @staticmethod
    def _truncate_description(text: str, max_len: int = 200) -> str:
        """Truncate description, keeping first sentence or max_len chars."""
        if not text or len(text) <= max_len:
            return text
        # Keep first sentence if it fits
        for sep in (". ", ".\n"):
            idx = text.find(sep)
            if 0 < idx <= max_len:
                return text[: idx + 1]
        return text[:max_len].rsplit(" ", 1)[0] + "..."

    @classmethod
    def _optimize_spec(cls, spec: dict[str, Any]) -> dict[str, Any]:
        """Aggressively strip non-input data to reduce token usage."""
        spec = copy.deepcopy(spec)

        for path_data in spec.get("paths", {}).values():
            for method_key, method_data in path_data.items():
                if not isinstance(method_data, dict):
                    continue

                # 1. Strip all responses — only keep minimal 200
                method_data["responses"] = {"200": {"description": "OK"}}

                # 2. Truncate operation description
                if "description" in method_data:
                    method_data["description"] = cls._truncate_description(
                        method_data["description"], 300
                    )

                # 3. Trim parameters: truncate descriptions, remove examples
                for param in method_data.get("parameters", []):
                    if not isinstance(param, dict):
                        continue
                    param.pop("examples", None)
                    param.pop("example", None)
                    if "description" in param:
                        param["description"] = cls._truncate_description(
                            param["description"], 120
                        )

                # 4. Trim request body: truncate descriptions, remove examples
                req_body = method_data.get("requestBody")
                if isinstance(req_body, dict):
                    for content in req_body.get("content", {}).values():
                        if isinstance(content, dict):
                            content.pop("examples", None)
                            content.pop("example", None)
                            # Trim descriptions inside schema properties
                            schema = content.get("schema", {})
                            cls._trim_schema_descriptions(schema)

        # 5. Remove component examples entirely
        components = spec.get("components", {})
        components.pop("examples", None)

        # 6. Remove response-only schemas from components
        schemas = components.get("schemas", {})
        to_remove = [
            name for name in schemas
            if any(
                kw in name.lower()
                for kw in (
                    "response", "_200_", "_400_", "_401_", "_403_",
                    "_404_", "_422_", "_429_", "_500_",
                )
            )
        ]
        for name in to_remove:
            del schemas[name]

        # 7. Trim descriptions inside remaining component schemas
        for schema in schemas.values():
            if isinstance(schema, dict):
                cls._trim_schema_descriptions(schema)

        return spec

    @classmethod
    def _trim_schema_descriptions(cls, schema: dict[str, Any]) -> None:
        """Recursively truncate descriptions within a JSON schema."""
        if not isinstance(schema, dict):
            return
        if "description" in schema:
            schema["description"] = cls._truncate_description(schema["description"], 120)
        schema.pop("example", None)
        schema.pop("examples", None)
        for prop in schema.get("properties", {}).values():
            cls._trim_schema_descriptions(prop)
        for kw in ("items", "additionalProperties"):
            if isinstance(schema.get(kw), dict):
                cls._trim_schema_descriptions(schema[kw])
        for item in schema.get("allOf", []) + schema.get("oneOf", []) + schema.get("anyOf", []):
            cls._trim_schema_descriptions(item)

    def _load_from_cache(self) -> dict[str, Any] | None:
        """Load spec from cache if it exists and is recent."""
        cache_file = self._get_cache_file_path()

        if not cache_file.exists():
            return None

        # Check if cache is still valid
        file_age = time.time() - cache_file.stat().st_mtime
        if file_age >= self._cache_config.cache_duration_seconds:
            return None

        print(f"📦 Using cached OpenAPI spec from {cache_file}")
        with open(cache_file, encoding="utf-8") as f:
            loaded_data = yaml.safe_load(f)
            return loaded_data if isinstance(loaded_data, dict) else None

    def _download_and_cache_spec(self) -> dict[str, Any]:
        """Download fresh spec and save to cache."""
        print("🌐 Downloading OpenAPI spec from Freepik...")

        try:
            response = httpx.get(self._spec_url)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to download OpenAPI spec: {e}")

        # Save to cache
        cache_file = self._get_cache_file_path()
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"💾 Cached OpenAPI spec to {cache_file}")
        loaded_data = yaml.safe_load(response.text)
        if not isinstance(loaded_data, dict):
            raise Exception("Invalid OpenAPI spec format: expected dict")
        return loaded_data

    def _get_cache_file_path(self) -> Path:
        """Get the path to the cache file."""
        temp_dir = Path(tempfile.gettempdir())
        return temp_dir / self._cache_config.cache_file_name
