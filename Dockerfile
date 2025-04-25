# Use full Python image (not slim)
FROM python:3.9

WORKDIR /app

# Copy everything
COPY . .

# Upgrade pip and install requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (for Railway/Gunicorn)
EXPOSE 8000

# Start the app using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
