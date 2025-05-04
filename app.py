"""Simple Flask app to display testimonials and allow users to contact seniors."""

from flask import Flask, render_template, request, url_for
import pandas as pd
import random
import urllib.parse

app = Flask(__name__)

# URLs for Google Sheets and sign-up form
# TODO: Make these environment variables instead of hardcoding
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1jVwCFKq-65EZOmSI12WVt1ol6RVTnFuLXCI5jObsnNs/export?format=csv&gid=1091959874"
GOOGLE_SIGN_UP_FORM = "https://forms.gle/7zrNwL6mxYjmYfBeA"


@app.route("/")
def index():
    """Render the index page with testimonials."""
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV)
        testimonials = []

        # Randomly select a testimonial to show on the index page
        for _, row in df.iterrows():
            story = str(row.get("Your story", "")).strip()
            bits_id = str(
                row.get("Batch, branch, year (BITS ID says it all)", "")
            ).strip()
            if story and story.lower() != "nan":
                testimonials.append({"story": story, "bits_id": bits_id})
    except Exception as e:
        testimonials = [
            {"story": "Unable to load stories at the moment.", "bits_id": ""}
        ]

    return render_template(
        "index.html",
        testimonials=testimonials,
        sign_up_link=GOOGLE_SIGN_UP_FORM,
        talk_form_link=url_for("talk_to_senior"),
    )


@app.route("/all")
def all_stories():
    """Render the all stories page with all testimonials."""
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV)
        testimonials = []

        for _, row in df.iterrows():
            story = str(row.get("Your story", "")).strip()
            bits_id = str(
                row.get("Batch, branch, year (BITS ID says it all)", "")
            ).strip()
            if story:
                testimonials.append({"story": story, "bits_id": bits_id})
    except Exception as e:
        testimonials = [
            {"story": "Unable to load stories at the moment.", "bits_id": ""}
        ]
    return render_template("all.html", testimonials=testimonials)


@app.route("/talk", methods=["GET", "POST"])
def talk_to_senior():
    """Render the talk to senior form and handle form submission."""
    if request.method == "POST":
        user_email = request.form.get("email")
        message = request.form.get("message")

        try:
            df = pd.read_csv(GOOGLE_SHEET_CSV)
            df = df[
                [
                    "Name",
                    "Batch, branch, year (BITS ID says it all)",
                    "Email",
                    "LinkedIn Profile Link",
                    "Phone number or other ways to connect if not email (e.g.., to call up on WhatsApp, DM on LinkedIN etc)",
                ]
            ].dropna(subset=["Email"])

            # Sample three random entries to contact
            selected_rows = df.sample(min(3, len(df))).to_dict(orient="records")
        except Exception as e:
            print("Error loading seniors:", e)
            selected_rows = []

        # Extract emails for mailto
        emails = [
            row["Email"]
            for row in selected_rows
            if "@"
            in row.get(
                "Email",
                "",
            )
        ]

        subject = urllib.parse.quote("Talk to your senior from BITS")
        body = urllib.parse.quote(f"{message}\n\nReply to: {user_email}")
        mailto_link = "mailto:" + ",".join(emails) + f"?subject={subject}&body={body}"

        return render_template(
            "talk_result.html",
            email_link=mailto_link,
            selected=selected_rows,
            message=message,
            user_email=user_email,
            email_recipients=emails,
        )

    return render_template("talk_form.html")
