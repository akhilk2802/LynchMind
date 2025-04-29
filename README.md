# LynchMind Project

## Overview
LynchMind is a data-driven project that combines financial analysis, data science, and generative AI to provide insights and tools for stock analysis and market recommendations. The project leverages LangChain, OpenAI embeddings, and ChromaDB for smarter retrieval and indexing, along with a custom-built screener application.

## Project Structure

### Root Directory
- **47 RAG LangChain Text Embedding & Indexing with OpenAI for Smarter Retrieval.ipynb**: A Jupyter Notebook demonstrating text embedding and indexing using OpenAI and LangChain.
- **48 LangChain RAG Vectorstore Indexing with OpenAI & ChromaDB.ipynb**: A Jupyter Notebook showcasing vectorstore indexing with OpenAI and ChromaDB.
- **build_index.py**: Script for building the index for retrieval-augmented generation (RAG).
- **chatbot_app.py**: Application script for a chatbot powered by generative AI.
- **genAI project Dataset.xlsx**: Dataset used for generative AI tasks.
- **Introduction_to_Data_and_Data_Science_3.docx**: Document introducing data and data science concepts.

### intro-to-ds-lectures/
- Contains files and data related to introductory data science lectures.

### screener/
- **app.py**: Main application script for the screener.
- **dowjones_lynch_project_data.xlsx**: Dataset for Dow Jones and Lynch project analysis.
- **requirements.txt**: Python dependencies for the screener application.
- **pages/**: Contains individual page scripts for the screener application:
  - `1_Home.py`: Home page.
  - `2_Stock_Analysis.py`: Stock analysis page.
  - `3_Recommendations.py`: Recommendations page.
  - `4_Screener.py`: Screener page.
  - `5_Market_Insights.py`: Market insights page.
  - `6_Peter_Lynch_Bot.py`: Peter Lynch-inspired bot page.
- **utils/**: Utility scripts for the screener application:
  - `data_loader.py`: Script for loading data.
  - `lynch_scoring.py`: Script for scoring stocks based on Lynch methodology.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akhilk2802/LynchMind.git
   ```
2. Navigate to the `screener` directory:
   ```bash
   cd screener
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Screener Application
1. Run the screener application:
   ```bash
   python app.py
   ```
2. Access the application in your web browser at `http://localhost:8501`.

### Notebooks
- Open the Jupyter Notebooks in the root directory to explore LangChain and OpenAI-based indexing and embedding techniques.

## Data
- **genAI project Dataset.xlsx**: Dataset for generative AI tasks.
- **dowjones_lynch_project_data.xlsx**: Dataset for stock analysis and recommendations.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.