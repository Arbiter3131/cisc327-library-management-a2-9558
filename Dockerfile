
FROM python:3.10.1-slim


WORKDIR /app


COPY . /app

# Install dependencies
RUN pip install -r requirements.txt  

# Expose port 5000 for Flask
EXPOSE 5000  

# Command to run the app
CMD ["python", "app.py"]