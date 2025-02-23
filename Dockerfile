# Use official Python base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project
COPY . .

# Expose the port Django runs on
EXPOSE 8000

# Run migrations and start the server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
