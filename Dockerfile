
# 1. Start from a lightweight Python image
FROM python:3.11-slim
# 2. Set environment variables to stop Python from buffering logs
# 3. Create a working folder inside the container named /app
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1\
    PYTHONUNBUFFERED=1
# 4. Copy requirements.txt FIRST so Docker can cache installed packages
COPY requirements.txt .
# 5. Install your Python dependencies inside the container
RUN pip install --no-cache-dir  --upgrade pip && pip install --no-cache-dir -r requirements.txt
# 6. Copy the rest of your app's code into /app
COPY . .
# 7. Expose port 8000
EXPOSE 8000
# 8. Command to start Uvicorn when the container boots
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]