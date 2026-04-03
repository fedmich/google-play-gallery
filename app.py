# app.py
import os
import glob
import json
from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)

# Directory where JSON files are stored
# DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/android')
DATA_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data/android')


@app.route('/')
def index():
    # Glob all .json files in data/android/
    json_files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    apps = []

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract key fields
                app_id = data.get('appId', 'unknown')
                title = data.get('title', 'No Title')
                # 'icon' is usually the thumbnail
                thumbnail = data.get('icon', '')
                apps.append({
                    'id': app_id,
                    'title': title,
                    'thumbnail': thumbnail,
                    'file_path': file_path
                })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return render_template('index.html', apps=apps)


@app.route('/info/<app_id>')
def app_detail(app_id):
    file_path = os.path.join(DATA_DIR, f"{app_id}.json")
    if not os.path.exists(file_path):
        abort(404)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return render_template('detail.html', app=data)
    except Exception as e:
        abort(500, description="Error loading app data")

# Optional: Serve static files (e.g., images) if needed


@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory('static', filename)


@app.route('/save/<app_id>')
def save_app_data(app_id):
    from flask import jsonify
    import json
    from google_play_scraper import app as play_app
    from google_play_scraper import exceptions

    save_dir = os.path.join(os.path.dirname(__file__), 'data', 'android')
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{app_id}.json")

    try:
        # Fetch app data with timeout via retry + timeout-safe scraper
        result = play_app(app_id, lang='en', country='us')

        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "success", "message": f"Saved {app_id}", "file": file_path}), 200

    except exceptions.AppNotFoundError:
        return jsonify({"error": "App not found on Google Play"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to scrape app: {str(e)}"}), 500


@app.route('/add')
def add_form():
    return render_template('index.html', show_add_modal=True)


if __name__ == '__main__':
    app.run(debug=True)
