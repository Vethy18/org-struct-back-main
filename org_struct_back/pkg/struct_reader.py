import os
from abc import ABC, abstractmethod
from uuid import uuid4

import pandas as pd

from org_struct_back.settings.struct_reader_settings import StructReaderSettings
from org_struct_back.storage.entities import NodeEntity


class StructReader(ABC):
    @abstractmethod
    def parse(self) -> NodeEntity | None:
        pass


class StructReaderImpl(StructReader):
    def __init__(self, settings: StructReaderSettings) -> None:
        self._settings = settings
        self._lines = self._read_excel()

    def parse(self) -> NodeEntity | None:
        from collections import defaultdict

        root_nodes: dict[str, NodeEntity] = {}
        node_map: dict[tuple[str, ...], NodeEntity] = {}

        for row in self._lines:
            print(f"[ROW] {row}")  # Debug row
            if len(row) < 5:
                continue

            path = tuple(row[:5])
            parent_node = None

            for i in range(1, len(path) + 1):
                sub_path = path[:i]
                name = path[i - 1]

                if not name or str(name).strip() == "":
                    continue

                if sub_path in node_map:
                    parent_node = node_map[sub_path]
                    continue

                node = NodeEntity(id=uuid4(), name=name, parent=parent_node)
                node_map[sub_path] = node

                if parent_node:
                    parent_node.children[name] = node
                else:
                    root_nodes[name] = node

                parent_node = node

        print(f"\n[DEBUG] Parsed {len(root_nodes)} root node(s).")
        for root in root_nodes.values():
            print(f"[DEBUG ROOT] {root.name}")
        print("[DEBUG] Returning first root node (if any)...\n")

        return list(root_nodes.values())[0] if root_nodes else None

    def _read_excel(self) -> list[list[str]]:
        if not os.path.isfile(self._settings.csv_path):
            print(f"[ERROR] File not found: {self._settings.csv_path}")
            return []

        df = pd.read_excel(
            self._settings.csv_path,
            header=None,
            names=["ЮЛ", "Филиал", "Департамент", "Отдел", "Должность"],
            dtype=str
        )

        df = df.fillna(method="ffill")  # Fill down empty cells
        df_unique = df.drop_duplicates()

        print(f"[INFO] Loaded {len(df_unique)} unique rows from Excel")
        return df_unique.values.tolist()



__all__ = ["StructReader", "StructReaderImpl"]
