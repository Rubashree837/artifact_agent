# API Keys Required

This project requires the following API keys:

- Google Gemini API Key
- Smithsonian Open Access API Key
- Europeana API Key

## Configuration

Create a `.env` file in the project root and add:

```env
GOOGLE_API_KEY=your_gemini_api_key
SMITHSONIAN_API_KEY=your_smithsonian_api_key
EUROPEANA_API_KEY=your_europeana_api_key

Replace the placeholder values with the respective API keys.

API Key Sources

Google Gemini API: https://ai.google.dev/
Smithsonian Open Access API: https://www.si.edu/openaccess/devtools
Europeana API: https://www.europeana.eu/en/apis

After adding the API keys, install the required dependencies and run:

pip install -r requirements.txt
python main.py