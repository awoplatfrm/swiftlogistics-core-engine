
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
# Copy the entrypoint script and make sure it's executable inside Docker
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x entrypoint.sh
# 7. Expose port 8000
EXPOSE 8000

ENTRYPOINT [ "/entrypoint.sh" ]
# 8. Command to start Uvicorn when the container boots
CMD [ "gunicorn", "app.main:app", "-w","4","-k" "uvicorn.workers.UvicornWorker", "-b" "--host", "0.0.0.0:8000" ]