from __future__ import annotations

import json
import pathlib
import tkinter as tk
from tkinter import ttk
from typing import Any


class App(tk.Tk):
    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.title("TCPad: TCP 客户端 & 服务器")
        self.minsize(800, 600)
        self.geometry("800x600")

        left = tk.Frame(self, width=260)
        left.pack_propagate(False)
        left.pack(side=tk.LEFT, fill=tk.Y)

        self.right = tk.Frame(self)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(left)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.quick_input_area = tk.Frame(left)
        self.quick_input_area.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))

        self.client_tab = tk.Frame(self.notebook)
        self.notebook.add(self.client_tab, text="客户端")

        self.server_tab = tk.Frame(self.notebook)
        self.notebook.add(self.server_tab, text="服务器")

        self.config = Config()
        self.controller = Controller(self)

        self.ui()

    def ui(self) -> None:
        last_tab_index = self.config.get("selected_tab_index")
        if last_tab_index:
            self.notebook.select(int(last_tab_index))

        def on_tab_changed(_: tk.Event[ttk.Notebook]) -> object:
            selected_index: int = self.notebook.index(self.notebook.select())
            self.config.set("selected_tab_index", selected_index)

        self.notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

        for i in range(1, 11):
            row = tk.Frame(self.quick_input_area)
            row.pack(fill=tk.X, pady=2)

            var = tk.StringVar(value="")
            self.config.bind(f"quick_input_{i}", var)

            entry = tk.Entry(row, textvariable=var)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

            def submit(var: tk.StringVar = var) -> Any:
                data = var.get()
                if not data:
                    return

                self.controller.submit(data)

            button = tk.Button(row, text="发送", command=submit)
            button.pack(side=tk.RIGHT)

        textarea = tk.Text(self.right, font=("monospace", 11))
        textarea.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def on_input(event: tk.Event[tk.Text]) -> object:
            if event.keysym == "Return":
                data = textarea.get("insert linestart", "insert lineend").strip()
                textarea.insert(tk.END, "\n")
                self.controller.submit(data)
                return "break"

        def on_message(data: str) -> None:
            textarea.insert(tk.END, data + "\n")

        textarea.bind("<Key>", on_input)
        self.controller.on_message = on_message


class Config:
    def __init__(self) -> None:
        self.file = pathlib.Path("config.json")
        self.obj: dict[str, Any] = self.load()

    def load(self) -> dict[str, Any]:
        if not self.file.exists():
            self.file.write_text("{}", encoding="utf-8")
            return {}

        content = self.file.read_text(encoding="utf-8")
        return json.loads(content)

    def get(self, name: str) -> Any | None:
        return self.obj.get(name)

    def set(self, name: str, value: Any) -> None:
        self.obj[name] = value

        content = json.dumps(self.obj, ensure_ascii=False)
        self.file.write_text(content, encoding="utf-8")

    def bind(self, name: str, var: tk.Variable):
        value = self.get(name)
        if value:
            var.set(value)

        def on_write(*_: Any) -> object:
            self.set(name, var.get())

        var.trace_add("write", on_write)


class Controller:
    def __init__(self, app: App) -> None:
        self.app = app

    def submit(self, data: str) -> None:
        self.on_message(data)

    def on_message(self, data: str) -> None:
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
