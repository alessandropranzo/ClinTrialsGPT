# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for both Streamlit and A2A server
EXPOSE 8501 8000

# Default to A2A server, but allow override
ENV RUN_MODE=a2a

# Start the appropriate service based on RUN_MODE
CMD ["sh", "-c", "if [ \"$RUN_MODE\" = \"streamlit\" ]; then streamlit run clintrialsgpt.py --server.port=8501 --server.address=0.0.0.0; else python a2a_server.py; fi"]