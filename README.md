# EY Water Challenge Showcase

An EY-inspired public showcase for our first machine learning competition project: the **2026 EY AI & Data Challenge: Optimizing Clean Water Supply**.

This repository is intentionally curated for public sharing. Instead of exposing every intermediate artifact from the working directory, it packages the project into a cleaner story:

- a `GitHub Pages` site in `docs/`
- selected notebooks in `notebooks/`
- public data summaries in `docs/assets/data/`
- a LinkedIn-ready draft in `linkedin/`

## What this showcase emphasizes

- The challenge was a real-world water quality prediction problem for South African river locations.
- We approached it as a full experiment program, not just a single model run.
- We iterated through feature engineering, external data enrichment, target-wise modeling, calibration, and repeated failure review.
- Our best tracked official score was `0.376`.

## Repository structure

- `docs/` — the public project page for GitHub Pages
- `docs/assets/data/showcase_data.json` — curated evidence bundle used by the page
- `notebooks/` — selected notebooks that show how the project evolved
- `linkedin/post_draft.md` — an English draft for the public LinkedIn post
- `scripts/build_showcase_data.py` — rebuilds the public JSON bundle from the local source project

## Publishing notes

1. Push this repository to GitHub.
2. Enable GitHub Pages and set the source to `docs/`.
3. Open the published page and confirm the charts load.
4. Update the GitHub repository URL in the LinkedIn post draft if needed.

## Brand and disclosure notes

- This is an **independent team showcase** inspired by EY's editorial design language.
- It is **not** an official EY page.
- The page uses challenge references and source links, but avoids official-looking branding claims.

## Source references

- EY challenge page: [challenge.ey.com](https://challenge.ey.com/)
- Official challenge repository: [Snowflake-Labs/EY-AI-and-Data-Challenge](https://github.com/Snowflake-Labs/EY-AI-and-Data-Challenge)
