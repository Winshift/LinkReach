FROM python:3.9

WORKDIR /code

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . /code/

# Set PYTHONPATH so 'backend' is discoverable
ENV PYTHONPATH="/code"

# Expose port for Hugging Face Spaces
EXPOSE 7860

# Run FastAPI app via uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
