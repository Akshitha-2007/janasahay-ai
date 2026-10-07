# JANASAHAY AI — AI-Powered Government Scheme Assistant
RAG pipeline: documents → extract (+OCR) → clean → chunk → `all-MiniLM-L6-v2` embeddings → ChromaDB → retrieval → Google Gemini → grounded answer + sources.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# OCR (optional): sudo apt install tesseract-ocr poppler-utils
mkdir -p .streamlit && cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then edit keys
streamlit run app.py
```
On first launch open **Home → Load sample scheme documents** to index 5 demo schemes.

## Deploy on Streamlit Community Cloud
1. `git init && git add . && git commit -m "JANASAHAY AI" && git branch -M main`
2. Create an empty GitHub repo, then `git remote add origin <url> && git push -u origin main`
3. share.streamlit.io → **New app** → pick repo, branch `main`, file `app.py`, Python 3.11+.
4. **Advanced settings → Secrets**:
```toml
GEMINI_API_KEY = "..."
ADMIN_PASSWORD = "..."
```
5. Deploy. `packages.txt` installs Tesseract + Poppler automatically.

Note: Community Cloud storage is ephemeral — re-index documents after a restart (use the sample loader or the Upload page).
