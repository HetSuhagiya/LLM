# Data Analysis & Reporting Tool

A web-based tool that allows users to upload CSV files, run SQL queries, and generate natural language reports using AI.

## Features

- 📤 Upload and preview CSV files
- 🔍 Run custom SQL queries on your data
- 🤖 Generate AI-powered natural language reports
- 📥 Export reports in multiple formats (TXT, MD, PDF)

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Upload Data**
   - Click the "Choose a CSV file" button to upload your dataset
   - The tool will display a preview and basic statistics of your data

2. **Run SQL Queries**
   - Write your SQL query in the text area
   - Click "Execute Query" to run the query
   - View the results in the table below

3. **Generate Report**
   - After running a query, click "Generate Report"
   - The AI will analyze the data and generate a natural language report
   - View the report in the application

4. **Export Report**
   - Choose your preferred format (TXT, MD, or PDF)
   - Click the download button to save the report

## Requirements

- Python 3.8+
- Internet connection (for AI report generation)
- CSV file with data to analyze

## Note

This tool uses the OpenRouter API to generate reports. Make sure you have a stable internet connection for the AI features to work properly. 