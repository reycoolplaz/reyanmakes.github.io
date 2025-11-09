# How to Add Images to Your Portfolio

## Quick Start - Adding Project Images

### 1. Upload Images to GitHub

1. Go to your repository on GitHub: `https://github.com/reyanmakes/reyanmakes.github.io`
2. Navigate to **`images`** → **`projects`** folder
3. Click **"Add file"** → **"Upload files"**
4. Upload your images with these names:
   - `featured1.jpg` - Your best/most recent project
   - `featured2.jpg` - Second featured project
   - `featured3.jpg` - Third featured project
5. Click **"Commit changes"**

### 2. Images Appear Automatically!

The site is set up to use these exact filenames, so your images will show up immediately.

## Your Portfolio Structure

### Featured Projects Section
- Shows your **3 best projects** with images
- These should be your most impressive work
- Good for college admissions to see your best first

### Journey/Timeline Section  
- Shows **all your projects organized by year**
- Demonstrates your growth over time
- Perfect for showing how you've evolved as a maker

## Editing Your Content

### To Update Featured Projects:

Edit `index.html` - look for the "Featured Projects" section. For each project card, update:

```html
<span class="year-badge">2024</span>  <!-- Year you built it -->
<h3>Your Project Title</h3>
<p class="project-description">What you built and why it matters...</p>
<div class="project-tags">
    <span class="tag">Python</span>  <!-- Technologies you used -->
    <span class="tag">Arduino</span>
</div>
```

### To Update Your Timeline:

Edit the timeline section with your actual projects:

```html
<div class="timeline-item">
    <div class="timeline-year">2024</div>
    <div class="timeline-content">
        <h3>Senior Year Projects</h3>
        <ul class="project-list">
            <li>
                <strong>AI Chatbot for School</strong> - Built a chatbot that helps students with homework
                <span class="mini-tags">Python • OpenAI • Flask</span>
            </li>
        </ul>
    </div>
</div>
```

## Tips for College Applications

### What to Highlight:
- **Impact**: How many people used it? What problem did it solve?
- **Learning**: What new skills did you gain?
- **Initiative**: Did you start this yourself or lead a team?
- **Challenges**: What obstacles did you overcome?

### Image Tips:
- Use clear photos of your projects in action
- Screenshots of working apps
- Photos of hardware builds
- Keep images under 2MB for fast loading
- Use landscape orientation (horizontal) for best display

## Supported Image Formats
- .jpg / .jpeg (recommended)
- .png
- .webp
- .gif

---

Need help? Just edit the HTML file and commit your changes to GitHub!
