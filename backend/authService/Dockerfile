# Use Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy backend code
COPY backend/authService ./backend
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend
COPY ../../frontend ./frontend

# Expose port
EXPOSE 5000

# Run the backend
CMD ["python", "backend/app.py"]
