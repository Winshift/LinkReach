FROM python:3.9

WORKDIR /code

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . /code/

# Set working directory to app folder
WORKDIR /code

# Add the current directory to Python path
ENV PYTHONPATH=/code

# Expose the port (matching the uvicorn command)
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 