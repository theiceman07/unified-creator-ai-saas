FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependencies definitions
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy the rest of the application
COPY . .

# Expose port for the API
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
