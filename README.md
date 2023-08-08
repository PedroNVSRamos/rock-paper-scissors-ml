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
- **Color-coded Nodes**: Entities are color-coded based on their type, ensuring clarity.
- **Curved Arrows**: Arrows are curved for better visualization and to prevent overlap.
- **Adaptive Coloring**: Arrow and label colors adjust based on the object of the relationship.

## Installation

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/PedroNVSRamos/RelationshipsVisualizationRug
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
 - `participants.csv` maps all participants by their unique ID and their type (e.g., "Tom" is type "Human" and "Puzzle" is type "Toy");
 - `realtionships.csv` maps the relationships between the subject type, object type and type of relationshipt (e.g., the relationship "play with" is an "active" type relationship betweetn the subject "Human" and the object "Toy").

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
