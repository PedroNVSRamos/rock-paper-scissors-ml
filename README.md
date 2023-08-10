# Relationship Visualization Tool

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contribution](#contribution)

## Overview

This tool provides a visual representation of relationships among different entities. Built with Python, leveraging the capabilities of the NetworkX library for relationship graph generation, and Dash by Plotly for an interactive web visualization.

## Features

- **Interactive Web Interface**: Easily input relationships through a user-friendly interface.
- **Color-coded relationshops**: Relationships are color-coded based on their type (buff or debuff).
- **IMages**: Images are assigned to nodes (Heroes and targets) to make them self explanatory. In addition, the relationships also are portrayed with their own image (Artifact icons).

## Installation

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/PedroNVSRamos/rock-paper-scissors-ml
    ```

2. **Navigate to the Project Directory**:

    ```bash
    cd path-to-your-project-directory
    ```

3. **Install Required Packages**:

    ```bash
    pip install -r requirements.txt
    ```

> Ensure you have Python 3.7 or above installed.

## Usage

1. Map the participants and the relationships, using the respective files:
 - `heroes.csv` maps all different heroes, as well as the artifacts they get assigned, and what level the Artifacts unlock and how many tiers each Artifact is quipped with; 
 - `artifacts.csv` maps the relationships between the subject Heroes and their targets (Classes or Origins) when using the equipped Artifacts. 
 For rebalancing purposes, just edit both files preserving the existing structure.

2. **Run the Application**:

    ```bash
    python relationships.py
    ```

3. Open your preferred web browser and navigate to:
   
    ```
    http://127.0.0.1:8050/
    ```

4. Input your relationships and see them visualized in real-time!

## Contribution

Got ideas or bug reports? We welcome contributions! Please fork the repository and create a pull request with your changes.
