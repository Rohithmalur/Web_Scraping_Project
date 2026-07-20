FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
   chromium \
   chromium-driver \
   fonts-liberation \
   libnss3 \
   libxss1 \
   libgbm1 \
   libgtk-3-0 \
   libasound2 \
   xvfb \
   curl \
   unzip \
   wget \
&& rm -rf /var/lib/apt/lists/*
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir setuptools && \
   pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "App.py", "--server.port=8501", "--server.address=0.0.0.0"]
 
