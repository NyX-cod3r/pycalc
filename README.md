# Animated Scientific Calculator

A Samsung-style scientific calculator desktop app built with Python and Tkinter.

## Features

- High-contrast dark calculator layout inspired by modern phone calculators
- Staggered button reveal on startup
- Moving accent sweep below the display
- Button press and hover color transitions
- Result flash animation on successful/error evaluation
- Error shake feedback on invalid operations
- Scientific functions: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
- Scientific functions: `ln`, `log`, `sqrt`, `exp`, `abs`, factorial (`!`)
- Constants and helpers: `PI`, `E`, `ANS`, `x^2`, `x^y`, `%`, `1/x`
- Angle mode toggle: `RAD` / `DEG`
- Safe AST-based parser and evaluator (no direct `eval`)
- Keyboard shortcuts: `Enter` to evaluate, `Backspace` to delete, `Esc` to clear
- Keyboard input: `0-9`, `+`, `-`, `*`, `/`, `%`, `.`, `(`, `)`, `^`

## Run

```bash
python calculator.py
```

## Requirements

- Python 3.9+
- Tkinter (usually included with standard Python installers)
