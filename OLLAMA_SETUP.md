# Ollama Setup Guide for Stock Researcher

This guide will help you set up Ollama with high-quality open-source models for your stock research application.

## What is Ollama?

Ollama is a tool that makes it easy to run large language models locally on your machine. It provides a simple API and command-line interface for managing and running open-source LLMs.

## Installation

### 1. Install Ollama

**macOS:**
```bash
# Download and install from the official website
curl -fsSL https://ollama.ai/install.sh | sh

# Or install via Homebrew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download the installer from [ollama.ai](https://ollama.ai/download)

### 2. Start Ollama Service

```bash
# Start the Ollama service (runs on http://localhost:11434 by default)
ollama serve
```

Keep this terminal open as Ollama needs to be running for the application to work.

### 3. Install Python Dependencies

```bash
cd backend
uv sync  # or pip install -r requirements.txt
```

## Recommended Models

Based on performance and efficiency, here are the best models for your stock research application:

### 1. **Llama 3.1 8B** (Recommended for most users)
- **Size:** ~4.7GB
- **Performance:** Excellent for reasoning and analysis
- **Best for:** General stock analysis, research, and decision-making

```bash
ollama pull llama3.1:8b
```

### 2. **Qwen2.5 7B** (Great alternative)
- **Size:** ~4.4GB
- **Performance:** Strong multilingual support and reasoning
- **Best for:** International stocks and diverse market analysis

```bash
ollama pull qwen2.5:7b
```

### 3. **Mixtral 8x7B** (For advanced users)
- **Size:** ~26GB
- **Performance:** Mixture of Experts model with excellent capabilities
- **Best for:** Complex financial analysis and research

```bash
ollama pull mixtral:8x7b
```

### 4. **Code Llama 7B** (For technical analysis)
- **Size:** ~3.8GB
- **Performance:** Specialized for code and technical analysis
- **Best for:** Technical indicators and algorithmic analysis

```bash
ollama pull codellama:7b
```

## Configuration

### 1. Update Environment Variables

Create or update your `.env` file in the backend directory:

```env
# Set the default LLM provider to Ollama
DEFAULT_LLM_PROVIDER=ollama-llama3.1

# Ollama configuration (optional, defaults to localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. Available Provider Options

You can switch between different models by changing the `DEFAULT_LLM_PROVIDER`:

- `ollama-llama3.1` - Llama 3.1 8B (recommended)
- `ollama-qwen2.5` - Qwen2.5 7B
- `ollama-mixtral` - Mixtral 8x7B
- `ollama-codellama` - Code Llama 7B
- `ollama-llama3.1-70b` - Llama 3.1 70B (requires more RAM)
- `ollama-qwen2.5-72b` - Qwen2.5 72B (requires more RAM)

## Usage

### 1. Start the Application

```bash
# Start Ollama service (in one terminal)
ollama serve

# Start the backend (in another terminal)
cd backend
uv run python main.py
```

### 2. Test the Integration

The application will automatically use the configured Ollama model. You can test it by:

1. Opening the frontend at `http://localhost:5173`
2. Entering a stock symbol (e.g., "AAPL")
3. The system will use your local Ollama model for analysis

## Performance Tips

### 1. Hardware Requirements

**Minimum (for 7B-8B models):**
- RAM: 8GB
- Storage: 10GB free space
- CPU: Modern multi-core processor

**Recommended (for 70B+ models):**
- RAM: 32GB+
- Storage: 50GB+ free space
- GPU: NVIDIA GPU with 16GB+ VRAM (optional but recommended)

### 2. Optimization

**For better performance:**
```bash
# Set environment variables for better performance
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_MAX_QUEUE=512
```

**For GPU acceleration (if you have an NVIDIA GPU):**
```bash
# Install CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Troubleshooting

### 1. Model Not Found
```bash
# List installed models
ollama list

# Pull the model if not installed
ollama pull llama3.1:8b
```

### 2. Connection Refused
- Ensure Ollama service is running: `ollama serve`
- Check if port 11434 is available: `lsof -i :11434`

### 3. Out of Memory
- Use smaller models (7B instead of 70B)
- Close other applications to free up RAM
- Consider using quantized models

### 4. Slow Performance
- Use GPU acceleration if available
- Reduce context window size in the code
- Use smaller models for faster responses

## Model Comparison

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| Llama 3.1 8B | 4.7GB | Fast | Excellent | General analysis |
| Qwen2.5 7B | 4.4GB | Fast | Excellent | Multilingual |
| Mixtral 8x7B | 26GB | Medium | Outstanding | Complex analysis |
| Code Llama 7B | 3.8GB | Fast | Good | Technical analysis |

## Next Steps

1. Install Ollama and pull your preferred model
2. Update your `.env` file with the desired provider
3. Start the application and test with a stock symbol
4. Monitor performance and adjust model size as needed

## Support

- [Ollama Documentation](https://ollama.ai/docs)
- [LangChain Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama)
- [Model Library](https://ollama.ai/library)

Happy analyzing! 🚀
