# Reyan Makes Portfolio

## Overview

A personal portfolio website showcasing the maker projects of Reyan Bhattacharjee, a high school student from Plainsboro, NJ. The site displays physical builds including go-karts, furniture, structures, and metalwork projects. Built as a static site with vanilla HTML, CSS, and JavaScript to maintain a handcrafted, authentic aesthetic that matches the maker ethos.

## User Preferences

- **Communication style**: Simple, everyday language
- **Aesthetic**: Handcrafted, genuine, maker's journal (not corporate)
- **Content focus**: Physical builds (woodworking, welding, metalwork) not software projects

## System Architecture

### Frontend Architecture

**Static Site Design**
- Pure HTML/CSS/JavaScript with no frameworks or build tools
- Three-page structure: Home (`index.html`), Projects (`projects.html`), About (`about.html`)
- Rationale: Simplicity matches the maker aesthetic; easy to maintain and host on GitHub Pages
- Trade-off: Manual updates required, but gives complete control over presentation

**Component Structure**
- Shared navigation bar across all pages with active state styling
- Reusable project card components with modal overlay system
- Responsive grid layouts for project galleries
- Inline SVG fallbacks for missing images (prevents broken image icons)

**Data Management**
- Project metadata stored in `script.js` as a JavaScript object (`projectData`)
- Each project includes: title, description, story, skills array, and materials list
- Modal system dynamically generates project detail views from this data
- Alternative: Could use JSON file, but inline JS object is simpler for static hosting

**Styling Approach**
- Custom CSS with CSS variables for color theming (`:root` with defined palette)
- Google Fonts (Poppins) for typography
- Mobile-first responsive design principles
- Color palette: off-white background (#F8F7F3), charcoal text (#333333), wood-brown accents (#A67B5B), orange highlights (#E67E22)

### Image Management System

**Static Asset Structure**
- Images stored in `/images/` directory
- Organized by project with specific naming convention (e.g., `gokart.jpg`, `lakehouse.jpg`, `bed.jpg`)
- Naming convention enforced to simplify updates (users replace files with exact names)

**Fallback Strategy**
- Inline SVG placeholders in `onerror` attributes prevent broken images
- Allows site to function even without uploaded photos
- Users can add real photos by simply uploading files with matching names

**User Documentation**
- `HOW-TO-ADD-IMAGES.md` provides step-by-step GitHub upload instructions
- `/images/HOW-TO-ADD-PHOTOS.md` duplicates instructions at asset level
- Design choice: Non-technical user (high school student) can update content via GitHub web interface

### Content Organization

**Homepage (index.html)**
- Hero section with personal introduction and maker philosophy
- Three featured project cards (Go-Kart, Lake House, Bed Frame)
- Call-to-action button to projects page
- Designed to make strong first impression for college applications

**Projects Page (projects.html)**
- Grid gallery of all builds (Lake House, Go-Kart, Bed Frame, Canoe Trailer, Knife, placeholder for more)
- Clickable cards open modal with full project details
- Modal shows story, skills used, and materials
- JavaScript-driven modal system with smooth interactions

**About Page (about.html)**
- Personal essay adapted from college application materials
- Skills breakdown (woodworking, welding, design, resourcefulness)
- Contact form integrated with Formspree (requires user to add form ID)
- Resume download button (placeholder for future PDF)
- Background and motivation section

### JavaScript Functionality

**Project Modal System**
- `projectData` object contains detailed information for each build
- Click handlers on project cards trigger modal display
- Modal populated dynamically from project data
- Close handlers for X button, backdrop click, and ESC key
- Prevents body scroll when modal is open

**Navigation**
- Smooth scroll for anchor links
- Active page highlighting in navigation
- Consistent navigation across all pages

## External Dependencies

### Hosting & Deployment
- **GitHub Pages** - Static site hosting directly from repository
- Repository: `reyanmakes/reyanmakes.github.io`
- Deployment: Automatic on push to main branch
- No build process required

### Frontend Libraries
- **Google Fonts** - Poppins font family via CDN
- Import URL: `https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap`
- Only external dependency; all other code is vanilla

### Third-Party Services
- **Formspree** - Contact form handling (requires user signup and form ID configuration)
- Free tier available, no backend required

### Assets
- User-uploaded project photos (JPG/PNG format)
- SVG fallback images (inline, no external files)
- No icon libraries or image processing tools required

### Browser APIs
- Standard DOM manipulation (no polyfills required)
- Event listeners for modal interactions
- CSS Grid and Flexbox (modern browser support assumed)

## Development Workflow

### Local Development
- Python HTTP server on port 5000 for local preview
- Command: `python -m http.server 5000 --bind 0.0.0.0`
- No compilation or build steps required

### Adding New Projects

1. **Add project photo** to `images/` folder with descriptive filename
2. **Edit `script.js`** - add project to `projectData` object:
   ```javascript
   projectname: {
       title: "Project Name",
       description: "Brief description",
       story: "Full story of the build process",
       skills: ["Skill 1", "Skill 2"],
       materials: "Materials used"
   }
   ```
3. **Edit `projects.html`** - copy existing project card and update:
   - `data-project` attribute to match key in projectData
   - Image src to match uploaded photo filename
   - Title and subtitle text

### Updating Content

- **Homepage intro**: Edit text in `index.html` hero section
- **About page**: Edit biography text in `about.html`
- **Contact form**: Replace `YOUR_FORM_ID` in `about.html` with actual Formspree form ID
- **Project details**: Update `projectData` in `script.js`
- **Styling**: Modify CSS variables in `styles.css` `:root` section

## Future Enhancements

### Immediate Next Steps
1. Upload actual project photos to replace SVG placeholders
2. Set up Formspree account and configure contact form
3. Add resume PDF and update download link

### Optional Improvements
- Mobile navigation hamburger menu for very small screens
- Build log section for ongoing projects
- Social media integration (Instagram, YouTube)
- Before/after image comparisons for projects
- Photo gallery within each project modal

## Technical Notes

- Site uses semantic HTML5 elements
- Accessible navigation with keyboard support
- Mobile-responsive with media queries at 768px breakpoint
- Image fallbacks ensure site never shows broken images
- All interactions work without JavaScript (graceful degradation)
- Contact form degrades to mailto: link if Formspree unavailable

## Project Structure

```
/
├── index.html              # Homepage with featured builds
├── projects.html           # Full project gallery
├── about.html              # Biography and contact
├── styles.css              # All styling (color palette, layouts, responsive)
├── script.js               # Project data and modal interactions
├── images/                 # Project photos directory
│   └── HOW-TO-ADD-PHOTOS.md
├── HOW-TO-ADD-IMAGES.md    # User guide for adding images
├── README.md               # Repository readme
└── replit.md               # This file
```
