import ast
import math
import operator
import re
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox


@dataclass(frozen=True)
class ButtonStyle:
    base: str
    hover: str
    press: str
    fg: str


class ScientificCalculator(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Scientific Calculator")
        self.geometry("340x580")
        self.minsize(320, 540)

        self.palette = {
            "bg": "#0C0D10",
            "panel": "#161A22",
            "display": "#10141B",
            "text": "#F4F7FC",
            "muted": "#9AA5B7",
            "accent": "#55C8FF",
            "digit": "#252B36",
            "operator": "#2F3848",
            "function": "#1F2631",
            "danger": "#5A2E3A",
            "equals": "#2A90FF",
        }

        self.configure(bg=self.palette["bg"])
        self.expression_var = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="0")
        self.mode_var = tk.StringVar(value="DEG")
        self.is_radian_mode = False
        self.last_answer = 0.0

        self._button_styles: dict[tk.Button, ButtonStyle] = {}
        self._animated_buttons: list[tk.Button] = []
        self._accent_position = 0
        self._expression_label_visible = False

        self._build_ui()
        self._bind_keys()
        self.after(80, self._run_intro_animation)

    def _build_ui(self) -> None:
        display_card = tk.Frame(self, bg=self.palette["display"], padx=14, pady=12)
        display_card.pack(fill="x", padx=12, pady=(12, 8))

        top_row = tk.Frame(display_card, bg=self.palette["display"])
        top_row.pack(fill="x")

        mode_chip = tk.Label(
            top_row,
            textvariable=self.mode_var,
            font=("Bahnschrift", 10),
            fg=self.palette["accent"],
            bg=self.palette["display"],
        )
        mode_chip.pack(side="left")

        self.expression_label = tk.Label(
            display_card,
            text="",
            anchor="e",
            font=("Bahnschrift", 13),
            fg=self.palette["muted"],
            bg=self.palette["display"],
            padx=2,
            pady=4,
        )

        self.result_label = tk.Label(
            display_card,
            textvariable=self.result_var,
            anchor="e",
            font=("Bahnschrift SemiBold", 32),
            fg=self.palette["text"],
            bg=self.palette["display"],
            padx=2,
        )
        self.result_label.pack(fill="x", pady=(2, 0))
        self._update_expression_preview()

        self.accent_canvas = tk.Canvas(
            display_card,
            height=4,
            bg=self.palette["display"],
            bd=0,
            highlightthickness=0,
        )
        self.accent_canvas.pack(fill="x", pady=(8, 0))
        self.accent_bar = self.accent_canvas.create_rectangle(0, 0, 80, 4, fill=self.palette["accent"], width=0)

        keyboard_root = tk.Frame(self, bg=self.palette["panel"])
        keyboard_root.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        all_rows = [
            [self.mode_var.get(), "sin", "cos", "tan", "ln", "log"],
            ["(", ")", "sqrt", "x^2", "x^y", "1/x"],
            ["PI", "E", "abs", "!", "%", "DEL"],
            ["C", "7", "8", "9", "/", "*"],
            ["ANS", "4", "5", "6", "-", "+"],
            ["+/-", "1", "2", "3", ".", "="],
            ["00", "0", "asin", "acos", "atan", "exp"],
        ]

        self._build_button_grid(keyboard_root, all_rows)

    def _build_button_grid(self, parent: tk.Frame, rows: list[list[str]]) -> None:
        total_columns = max(len(row) for row in rows)
        for col_index in range(total_columns):
            parent.grid_columnconfigure(col_index, weight=1, uniform="key-col", minsize=48)

        for row_index, row in enumerate(rows):
            parent.grid_rowconfigure(row_index, weight=1, uniform="key-row", minsize=48)
            for col_index, label in enumerate(row):
                role = self._resolve_role(label)
                button = self._create_button(parent, label, role)
                button.grid(row=row_index, column=col_index, sticky="nsew", padx=3, pady=3)

    def _resolve_role(self, label: str) -> str:
        if label == "=":
            return "equals"
        if label in {"C", "DEL"}:
            return "danger"
        if label in {"+", "-", "*", "/", "%", "x^y"}:
            return "operator"
        if label in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "00", "."}:
            return "digit"
        return "function"

    def _create_button(self, parent: tk.Widget, label: str, role: str) -> tk.Button:
        style_map = {
            "digit": ButtonStyle(
                self.palette["digit"],
                self._blend_hex(self.palette["digit"], "#FFFFFF", 0.16),
                self._blend_hex(self.palette["digit"], "#000000", 0.16),
                self.palette["text"],
            ),
            "operator": ButtonStyle(
                self.palette["operator"],
                self._blend_hex(self.palette["operator"], "#FFFFFF", 0.18),
                self._blend_hex(self.palette["operator"], "#000000", 0.18),
                self.palette["text"],
            ),
            "function": ButtonStyle(
                self.palette["function"],
                self._blend_hex(self.palette["function"], "#FFFFFF", 0.14),
                self._blend_hex(self.palette["function"], "#000000", 0.16),
                self.palette["text"],
            ),
            "danger": ButtonStyle(
                self.palette["danger"],
                self._blend_hex(self.palette["danger"], "#FFFFFF", 0.16),
                self._blend_hex(self.palette["danger"], "#000000", 0.20),
                self.palette["text"],
            ),
            "equals": ButtonStyle(
                self.palette["equals"],
                self._blend_hex(self.palette["equals"], "#FFFFFF", 0.20),
                self._blend_hex(self.palette["equals"], "#000000", 0.20),
                "#FFFFFF",
            ),
        }
        style = style_map[role]
        initial_bg = self._blend_hex(self.palette["bg"], style.base, 0.22)
        initial_fg = self._blend_hex(self.palette["bg"], style.fg, 0.06)

        button = tk.Button(
            parent,
            text=label,
            bd=0,
            relief="flat",
            font=("Bahnschrift SemiBold", 12),
            bg=initial_bg,
            fg=initial_fg,
            activebackground=style.hover,
            activeforeground=style.fg,
            cursor="hand2",
            padx=3,
            pady=4,
            command=lambda value=label: self._on_button_click(value),
        )
        button.bind("<Enter>", lambda _event, btn=button: self._on_button_enter(btn))
        button.bind("<Leave>", lambda _event, btn=button: self._on_button_leave(btn))
        button.bind("<ButtonPress-1>", lambda _event, btn=button: self._on_button_press(btn))
        button.bind("<ButtonRelease-1>", lambda _event, btn=button: self._on_button_release(btn))

        self._button_styles[button] = style
        self._animated_buttons.append(button)
        if label in {"RAD", "DEG"}:
            self.mode_button = button
        return button

    def _on_button_enter(self, button: tk.Button) -> None:
        style = self._button_styles[button]
        button.configure(bg=style.hover)

    def _on_button_leave(self, button: tk.Button) -> None:
        style = self._button_styles[button]
        button.configure(bg=style.base)

    def _on_button_press(self, button: tk.Button) -> None:
        style = self._button_styles[button]
        button.configure(bg=style.press)

    def _on_button_release(self, button: tk.Button) -> None:
        style = self._button_styles[button]
        button.configure(bg=style.hover if self._is_pointer_over(button) else style.base)

    def _is_pointer_over(self, widget: tk.Widget) -> bool:
        pointer_x = widget.winfo_pointerx() - widget.winfo_rootx()
        pointer_y = widget.winfo_pointery() - widget.winfo_rooty()
        return 0 <= pointer_x < widget.winfo_width() and 0 <= pointer_y < widget.winfo_height()

    def _run_intro_animation(self) -> None:
        for index, button in enumerate(self._animated_buttons):
            self.after(30 * index, lambda btn=button: self._animate_button_reveal(btn))
        self._animate_accent_bar()

    def _animate_button_reveal(self, button: tk.Button) -> None:
        style = self._button_styles[button]
        for step in range(7):
            ratio = (step + 1) / 7
            bg = self._blend_hex(self.palette["bg"], style.base, ratio)
            fg = self._blend_hex(self.palette["bg"], style.fg, ratio)
            self.after(
                step * 16,
                lambda current_button=button, current_bg=bg, current_fg=fg: current_button.configure(
                    bg=current_bg,
                    fg=current_fg,
                ),
            )

    def _animate_accent_bar(self) -> None:
        width = self.accent_canvas.winfo_width()
        if width <= 1:
            self.after(60, self._animate_accent_bar)
            return

        self._accent_position = (self._accent_position + 9) % (width + 120)
        x2 = self._accent_position
        x1 = x2 - 120
        self.accent_canvas.coords(self.accent_bar, x1, 0, x2, 4)
        self.after(35, self._animate_accent_bar)

    def _flash_result(self, success: bool) -> None:
        start_color = self.palette["accent"] if success else "#E56B7E"
        for step in range(9):
            ratio = step / 8
            color = self._blend_hex(start_color, self.palette["text"], ratio)
            self.after(step * 24, lambda current=color: self.result_label.configure(fg=current))

    def _shake_window(self) -> None:
        geometry = self.geometry()
        match = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geometry)
        if not match:
            return

        width, height, x_pos, y_pos = map(int, match.groups())
        offsets = [0, 8, -8, 6, -6, 4, -4, 0]
        for frame_index, offset in enumerate(offsets):
            self.after(
                frame_index * 20,
                lambda frame_offset=offset: self.geometry(
                    f"{width}x{height}+{x_pos + frame_offset}+{y_pos}"
                ),
            )

    def _bind_keys(self) -> None:
        self.bind("<Key>", self._on_key)

    def _on_key(self, event: tk.Event) -> None:
        key = event.keysym
        char = event.char

        if key in {"Return", "KP_Enter"}:
            self._evaluate()
            return
        if key == "BackSpace":
            self._backspace()
            return
        if key == "Escape":
            self._clear()
            return
        if char in "0123456789.+-*/()%":
            self._append(char)
            return
        if char in {"(", ")"}:
            self._append(char)
            return
        if char == "^":
            self._append("**")

    def _on_button_click(self, value: str) -> None:
        if value == "C":
            self._clear()
            return
        if value == "DEL":
            self._backspace()
            return
        if value == "=":
            self._evaluate()
            return
        if value in {"RAD", "DEG"}:
            self._toggle_angle_mode()
            return
        if value == "+/-":
            self._toggle_sign()
            return
        if value == "ANS":
            self._append("ans")
            return
        if value == "PI":
            self._append("pi")
            return
        if value == "E":
            self._append("e")
            return
        if value in {"sin", "cos", "tan", "asin", "acos", "atan", "ln", "log", "sqrt", "abs", "exp"}:
            self._append(f"{value}(")
            return
        if value == "x^2":
            self._append("**2")
            return
        if value == "x^y":
            self._append("**")
            return
        if value == "1/x":
            self._append("1/(")
            return
        self._append(value)

    def _toggle_angle_mode(self) -> None:
        self.is_radian_mode = not self.is_radian_mode
        mode = "RAD" if self.is_radian_mode else "DEG"
        self.mode_var.set(mode)
        self.mode_button.configure(text=mode)

    def _toggle_sign(self) -> None:
        expression = self.expression_var.get().strip()
        if not expression:
            self.expression_var.set("-")
            self._update_expression_preview()
            return

        if expression.startswith("-(") and expression.endswith(")"):
            self.expression_var.set(expression[2:-1])
        else:
            self.expression_var.set(f"-({expression})")
        self._update_expression_preview()

    def _append(self, value: str) -> None:
        self.expression_var.set(f"{self.expression_var.get()}{value}")
        self._update_expression_preview()

    def _clear(self) -> None:
        self.expression_var.set("")
        self.result_var.set("0")
        self._update_expression_preview()

    def _backspace(self) -> None:
        self.expression_var.set(self.expression_var.get()[:-1])
        self._update_expression_preview()

    def _evaluate(self) -> None:
        expression = self.expression_var.get().strip()
        if not expression:
            return

        try:
            normalized = self._rewrite_factorials(expression)
            result = self._safe_eval(normalized)
            if not math.isfinite(result):
                raise ValueError("Result is out of range")

            self.last_answer = result
            formatted = self._format_result(result)
            self.result_var.set(formatted)
            self.expression_var.set(formatted)
            self._update_expression_preview()
            self._flash_result(success=True)
        except ZeroDivisionError:
            self._show_error("Cannot divide by zero.")
        except ValueError as err:
            self._show_error(str(err) or "Invalid expression.")
        except Exception:
            self._show_error("Invalid expression.")

    def _show_error(self, message: str) -> None:
        self.result_var.set("Error")
        self._flash_result(success=False)
        self._shake_window()
        messagebox.showerror("Calculation Error", message)

    def _format_result(self, value: float) -> str:
        if abs(value - round(value)) < 1e-12:
            return str(int(round(value)))
        if abs(value) >= 1e12 or (0 < abs(value) < 1e-9):
            return f"{value:.10e}"
        return f"{value:.12f}".rstrip("0").rstrip(".")

    def _should_show_expression_preview(self, expression: str) -> bool:
        cleaned = expression.strip()
        if not cleaned:
            return False
        if cleaned in {"+", "-", ".", "+.", "-."}:
            return False

        # Hide the preview for plain numeric inputs/results to avoid duplicate lines.
        if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", cleaned):
            return False
        if cleaned.lower() in {"pi", "e", "ans"}:
            return False
        return True

    def _update_expression_preview(self) -> None:
        expression = self.expression_var.get()
        if self._should_show_expression_preview(expression):
            self.expression_label.configure(text=expression)
            if not self._expression_label_visible:
                self.expression_label.pack(fill="x", before=self.result_label)
                self._expression_label_visible = True
        else:
            self.expression_label.configure(text="")
            if self._expression_label_visible:
                self.expression_label.pack_forget()
                self._expression_label_visible = False

    def _rewrite_factorials(self, expression: str) -> str:
        rewritten = expression.replace(" ", "")
        marker = rewritten.find("!")

        while marker != -1:
            if marker == 0:
                raise ValueError("Factorial is missing an operand")
            start = self._factorial_operand_start(rewritten, marker - 1)
            operand = rewritten[start:marker]
            rewritten = f"{rewritten[:start]}fact({operand}){rewritten[marker + 1:]}"
            marker = rewritten.find("!")
        return rewritten

    def _factorial_operand_start(self, expression: str, end_index: int) -> int:
        if expression[end_index] == ")":
            depth = 1
            cursor = end_index - 1
            while cursor >= 0:
                if expression[cursor] == ")":
                    depth += 1
                elif expression[cursor] == "(":
                    depth -= 1
                    if depth == 0:
                        break
                cursor -= 1
            if depth != 0:
                raise ValueError("Unbalanced parentheses")

            name_cursor = cursor - 1
            while name_cursor >= 0 and (expression[name_cursor].isalnum() or expression[name_cursor] == "_"):
                name_cursor -= 1
            return name_cursor + 1

        cursor = end_index
        while cursor >= 0 and (expression[cursor].isalnum() or expression[cursor] in {".", "_"}):
            cursor -= 1

        if cursor == end_index:
            raise ValueError("Factorial has an invalid operand")
        return cursor + 1

    def _safe_eval(self, expression: str) -> float:
        node = ast.parse(expression, mode="eval")

        binary_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
        }
        unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
        }

        functions = {
            "sin": self._sin,
            "cos": self._cos,
            "tan": self._tan,
            "asin": self._asin,
            "acos": self._acos,
            "atan": self._atan,
            "sqrt": math.sqrt,
            "abs": abs,
            "exp": math.exp,
            "ln": math.log,
            "log": self._log,
            "fact": self._factorial,
        }
        constants = {
            "pi": math.pi,
            "e": math.e,
            "ans": self.last_answer,
        }

        def _eval(current: ast.AST) -> float:
            if isinstance(current, ast.Expression):
                return _eval(current.body)

            if isinstance(current, ast.BinOp):
                op_type = type(current.op)
                if op_type not in binary_ops:
                    raise ValueError("Unsupported operator")
                return float(binary_ops[op_type](_eval(current.left), _eval(current.right)))

            if isinstance(current, ast.UnaryOp):
                op_type = type(current.op)
                if op_type not in unary_ops:
                    raise ValueError("Unsupported unary operator")
                return float(unary_ops[op_type](_eval(current.operand)))

            if isinstance(current, ast.Call):
                if not isinstance(current.func, ast.Name):
                    raise ValueError("Invalid function call")
                function_name = current.func.id
                if function_name not in functions:
                    raise ValueError(f"Unsupported function: {function_name}")
                if current.keywords:
                    raise ValueError("Keyword arguments are not supported")
                arguments = [_eval(arg) for arg in current.args]
                return float(functions[function_name](*arguments))

            if isinstance(current, ast.Name):
                if current.id not in constants:
                    raise ValueError(f"Unknown symbol: {current.id}")
                return float(constants[current.id])

            if isinstance(current, ast.Constant):
                if isinstance(current.value, bool) or not isinstance(current.value, (int, float)):
                    raise ValueError("Only numeric constants are allowed")
                return float(current.value)

            raise ValueError("Invalid expression")

        return _eval(node)

    def _angle_input(self, value: float) -> float:
        return value if self.is_radian_mode else math.radians(value)

    def _angle_output(self, value: float) -> float:
        return value if self.is_radian_mode else math.degrees(value)

    def _sin(self, value: float) -> float:
        return math.sin(self._angle_input(value))

    def _cos(self, value: float) -> float:
        return math.cos(self._angle_input(value))

    def _tan(self, value: float) -> float:
        return math.tan(self._angle_input(value))

    def _asin(self, value: float) -> float:
        return self._angle_output(math.asin(value))

    def _acos(self, value: float) -> float:
        return self._angle_output(math.acos(value))

    def _atan(self, value: float) -> float:
        return self._angle_output(math.atan(value))

    def _log(self, *args: float) -> float:
        if len(args) == 1:
            return math.log10(args[0])
        if len(args) == 2:
            return math.log(args[0], args[1])
        raise ValueError("log expects one or two arguments")

    def _factorial(self, value: float) -> float:
        rounded = round(value)
        if abs(value - rounded) > 1e-10:
            raise ValueError("Factorial requires an integer")
        if rounded < 0:
            raise ValueError("Factorial requires a non-negative integer")
        return float(math.factorial(int(rounded)))

    def _blend_hex(self, start_hex: str, end_hex: str, ratio: float) -> str:
        ratio = max(0.0, min(1.0, ratio))
        start_rgb = self._hex_to_rgb(start_hex)
        end_rgb = self._hex_to_rgb(end_hex)
        mixed = tuple(
            int(start_channel + (end_channel - start_channel) * ratio)
            for start_channel, end_channel in zip(start_rgb, end_rgb)
        )
        return f"#{mixed[0]:02X}{mixed[1]:02X}{mixed[2]:02X}"

    @staticmethod
    def _hex_to_rgb(color: str) -> tuple[int, int, int]:
        cleaned = color.lstrip("#")
        return int(cleaned[0:2], 16), int(cleaned[2:4], 16), int(cleaned[4:6], 16)


if __name__ == "__main__":
    app = ScientificCalculator()
    app.mainloop()
