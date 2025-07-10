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

# Expose the port for Hugging Face Spaces
EXPOSE 7860

# Command to run the application for Hugging Face Spaces
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"] 