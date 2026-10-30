# HTML structure validator (catalog #195)

DOM visitor + manifest checker from Greg Wilson’s *Software Design by Example*, Chapter 11.

## Run the web demo (port 3033)

```powershell
Set-Location "c:\Users\emmak\Desktop\Content\CodingProjects\PortProjects\demos\html-validator\web"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 3033
```

Open http://localhost:3033

Provenance: [BOOK_DIRECTIONS.md](./BOOK_DIRECTIONS.md).
