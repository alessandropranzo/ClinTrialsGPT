# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir \
    openai==1.59.8 \
    streamlit==1.41.1

# Expose port 8501 for Streamlit
EXPOSE 8501

# Start Ollama in the background and launch Streamlit
CMD ["sh", "-c", "streamlit run clintrialsgpt.py --server.port=8501 --server.address=0.0.0.0"]