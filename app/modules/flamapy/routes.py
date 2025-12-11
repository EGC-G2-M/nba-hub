import logging
import csv
import re

from flask import jsonify

from app.modules.flamapy import flamapy_bp
from app.modules.hubfile.services import HubfileService

logger = logging.getLogger(__name__)


@flamapy_bp.route("/flamapy/check_csv/<int:file_id>", methods=["GET"])
def check_csv(file_id):
    expected_header = [
        "Name",
        "Height",
        "Age",
        "Games",
        "Points per game",
        "Assists per game",
        "Rebounds per game",
    ]
    errors = []
    try:
        hubfile = HubfileService().get_by_id(file_id)
        path = hubfile.get_path()
        height_re = re.compile(r"^\d+m\d{2}$")
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                return jsonify({"errors": ["Empty file"]}), 400
            header = [h.strip() for h in header]
            if len(header) < len(expected_header) or header[: len(expected_header)] != expected_header:
                errors.append(
                    f"Header mismatch. Expected: {', '.join(expected_header)}. Found: {', '.join(header)}"
                )
            line_no = 1 
            for row in reader:
                line_no += 1
                if not any(cell.strip() for cell in row):
                    continue
                if len(row) < len(expected_header):
                    errors.append(
                        f"Line {line_no}: expected {len(expected_header)} columns, found {len(row)}"
                    )
                    continue

                name = row[0].strip()
                height = row[1].strip()
                age = row[2].strip()
                games = row[3].strip()
                points = row[4].strip()
                assists = row[5].strip()
                rebounds = row[6].strip()

                if not name:
                    errors.append(f"Line {line_no}: Name is empty")

                if not height_re.match(height):
                    errors.append(
                        f"Line {line_no}: Height '{height}' does not match pattern e.g. '1m95'"
                    )
                for field_name, value in (("Age", age), ("Games", games)):
                    if field_name == "Age" and value == "":
                        continue
                    try:
                        int(value)
                    except Exception:
                        errors.append(
                            f"Line {line_no}: {field_name} '{value}' is not a valid integer"
                        )

                # Float fields
                for field_name, value in (
                    ("Points per game", points),
                    ("Assists per game", assists),
                    ("Rebounds per game", rebounds),
                ):
                    try:
                        float(value)
                    except Exception:
                        errors.append(
                            f"Line {line_no}: {field_name} '{value}' is not a valid number"
                        )

        if errors:
            return jsonify({"errors": errors}), 400

        return jsonify({"message": "Valid CSV file"}), 200

    except Exception as e:
        logger.exception("Error comprobando CSV")
        return jsonify({"error": str(e)}), 500


@flamapy_bp.route("/flamapy/valid/<int:file_id>", methods=["GET"])
def valid(file_id):
    return jsonify({"success": True, "file_id": file_id})
