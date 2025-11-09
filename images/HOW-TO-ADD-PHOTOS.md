# How to Add Your Project Photos

## Quick Guide for Adding Images

Your portfolio is set up to display photos of your actual builds. Here's how to add them:

### 1. Take Photos of Your Projects

For each project, take clear photos showing:
- **The finished build** (main hero shot)
- **Before/during shots** if you have them
- **Detail shots** of interesting features
- **Action shots** of the project in use

### 2. Name Your Photos

Rename your photos to match these exact filenames:

**For Homepage (3 featured builds):**
- `gokart.jpg` - Your go-kart photo
- `lakehouse.jpg` - The lake house/fort
- `bed.jpg` - Your custom bed frame

**For Projects Page (all builds):**
- `gokart.jpg` - Go-kart
- `lakehouse.jpg` - Lake House fort
- `bed.jpg` - Bed Frame  
- `canoe-trailer.jpg` - Canoe trailer
- `knife.jpg` - Hand-forged knife

### 3. Upload to GitHub

1. Go to your repository: `https://github.com/reyanmakes/reyanmakes.github.io`
2. Click on the **`images`** folder
3. Click **"Add file"** → **"Upload files"**
4. Drag and drop all your renamed photos
5. Click **"Commit changes"**

### 4. Your Photos Appear Automatically!

Once uploaded to GitHub, your photos will show up on your website within a few minutes.

## Photo Tips

### Best Practices:
- **Format**: Use .jpg or .png files
- **Size**: Keep photos under 2MB each for fast loading
- **Dimensions**: 1200px wide is perfect (landscape orientation)
- **Quality**: Make sure photos are clear and well-lit
- **Background**: Clean backgrounds help your builds stand out

### Good Photo Examples:
- Go-kart sitting outside with you in it
- Lake house showing the full structure
- Bed frame installed in your room
- Canoe loaded on the bike trailer
- Knife on a wooden surface or in your hand

### Photo Editing (Optional):
- Crop to remove distractions
- Adjust brightness/contrast if needed
- Don't over-edit — keep it authentic!

## Adding More Projects

Want to add new projects beyond the initial five?

1. **Add the photo** to the `images/` folder with a descriptive name (e.g., `treehouse.jpg`)
2. **Edit `projects.html`** - copy an existing project card and update:
   - Image filename
   - Project title
   - Description
3. **Edit `script.js`** - add project details to the `projectData` object

Example:
```javascript
yourproject: {
    title: "Your Project Name",
    description: "Brief description...",
    story: "Longer story about the build...",
    skills: ["Skill 1", "Skill 2"],
    materials: "Materials you used"
}
```

## Need Help?

If photos aren't showing up:
1. Check that filenames match exactly (case-sensitive!)
2. Make sure files are in the `images/` folder, not a subfolder
3. Wait a few minutes for GitHub Pages to update
4. Try a hard refresh: Ctrl+Shift+R (PC) or Cmd+Shift+R (Mac)

---

**Remember:** Your builds are impressive — let the photos show that! Good lighting and clear shots will make your portfolio stand out.
