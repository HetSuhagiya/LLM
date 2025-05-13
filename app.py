import streamlit as st
import pandas as pd
import pandasql as psql
import openai
import tempfile
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO

# Configure the page
st.set_page_config(
    page_title="Data Analysis & Reporting Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .report-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .metric-box {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for storing data
if 'df' not in st.session_state:
    st.session_state.df = None
if 'query_result' not in st.session_state:
    st.session_state.query_result = None

# Function to execute SQL query
def execute_sql_query(query, df):
    try:
        result = psql.sqldf(query, locals())
        return result
    except Exception as e:
        st.error(f"Error executing SQL query: {str(e)}")
        return None

def create_pdf(report_content):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=12
    ))
    
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12
    ))
    
    # Build the PDF content
    story = []
    
    # Title
    story.append(Paragraph("Business Analysis Report", styles['CustomTitle']))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['CustomBody']))
    story.append(Spacer(1, 20))
    
    # Report content
    for line in report_content.split('\n'):
        if line.strip():
            if line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.'):
                story.append(Paragraph(line, styles['CustomHeading']))
            else:
                story.append(Paragraph(line, styles['CustomBody']))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("---", styles['CustomBody']))
    story.append(Paragraph("This report was generated using the Data Analysis & Reporting Tool", styles['CustomBody']))
    
    # Build the PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Function to format report for download
def format_report_for_download(report_content, format_type):
    if format_type == 'md':
        return f"""# Business Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{report_content}

---
*This report was generated using the Data Analysis & Reporting Tool*
"""
    elif format_type == 'txt':
        return f"""BUSINESS ANALYSIS REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{report_content}

---
This report was generated using the Data Analysis & Reporting Tool
"""
    else:  # PDF
        return create_pdf(report_content)

# Function to generate report using OpenRouter API
def generate_report(data):
    try:
        openai.api_key = "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"
        openai.api_base = "https://openrouter.ai/api/v1"

        # Get column names and data types
        columns_info = {col: str(dtype) for col, dtype in data.dtypes.items()}
        
        # Calculate key metrics
        key_metrics = {}
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                key_metrics[col] = {
                    'total': data[col].sum(),
                    'avg': data[col].mean(),
                    'change': ((data[col].iloc[-1] - data[col].iloc[0]) / data[col].iloc[0] * 100) if len(data) > 1 else 0
                }
            elif pd.api.types.is_datetime64_dtype(data[col]):
                key_metrics[col] = {
                    'period': f"{data[col].min()} to {data[col].max()}"
                }
            else:
                key_metrics[col] = {
                    'top_value': data[col].value_counts().index[0] if not data[col].empty else None
                }
        
        prompt = f"""As a business analyst, provide a concise business report for the following query results. Focus only on the most important insights and metrics.

Key Metrics:
{key_metrics}

Please provide a brief report (max 3-4 paragraphs) that includes:

1. Key Finding (1 sentence)
2. Critical Metrics (2-3 most important numbers)
3. Business Impact (1-2 sentences)
4. Action Item (1 sentence)

Keep the analysis high-level and focus on the most significant insights. Avoid detailed explanations and focus on actionable insights."""

        completion = openai.ChatCompletion.create(
            model="microsoft/phi-4-reasoning-plus:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Data Analysis Tool"
            }
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        return None

# Sidebar
with st.sidebar:
    st.title("📊 About")
    st.markdown("""
    This tool helps you:
    - Upload and analyze CSV data
    - Run SQL queries
    - Generate business reports
    - Export insights
    """)
    
    st.title("💡 Tips")
    st.markdown("""
    - Use SQL to filter and aggregate data
    - Focus on key metrics
    - Export reports for sharing
    """)

# Main app layout
st.title("📊 Data Analysis & Reporting Tool")

# File upload section
st.header("1. Upload CSV File")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.success("File uploaded successfully!")
        
        # Display data preview
        st.subheader("Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        
        # Display basic statistics
        st.subheader("Basic Statistics")
        st.dataframe(df.describe(), use_container_width=True)
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

# SQL Query section
st.header("2. Run SQL Query")
if st.session_state.df is not None:
    query = st.text_area("Enter your SQL query:", height=150)
    if st.button("Execute Query"):
        if query:
            result = execute_sql_query(query, st.session_state.df)
            if result is not None:
                st.session_state.query_result = result
                st.subheader("Query Results")
                st.dataframe(result, use_container_width=True)
        else:
            st.warning("Please enter a SQL query.")
else:
    st.info("Please upload a CSV file first to run SQL queries.")

# Report Generation section
if st.session_state.query_result is not None:
    st.header("3. Generate Report")
    if st.button("Generate Report"):
        with st.spinner("Generating concise business report..."):
            report = generate_report(st.session_state.query_result)
            if report:
                st.session_state.report = report
                st.subheader("Generated Business Report")
                
                # Display report in a styled box
                st.markdown('<div class="report-box">', unsafe_allow_html=True)
                st.write(report)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Export options
                st.subheader("Export Report")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    formatted_txt = format_report_for_download(report, 'txt')
                    st.download_button(
                        label="📄 Download as TXT",
                        data=formatted_txt,
                        file_name=f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    formatted_md = format_report_for_download(report, 'md')
                    st.download_button(
                        label="📝 Download as MD",
                        data=formatted_md,
                        file_name=f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
                
                with col3:
                    formatted_pdf = format_report_for_download(report, 'pdf')
                    st.download_button(
                        label="📑 Download as PDF",
                        data=formatted_pdf,
                        file_name=f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    ) 