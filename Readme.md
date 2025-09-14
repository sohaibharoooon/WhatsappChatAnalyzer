# Whatsapp Chat Analyzer

A Django-based web application to analyze WhatsApp chat exports for insights and statistics.

## Making Process

you can check WhatappChatAnalyzer/Whatsapp chat analysis.ipynb file for more details.

## Features

- Upload and analyze WhatsApp chat
- Visualize message statistics
- User-friendly interface

## Getting Started

### Prerequisites

- Python 3.8+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/WhatsappChatAnalyzer.git
cd WhatsappChatAnalyzer
```

### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Usage

1. Go to Whatsapp, Open chat click on three dot and click export.
2. Choose without media option.
3. Save the exported chat zip file to your computer.
4. Extract the zip file to get the .txt chat file.
5. On the web app, upload the .txt file to analyze.
6. View the generated statistics and visualizations.


## License

MIT License
