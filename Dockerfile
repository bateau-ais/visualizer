# NOVA Visualizer Module
FROM python:3.12-slim

WORKDIR /app

# Copy dependencies
COPY visualizer/backend/requirements.txt .
RUN pip install -q --no-cache-dir -r requirements.txt

# Copy application files
COPY visualizer/ .

# Expose port for web interface
EXPOSE 8000

# Run the main application
CMD ["python", "backend/main.py"]
