#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from typing import Dict

from flask import Flask, render_template, request, redirect, url_for, flash, send_file

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from contact_manager import ContactManager  # noqa: E402


def create_app() -> Flask:
    app = Flask(__name__, template_folder=str(CURRENT_DIR / "templates"), static_folder=str(CURRENT_DIR / "static"))
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

    data_file_env = os.environ.get("CONTACTS_JSON_PATH")
    manager = ContactManager(data_file=data_file_env or str(PROJECT_ROOT / "contacts.json"))

    @app.context_processor
    def inject_globals() -> Dict:
        return {"APP_NAME": "Contact Manager UI"}

    @app.get("/")
    def index():
        q = (request.args.get("q") or "").strip()
        contacts = manager.search_contacts(q) if q else manager.list_contacts()
        stats = manager.get_stats()
        return render_template("index.html", contacts=contacts, query=q, stats=stats)

    @app.post("/contacts")
    def create_contact():
        form = request.form
        try:
            manager.add_contact(
                name=(form.get("name") or "").strip(),
                email=(form.get("email") or "").strip(),
                phone=(form.get("phone") or "").strip(),
                company=(form.get("company") or "").strip(),
                address=(form.get("address") or "").strip(),
                notes=(form.get("notes") or "").strip(),
            )
            flash("Contact created", "success")
        except ValueError as e:
            flash(str(e), "danger")
        return redirect(url_for("index"))

    @app.get("/contacts/<int:contact_id>")
    def view_contact(contact_id: int):
        contact = manager.get_contact(contact_id)
        if not contact:
            flash("Contact not found", "danger")
            return redirect(url_for("index"))
        return render_template("detail.html", contact=contact)

    @app.post("/contacts/<int:contact_id>/update")
    def update_contact(contact_id: int):
        form = request.form
        updates = {k: (form.get(k) or "").strip() for k in ["name", "email", "phone", "company", "address", "notes"]}
        try:
            if not manager.update_contact(contact_id, **updates):
                flash("Contact not found", "danger")
            else:
                flash("Contact updated", "success")
        except ValueError as e:
            flash(str(e), "danger")
        return redirect(url_for("view_contact", contact_id=contact_id))

    @app.post("/contacts/<int:contact_id>/delete")
    def delete_contact(contact_id: int):
        if manager.delete_contact(contact_id):
            flash("Contact deleted", "warning")
        else:
            flash("Contact not found", "danger")
        return redirect(url_for("index"))

    @app.get("/export/<fmt>")
    def export(fmt: str):
        if fmt not in ("json", "csv"):
            flash("Unsupported export format", "danger")
            return redirect(url_for("index"))
        data = manager.export_contacts(fmt)
        out_path = CURRENT_DIR / f"contacts_export.{fmt}"
        out_path.write_text(data, encoding="utf-8")
        return send_file(str(out_path), as_attachment=True)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=True)

