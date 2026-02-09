# Use Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy backend code
COPY backend ./backend

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/fileService/requirements.txt

# Copy frontend
COPY ../../frontend ./frontend

# Add backend to Python path
ENV PYTHONPATH=/app/backend

# Expose port
EXPOSE 5001

# Run the backend
CMD ["python", "backend/fileService/app.py"]
