# Use the official lightweight Python 3.11 image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files first to leverage Docker's layer caching
COPY pyproject.toml setup.py ./

# Copy the backend code (required for setup.py to work)
COPY backend/ ./backend/

# Install dependencies (no cache keeps the image small)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
# CRITICAL: --host 0.0.0.0 makes the server accessible outside the container
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]