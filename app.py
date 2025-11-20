import os
import json
from flask import Flask, render_template, send_from_directory, abort
from openpyxl import load_workbook
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

app = Flask(__name__)

def list_data_files():
    allowed = (".json", ".csv", ".xlsx", ".xls")
    files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(allowed)]
    files.sort()
    return files

def read_any_file(filepath):
    """Read JSON, CSV, or XLSX without pandas. Return list/dict or list of primitives."""
    _, ext = os.path.splitext(filepath.lower())
    full = os.path.join(DATA_DIR, filepath)

    if ext == ".json":
        with open(full, "r", encoding="utf-8") as f:
            data = json.load(f)
        # normalize dict -> list
        if isinstance(data, dict):
            # try to find a list value inside the dict
            list_values = [v for v in data.values() if isinstance(v, list)]
            if list_values:
                return list_values[0]
            return [data]
        return data

    elif ext == ".csv":
        rows = []
        with open(full, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # optional: convert numeric strings to numbers (simple)
                rows.append({k: try_parse_number(v) for k, v in row.items()})
        return rows

    elif ext in (".xls", ".xlsx"):
        wb = load_workbook(full, data_only=True)
        sheet = wb.active
        rows = list(sheet.rows)
        if not rows:
            return []
        # read header from first row
        headers = [cell.value if cell.value is not None else "" for cell in rows[0]]
        data = []
        for r in rows[1:]:
            values = [cell.value for cell in r]
            item = dict(zip(headers, values))
            data.append(item)
        return data

    else:
        raise ValueError("Unsupported file type")

def try_parse_number(value):
    """Try to convert strings to int/float if appropriate (keeps others unchanged)."""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return value
    s = str(value).strip()
    if s == "":
        return ""
    # try int
    try:
        i = int(s)
        return i
    except:
        pass
    # try float
    try:
        f = float(s)
        return f
    except:
        pass
    return s

@app.route("/")
def index():
    files = list_data_files()
    return render_template("index.html", files=files)

@app.route("/view/<path:filename>")
def view_file(filename):
    files = list_data_files()
    if filename not in files:
        abort(404, description="File not found")
    try:
        data = read_any_file(filename)
    except Exception as e:
        return render_template("view_table.html", filename=filename, error=str(e), data=None)

    # If data is list of dicts -> columns + records
    if isinstance(data, list) and data and isinstance(data[0], dict):
        columns = sorted({k for row in data for k in row.keys()})
        return render_template("view_table.html", filename=filename, data=data, columns=columns)

    # If single dict
    if isinstance(data, dict):
        columns = sorted(list(data.keys()))
        return render_template("view_table.html", filename=filename, data=[data], columns=columns)

    # list of primitives or empty list
    return render_template("view_table.html", filename=filename, data=data, columns=None)

@app.route("/json_keys/<path:filename>")
def json_keys(filename):
    files = list_data_files()
    if filename not in files:
        abort(404)
    _, ext = os.path.splitext(filename.lower())
    if ext != ".json":
        return render_template("view_json_keys.html", filename=filename, error="File bukan JSON", keys=None)
    full = os.path.join(DATA_DIR, filename)
    try:
        with open(full, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except Exception as e:
        return render_template("view_json_keys.html", filename=filename, error=str(e), keys=None)

    if isinstance(obj, list):
        if not obj:
            return render_template("view_json_keys.html", filename=filename, keys=[])
        if isinstance(obj[0], dict):
            keys = sorted({k for d in obj for k in d.keys()})
            return render_template("view_json_keys.html", filename=filename, keys=keys)
        else:
            return render_template("view_json_keys.html", filename=filename, keys=["(primitive list)"])
    elif isinstance(obj, dict):
        keys = sorted(list(obj.keys()))
        return render_template("view_json_keys.html", filename=filename, keys=keys)
    else:
        return render_template("view_json_keys.html", filename=filename, keys=["(unknown JSON top-level)"])

@app.route("/download/<path:filename>")
def download_file(filename):
    files = list_data_files()
    if filename not in files:
        abort(404)
    return send_from_directory(DATA_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)
    app.run(debug=True, port=5000)
