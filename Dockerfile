FROM python:3.11.7-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG DB_USER=${DB_USER} 
ENV DB_USER=${DB_USER} 

ARG DB_PASS=${DB_PASS} 
ENV DB_PASS=${DB_PASS} 

ARG DB_NAME=${DB_NAME} 
ENV DB_NAME=${DB_NAME} 

ARG DB_HOST=${DB_HOST} 
ENV DB_HOST=${DB_HOST} 

ARG DB_PORT=${DB_PORT} 
ENV DB_PORT=${DB_PORT} 

ARG ENV=${ENV} 
ENV ENV=${ENV} 


ARG REDIS_URL=${REDIS_URL}
ENV REDIS_URL=${REDIS_URL}

# Set the base directory used in any further RUN, COPY, and ENTRYPOINT
# commands.
RUN mkdir -p /app
RUN mkdir -p /app/static
WORKDIR /app

# Install essential dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies into the container
COPY bankingsystem ./ 

# install python dependencies
RUN pip install -r requirements.txt

EXPOSE 8000

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]