# todo-api
basic API that interacts with a database (currently a JSON file)

### Setup Instructions
1. Clone the repository:
```bash
git clone https://github.com/Aetheridon/todo-api.git
cd todo-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the API:
```bash
cd src
uvicorn api:app --reload
```

The API can now be interacted with at http://127.0.0.1:8000/docs#/
