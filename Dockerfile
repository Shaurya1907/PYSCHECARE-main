FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download required NLTK data
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('wordnet', quiet=True)"

# Copy the rest of the application
COPY . .

# Expose the Flask port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_PORT=5000

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
