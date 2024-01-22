from flask import Flask, render_template, request, redirect, url_for, session
import git_analysis
import json
import pandas as pd
import plotly.express as px
import os
import logging
import plotly



app = Flask(__name__)
app.secret_key = 'difficult to guess key'

def create_heatmap(data, title, xaxis_title, yaxis_title):
    fig = px.density_heatmap(data, x=xaxis_title, y=yaxis_title, title=title)
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

def create_bar_chart(data, title, xaxis_title, yaxis_title):
    #data_sorted = data.sort_values(by=yaxis_title, ascending=False)
    fig = px.bar(data, x=xaxis_title, y=yaxis_title, title=title)
    return fig

def load_config():
    config_file_path = 'config.json'
    config = None

    if os.path.exists(config_file_path):
        try:
            with open(config_file_path) as config_file:
                config = json.load(config_file)
        except Exception as e:
            pass  # Ignore invalid config

    return config

def process_input_data(repo_paths, recent_days, file_extensions, max_files):
    results = {}
    for repo_path in repo_paths:
        if not file_extensions:
            file_extensions = None  # Or keep it as an empty list based on how git_analysis.analyze_git_repo handles it
        # Analyze the Git repository for each path
        file_commit_age, file_change_frequency = git_analysis.analyze_git_repo(repo_path, recent_days, file_extensions)

        # Sort and process data for age and frequency
        sorted_age = dict(sorted(file_commit_age.items(), key=lambda item: item[1], reverse=False)[:max_files])
        sorted_frequency = dict(sorted(file_change_frequency.items(), key=lambda item: item[1], reverse=True)[:max_files])

        # Create dataframes for visualization
        df_age = pd.DataFrame(list(sorted_age.items()), columns=['File', 'Days Since Last Commit'])
        df_frequency = pd.DataFrame(list(sorted_frequency.items()), columns=['File', 'Commit Frequency'])

        # Generate visualizations
        heatmap_age = create_heatmap(df_age, "File Commit Age", "File", "Days Since Last Commit")
        heatmap_frequency = create_heatmap(df_frequency, "File Change Frequency", "File", "Commit Frequency")

        bar_chart_age = create_bar_chart(df_age, "File Commit Age", "Days Since Last Commit", "File")
        bar_chart_frequency = create_bar_chart(df_frequency, "File Change Frequency", "Commit Frequency", "File")

        # Save visualizations to static files
        #heatmap_age_path = f"static/heatmap_age_{repo_path.replace('/', '_')}.png"
        #heatmap_age_path = f"static/heatmap_age_{repo_path.replace('/', '_')}.png"
        #heatmap_frequency_path = f"static/heatmap_frequency_{repo_path.replace('/', '_')}.png"
        bar_chart_age_path = f"bar_chart_age_{repo_path.replace('/', '_')}.png"
        bar_chart_frequency_path = f"bar_chart_frequency_{repo_path.replace('/', '_')}.png"

        #heatmap_frequency.write_image(heatmap_frequency_path)
        bar_chart_age.write_image("static/" + bar_chart_age_path)
        bar_chart_frequency.write_image("static/" + bar_chart_frequency_path)

        # Store the paths and data for results
        results[repo_path] = {
            'bar_chart_age_path': bar_chart_age_path, 
            'bar_chart_frequency_path': bar_chart_frequency_path, 
            'sorted_age': sorted_age, 
            'sorted_frequency': sorted_frequency
        }
    return results


@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        new_config = request.form.get('new_config')
        try:
            config_data = json.loads(new_config)
            with open('config.json', 'w') as config_file:
                json.dump(config_data, config_file, indent=4)
            
            # Store the new configuration in the session
            session['config'] = config_data

            # Redirect to the results route indicating the source is from config
            return redirect(url_for('results', from_config=True))
        except json.JSONDecodeError:
            # Handle invalid JSON format
            return "Invalid JSON format", 400

    # Load existing configuration for display
    config = load_config()
    return render_template('config.html', config=config)

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Capture form data
        selected_repo = request.form.get('repo_path')
        recent_days = int(request.form.get('recent_days', 30))
        file_extensions_input = request.form.get('file_extensions', '')
        file_extensions = [ext.strip() for ext in file_extensions_input.split(',') if ext.strip()]
        max_files = int(request.form.get('max_files', 10))

        # Redirect to results route with form data
        return redirect(url_for('results', repo=selected_repo, days=recent_days, exts=file_extensions, max=max_files))
    
    # Render the form template for GET requests
    return render_template('form.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    
    return redirect(url_for('form'))

@app.route('/results')
def results():
    if 'from_config' in request.args:
        config = session.get('config', {})
        repo_paths = config.get('repositories', [])
        recent_days = config.get('recent_days', 30)
        file_extensions = config.get('file_extensions', [])
        max_files = config.get('max_files', 10)
    else:
        repo_paths = [request.args.get('repo', [])]
        recent_days = int(request.args.get('days', 30))
        file_extensions = request.args.getlist('exts')
        max_files = int(request.args.get('max', 10))

    results = process_input_data(repo_paths, recent_days, file_extensions, max_files)
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
