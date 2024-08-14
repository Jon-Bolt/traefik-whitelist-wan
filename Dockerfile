FROM python:3.9-slim-buster

WORKDIR /app

COPY get_wan_ip.py . 

RUN pip install requests

# Add the CMD instruction to run your script
CMD ["python", "get_wan_ip.py"] 
