FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY bot.py .
COPY config.json .

# Create logs directory
RUN mkdir -p /app/logs

# Run the bot
CMD ["python", "bot.py"]
