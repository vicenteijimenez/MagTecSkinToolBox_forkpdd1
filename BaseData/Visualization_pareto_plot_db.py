# -*- coding: utf-8 -*-
"""
Created on Tue May 4 09:29:11 2026
@author: benjamin
@updated: Auto-detect inner study names and force file-system writes
"""

import optuna
import plotly.graph_objects as go
import os
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def load_study_automatically(db_path: str) -> optuna.study.Study:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file absolutely missing at: {db_path}")

    storage_url = f"sqlite:///{db_path}"
    
    # 1. Query the database engine to see what studies it actually holds
    try:
        summaries = optuna.study.get_all_study_summaries(storage=storage_url)
    except Exception as e:
        raise RuntimeError(f"Could not read the SQLite structure: {e}")

    if not summaries:
        raise ValueError(f"The file exists, but it contains 0 Optuna studies. It might be blank or pending initial writes.")

    # 2. Grab the first active study name found inside the DB file dynamically
    detected_study_name = summaries[0].study_name
    logging.info(f"-> Found internal study named: '{detected_study_name}'")
    
    study = optuna.load_study(study_name=detected_study_name, storage=storage_url)
    logging.info(f"-> Successfully extracted {len(study.trials)} iterations/trials.")
    
    return study

def extract_pareto_points(study: optuna.study.Study) -> Tuple[List[List[float]], List[List[float]]]:
    # We look for any completed trials instead of filtering strictly to avoid empty arrays
    completed_trials = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
    
    if not completed_trials:
        raise ValueError("Database has trials, but 0 of them have status 'COMPLETE' yet.")

    pareto_trials = study.best_trials
    pareto_ids = {t.number for t in pareto_trials}

    pareto_points = []
    dominated_points = []

    for trial in completed_trials:
        if trial.values is None:
            continue
        if trial.number in pareto_ids:
            pareto_points.append(trial.values)
        else:
            dominated_points.append(trial.values)

    return pareto_points, dominated_points

def plot_pareto(pareto_points, dominated_points, study_name: str, output_file: str):
    dim = len(pareto_points[0])
    fig = go.Figure()

    if dim == 2:
        if dominated_points:
            x, y = zip(*dominated_points)
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers', marker=dict(size=5, color='blue', opacity=0.6), name='Dominated'))
        if pareto_points:
            x, y = zip(*pareto_points)
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers', marker=dict(size=7, color='red'), name='Pareto Front'))
        fig.update_layout(title=f"Pareto Space: {study_name}", xaxis_title='Objective 1', yaxis_title='Objective 2')
    elif dim == 3:
        if dominated_points:
            x, y, z = zip(*dominated_points)
            fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=4, color='blue', opacity=0.6), name='Dominated'))
        if pareto_points:
            x, y, z = zip(*pareto_points)
            fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=6, color='yellow'), name='Pareto Front'))
        fig.update_layout(title=f"Pareto Space: {study_name}", scene=dict(xaxis_title='Obj 1', yaxis_title='Obj 2', zaxis_title='Obj 3'))
    else:
        raise NotImplementedError(f"Plots only support 2D or 3D datasets. Found dimensions: {dim}")

    fig.write_html(output_file)
    print(f"\n[SUCCESS] Interactive plot generated and forced out to: {output_file}\n")

def main():
    db_path = "/home/vicenteijimenez/pd1/MagTecSkinToolBox_forkpdd1/Applications/OptimizationResults/SensorFinger/SensorFinger_0_optuna_evolutionary.db"
    output_html = "/home/vicenteijimenez/pd1/MagTecSkinToolBox_forkpdd1/BaseData/sensor_finger_pareto.html"

    print("\n--- Starting Optuna Extraction Diagnostic ---")
    try:
        study = load_study_automatically(db_path)
        pareto_points, dominated_points = extract_pareto_points(study)
        plot_pareto(pareto_points, dominated_points, study.study_name, output_html)
    except Exception as e:
        print(f"\n[CRASH ERROR] Pipeline execution stopped: {e}\n")

if __name__ == "__main__":
    main()