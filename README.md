# 110 Pest Control Services

Website for 110 Pest Control Services, a family-owned, licensed pest control company in Hollywood, FL.

Plain HTML and CSS, no build step. Open `index.html` in a browser to preview.

- `index.html` is the English page and `es/index.html` is the Spanish page. When you change wording, update both.
- `styles.css` holds the styling
- `images/` holds photos and logos

## Before launch

- The quote form uses FormSubmit (formsubmit.co). The first time someone submits it, FormSubmit sends an activation email to pestcontrol110@outlook.com. Click the link in that email so later submissions get delivered.
- Social links live in the `socials` block in the footer of both pages. Add new ones next to the Facebook link.

## Pages

The two homepages (`index.html`, `es/index.html`) are edited by hand.
The Services, About and Contact pages (English and Spanish) and `sitemap.xml` are generated:

1. Edit the text in `_build/content.py` (or a homepage).
2. Run `python3 _build/build.py`.
3. Commit everything it changed.

The generator copies the footer, service icons, About and Contact sections from the homepages,
so change those on the homepage and re-run the build.
