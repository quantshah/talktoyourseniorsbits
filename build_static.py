import pandas as pd
import json
import os
from pathlib import Path

# URLs (Consider using environment variables in a real CI/CD setup)
# Ensure these GIDs point to the correct sheets
TESTIMONIALS_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1jVwCFKq-65EZOmSI12WVt1ol6RVTnFuLXCI5jObsnNs/export?format=csv&gid=1091959874"
SENIORS_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1jVwCFKq-65EZOmSI12WVt1ol6RVTnFuLXCI5jObsnNs/export?format=csv&gid=1091959874" # Adjust GID if seniors are on a different tab
GOOGLE_SIGN_UP_FORM = "https://forms.gle/7zrNwL6mxYjmYfBeA"
OUTPUT_DIR = "docs" # Directory for GitHub Pages
SENIOR_EMAIL_COLUMN = "Email" # Ensure this matches the column header in your sheet
SENIOR_LINKEDIN_COLUMN = "LinkedIn" # Column containing LinkedIn profile URLs

# --- Fetching Functions ---

def fetch_testimonials():
    """Fetches and cleans testimonials."""
    try:
        df = pd.read_csv(TESTIMONIALS_SHEET_CSV)
        testimonials = []
        for _, row in df.iterrows():
            story = str(row.get("Your story", "")).strip()
            bits_id = str(
                row.get("Batch, branch, year (BITS ID says it all)", "")
            ).strip()
            if story and story.lower() != "nan":
                testimonials.append({"story": story, "bits_id": bits_id})
        print(f"Successfully fetched {len(testimonials)} testimonials.")
        return testimonials
    except Exception as e:
        print(f"Error fetching testimonials: {e}")
        return [{"story": "Unable to load stories at the moment.", "bits_id": ""}]

def fetch_seniors():
    """Fetches and cleans senior email addresses and LinkedIn links."""
    try:
        df = pd.read_csv(SENIORS_SHEET_CSV)
        if SENIOR_EMAIL_COLUMN not in df.columns:
             print(f"Error: Column '{SENIOR_EMAIL_COLUMN}' not found in the seniors sheet.")
             return []
             
        # Get rows with valid emails
        valid_rows = df[df[SENIOR_EMAIL_COLUMN].notna() & 
                        df[SENIOR_EMAIL_COLUMN].astype(str).str.contains('@', na=False)]
        
        # Create a list of senior info dictionaries
        seniors = []
        for _, row in valid_rows.iterrows():
            email = str(row.get(SENIOR_EMAIL_COLUMN, "")).strip()
            
            # Get LinkedIn if available
            linkedin = ""
            if SENIOR_LINKEDIN_COLUMN in df.columns:
                linkedin_val = row.get(SENIOR_LINKEDIN_COLUMN, "")
                if linkedin_val and str(linkedin_val).lower() != "nan":
                    linkedin = str(linkedin_val).strip()
            
            if email:  # Only add if there's a valid email
                seniors.append({"email": email, "linkedin": linkedin})
        
        print(f"Successfully fetched {len(seniors)} unique senior profiles.")
        return seniors
    except Exception as e:
        print(f"Error fetching senior data: {e}")
        return []

# --- HTML Generation Functions ---

def generate_index_html(template_content, testimonials, output_path):
    """Generates index.html from the template and data."""
    # Basic templating: Replace placeholders
    
    # 1. Embed testimonials as JSON
    testimonials_json = json.dumps(testimonials)
    content = template_content.replace("{{ testimonials | tojson }}", testimonials_json)
    
    # 2. Replace sign-up link
    content = content.replace("{{ sign_up_link }}", GOOGLE_SIGN_UP_FORM)

    # 3. Statically generate the 'Talk to a Senior' link
    #    Remove the conditional tags and replace the placeholder link
    content = content.replace("            {% if talk_form_link %}\n", "") # Remove opening tag line
    content = content.replace(
        '            <a href="{{ talk_form_link }}">Talk to a Senior</a>\n',
        '            <a href="talk.html">Talk to a Senior</a>\n'
    ) # Replace link line
    content = content.replace("            {% endif %}\n", "") # Remove closing tag line
            
    # 4. Adjust static paths (assuming static/ is at the root with index.html)
    content = content.replace('url("/static/', 'url("static/')

    # 5. Adjust "See All" link
    content = content.replace('href="/all"', 'href="all.html"')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated {output_path}")

def generate_all_html(testimonials, output_path):
    """Generates all.html to display all testimonials."""
    list_items = ""
    if testimonials and testimonials[0]['story'] != "Unable to load stories at the moment.":
        for t in testimonials:
            story = t.get('story', 'No story provided')
            author = f"- {t['bits_id']}" if t.get('bits_id') else ""
            list_items += f"<li><p>{story}</p><small>{author}</small></li>\n"
    else:
         list_items = "<li><p>Unable to load stories at the moment.</p></li>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>All Stories - BITS Mental Health</title>
    <style>
        body {{ 
            margin: 0;
            font-family: sans-serif;
            background: url("static/images/background.png") no-repeat center center fixed;
            background-size: cover;
            color: white;
            text-align: center;
            min-height: 100vh;
            position: relative;
        }}
        
        .overlay {{
            background-color: rgba(0, 0, 0, 0.5);
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
            overflow-y: auto;
        }}
        
        h1 {{ text-align: center; color: #ffffff; margin-bottom: 20px; }}
        ul {{ 
            list-style: none; 
            padding: 0; 
            max-width: 800px; 
            margin: 20px auto; 
            width: 90%;
        }}
        li {{ 
            background-color: rgba(30, 30, 30, 0.8); 
            border: 1px solid #333; 
            border-radius: 8px; 
            margin-bottom: 15px; 
            padding: 15px 20px;
            text-align: left;
        }}
        p {{ margin: 0 0 5px 0; }}
        small {{ color: #aaaaaa; display: block; text-align: right; }}
        a {{ color: #bb86fc; }}
        .back-link {{ display: block; text-align: center; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="overlay">
        <h1>All Stories</h1>
        <ul>
            {list_items}
        </ul>
        <div class="back-link">
            <a href="index.html">Back to Home</a>
        </div>
    </div>
</body>
</html>"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated {output_path}")

def generate_talk_html(template_content, seniors_list, output_path):
    """Generates talk.html, embedding the senior email list as JSON."""
    # Convert the list of emails to a JSON string suitable for embedding in JS
    seniors_json = json.dumps(seniors_list) 
    
    # Replace a placeholder in the template with the JSON string
    # Ensure the placeholder {{ seniors_json }} exists in templates/talk.html
    content = template_content.replace("{{ seniors_json }}", seniors_json)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated {output_path} with {len(seniors_list)} senior emails embedded")


# --- Main Execution ---

if __name__ == "__main__":
    # Ensure output directory exists
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Ensure template directory exists (or handle error)
    template_dir = Path("templates")
    if not template_dir.is_dir():
        print(f"Error: Template directory '{template_dir}' not found.")
        exit(1)

    # Copy static assets
    static_dir_src = Path("static")
    static_dir_dest = output_path / "static"
    if static_dir_src.exists() and static_dir_src.is_dir():
        if not static_dir_dest.exists():
             static_dir_dest.mkdir(parents=True, exist_ok=True)
             print(f"Copying static assets to {static_dir_dest}...")
             # Basic copy (adjust if subdirectories exist in static/)
             copied_count = 0
             for item in static_dir_src.iterdir():
                  if item.is_file():
                       (static_dir_dest / item.name).write_bytes(item.read_bytes())
                       copied_count += 1
             print(f"Copied {copied_count} static file(s).")
        else:
             print("Static assets directory already exists in output.")
    else:
         print("Warning: Source static directory not found, skipping copy.")


    # Fetch data
    all_testimonials = fetch_testimonials()
    all_seniors = fetch_seniors() # Fetch the list of senior emails

    # --- Read Templates ---
    try:
        with open(template_dir / "index.html", 'r', encoding='utf-8') as f:
            index_template = f.read()
    except FileNotFoundError:
        print(f"Error: {template_dir / 'index.html'} not found.")
        exit(1)
        
    try:
        with open(template_dir / "talk.html", 'r', encoding='utf-8') as f:
            talk_template = f.read()
    except FileNotFoundError:
        print(f"Error: {template_dir / 'talk.html'} not found. Create this template file.")
        # Decide if you want to exit or continue without talk.html
        talk_template = None # Or exit(1)
        

    # --- Generate HTML Files ---
    generate_index_html(index_template, all_testimonials, output_path / "index.html")
    generate_all_html(all_testimonials, output_path / "all.html")
    
    if talk_template:
        generate_talk_html(talk_template, all_seniors, output_path / "talk.html")
    else:
        print("Skipping talk.html generation due to missing template.")


    print("\nStatic site generation complete.")
    print(f"Output files are in the '{output_path}' directory.")
