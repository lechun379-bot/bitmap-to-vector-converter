# CorelDRAW Macro Setup Guide

## 1) Prepare the Python script

Place `corel_vectorize.py` in a location like:

`C:\Users\<YourUser>\Desktop\corel_vectorize.py`

Then install dependencies:

```bash
python -m pip install opencv-python-headless pillow numpy
```

## 2) Add the CorelDRAW macro

Open CorelDRAW and run:

- Tools > Visual Basic > Create New Visual Basic Project
- Paste the contents of `corel_draw_macro.bas` into the editor
- Save the project

## 3) Run the macro

- Select a bitmap in CorelDRAW
- Run `ConvertBitmapToVector`
- The macro will export the bitmap to a temporary PNG, run the Python vectorizer, then import the generated SVG back into the document

## 4) Typical use cases

- Scan-to-vector conversion
- Tracing logos and icons
- Turning a bitmap into editable outlines in CorelDRAW

## 5) Tips for better results

- Use high-contrast PNGs whenever possible
- Remove background noise first
- If the result is too noisy, increase `--min-area`
- If the result loses too much detail, lower `--simplify` and `--min-area`

Example:

```bash
python corel_vectorize.py input.png output.svg --threshold 160 --blur 2 --min-area 5 --simplify 0.002 --adaptive --bezier --curves
```
