import ollama
import logging

logger = logging.getLogger(__name__)

def extract_stock_symbol(user_input):
    """Extract stock ticker symbol from natural language input using Ollama's gemma:2b model."""
    prompt = f"""
   Give only tag or symbol for the related company to {user_input} in Captials """
    
    try:
        response = ollama.generate(
            model='gemma:2b',
            prompt=prompt,
            options={'temperature': 0.1}  # More deterministic output
        )
        logger.debug(f"Ollama response: {response}")
        symbol = response.get('response', '').strip()
        return symbol if symbol and symbol != 'None' else None
    except Exception as e:
        logger.error(f"Error in ollama.generate: {e}")
        return None

if __name__ == "__main__":
    user_input = input("Enter a stock query: ")
    ticker = extract_stock_symbol(user_input)
    print(f"Extracted stock ticker: {ticker}")
