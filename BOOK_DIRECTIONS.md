# Book directions — HTML structure validator

**Catalog #195** · Greg Wilson, *Software Design by Example: A Tool-Based Introduction with Python* (CRC, 2024), **Chapter 11** — An HTML Validator

- Book site: [gvwilson.github.io/sdxpy/check](https://gvwilson.github.io/sdxpy/check/)
- Upstream: [gvwilson/sdxpy/check](https://github.com/gvwilson/sdxpy/tree/main/check)
- Local reference: [`reference/`](./reference/)
- Core logic: [`html_validator_core.py`](./html_validator_core.py)

## What the book asks you to build

1. Parse HTML into a DOM with **BeautifulSoup**.
2. Walk the tree with a **Visitor** base class.
3. **Catalog** visitor — record which child tags appear under each parent.
4. **Check** visitor — compare actual children to allowed sets from a **YAML manifest**.
5. Report disallowed child tags per parent.

## Web version (`web/` — FastAPI, port **3033**)

| Book piece | Web equivalent |
|------------|----------------|
| `check.py` + `manifest.yml` | `POST /api/analyze` with preset or custom YAML |
| `catalog.py` | Catalog section in API response |
| CLI file args | Paste HTML + sample loaders in the UI |

**Catalog note:** Tier **B** pick (outside the O'Hanlon → Derks → Sweigart → Eckroth wheel) to represent the master **~189-book** library.
