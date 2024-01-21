from flask import Flask, render_template, request
import git_analysis
import json
import pandas as pd
import plotly.express as px
import os  # Import the os module for file existence check

app = Flask(__name__)

# Check if config.json exists
config_file_path = 'config.json'
config = None

if os.path.exists(config_file_path):
    with open(config_file_path) as config_file:
        config = json.load(config_file)

def create_heatmap(data, title, xaxis_title, yaxis_title):
    fig = px.density_heatmap(data, x='x_column', y='y_column', z='z_column', title=title)
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_repo = None
    recent_days = config.get('default_recent_days', 30)

    if request.method == 'POST':
        selected_repo = request.form.get('repo_path')
        recent_days = int(request.form.get('recent_days', recent_days))

    repo_paths = config.get('repositories', [])  # Use an empty list if 'repositories' is not found in config

    if config is None:  # Check if config is not loaded (config.json not found)
        return render_template('index.html', error_message='config.json not found')

    results = {}

    for repo_path in repo_paths:
        if selected_repo and repo_path != selected_repo:
            continue
        file_commit_age, file_change_frequency = git_analysis.analyze_git_repo(repo_path, recent_days)

        # Convert data to Pandas DataFrame
        df_age = pd.DataFrame(list(file_commit_age.items()), columns=['File', 'Days Since Last Commit'])
        df_frequency = pd.DataFrame(list(file_change_frequency.items()), columns=['File', 'Commit Frequency'])

        heatmap_age = create_heatmap(df_age, "File Commit Age", "File", "Days Since Last Commit")
        heatmap_frequency = create_heatmap(df_frequency, "File Change Frequency", "File", "Commit Frequency")

        results[repo_path] = (heatmap_age, heatmap_frequency, file_commit_age, file_change_frequency)

    return render_template('index.html', results=results, repo_paths=repo_paths, selected_repo=selected_repo)

if __name__ == '__main__':
    app.run(debug=True)
