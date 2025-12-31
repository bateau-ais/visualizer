# NOVA Visualizer Module
FROM python:3.10-slim

WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install -q --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port for web interface
EXPOSE 5000

# Run the main application
CMD ["python", "app.py"]
