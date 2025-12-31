/**
 * Edit Mode for Portfolio Site
 * Enables WYSIWYG editing when ?edit=true is in URL
 */
(function() {
    const params = new URLSearchParams(location.search);
    const editMode = params.get('edit') === 'true';
    const adminUrl = params.get('admin') || '';
    const token = params.get('token') || '';

    if (!editMode) return;

    console.log('[Edit Mode] Activated');

    // Store original content for cancel
    let originalContent = null;

    // Element to data path mapping
    const editableConfig = [
        { selector: '.hero-title', path: 'hero.title', type: 'single' },
        { selector: '.hero-subtitle', path: 'hero.subtitle', type: 'single' },
        { selector: '.hero-about p', path: 'about.paragraphs', type: 'array' },
        { selector: '.hero-skills h3', path: 'about.skillsTitle', type: 'single' },
        { selector: '.skill', path: 'about.skills', type: 'array' },
        { selector: '.social-pill.youtube span', path: 'hero.social.youtube.label', type: 'single' },
        { selector: '.cta-button', path: 'hero.ctaText', type: 'single' },
        { selector: '.section-title', path: null, type: 'single' }, // Multiple, handle separately
        { selector: '.milestone-card h3', path: 'milestones.title', type: 'milestone' },
        { selector: '.milestone-card > p:first-of-type', path: 'milestones.description', type: 'milestone' },
        { selector: '.contact-description', path: 'contact.description', type: 'single' },
    ];

    // Make elements editable
    function enableEditing() {
        editableConfig.forEach(config => {
            document.querySelectorAll(config.selector).forEach((el, idx) => {
                el.contentEditable = true;
                el.classList.add('editable');
                el.dataset.editPath = config.path;
                el.dataset.editType = config.type;
                el.dataset.editIndex = idx;

                // Prevent link navigation while editing
                el.addEventListener('click', e => {
                    if (el.isContentEditable) {
                        e.preventDefault();
                    }
                });
            });
        });

        // Add hover effect for skills to show they're editable
        document.querySelectorAll('.skills-grid').forEach(grid => {
            const addBtn = document.createElement('button');
            addBtn.className = 'edit-add-btn';
            addBtn.textContent = '+ Add Skill';
            addBtn.onclick = () => addSkill(grid);
            grid.appendChild(addBtn);
        });

        // Add delete buttons to skills
        document.querySelectorAll('.skill').forEach(skill => {
            const deleteBtn = document.createElement('span');
            deleteBtn.className = 'edit-delete-btn';
            deleteBtn.textContent = '×';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                skill.remove();
                markDirty();
            };
            skill.appendChild(deleteBtn);
        });
    }

    // Add a new skill
    function addSkill(grid) {
        const skill = document.createElement('div');
        skill.className = 'skill editable';
        skill.contentEditable = true;
        skill.dataset.editPath = 'about.skills';
        skill.dataset.editType = 'array';
        skill.textContent = 'New Skill';

        const deleteBtn = document.createElement('span');
        deleteBtn.className = 'edit-delete-btn';
        deleteBtn.textContent = '×';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            skill.remove();
            markDirty();
        };
        skill.appendChild(deleteBtn);

        // Insert before the add button
        const addBtn = grid.querySelector('.edit-add-btn');
        grid.insertBefore(skill, addBtn);
        skill.focus();

        // Select all text
        const range = document.createRange();
        range.selectNodeContents(skill.childNodes[0]);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);

        markDirty();
    }

    // Collect all edited data
    function collectData() {
        const data = {
            hero: {
                title: '',
                subtitle: '',
                ctaText: '',
                ctaLink: '',
                social: { youtube: { url: '', label: '' } }
            },
            about: [],
            skills: [],
            skillsTitle: '',
            contact: [],
            milestones: []
        };

        // Hero title
        const heroTitle = document.querySelector('.hero-title');
        if (heroTitle) data.hero.title = heroTitle.textContent.trim();

        // Hero subtitle
        const heroSubtitle = document.querySelector('.hero-subtitle');
        if (heroSubtitle) data.hero.subtitle = heroSubtitle.textContent.trim();

        // CTA button
        const ctaBtn = document.querySelector('.cta-button');
        if (ctaBtn) {
            data.hero.ctaText = ctaBtn.textContent.trim();
            data.hero.ctaLink = ctaBtn.getAttribute('href') || '#featured';
        }

        // YouTube
        const ytPill = document.querySelector('.social-pill.youtube');
        if (ytPill) {
            const ytSpan = ytPill.querySelector('span');
            data.hero.social.youtube.label = ytSpan ? ytSpan.textContent.trim() : '';
            data.hero.social.youtube.url = ytPill.getAttribute('href') || '';
        }

        // About paragraphs
        document.querySelectorAll('.hero-about p').forEach(p => {
            const text = p.textContent.trim();
            if (text) data.about.push(text);
        });

        // Skills title
        const skillsTitle = document.querySelector('.hero-skills h3');
        if (skillsTitle) data.skillsTitle = skillsTitle.textContent.trim();

        // Skills
        document.querySelectorAll('.skill').forEach(skill => {
            // Get text content without the delete button
            const text = Array.from(skill.childNodes)
                .filter(n => n.nodeType === Node.TEXT_NODE)
                .map(n => n.textContent.trim())
                .join('');
            if (text) data.skills.push(text);
        });

        // Contact links - preserve existing structure
        document.querySelectorAll('.contact-button').forEach(btn => {
            data.contact.push({
                label: btn.textContent.trim(),
                url: btn.getAttribute('href') || ''
            });
        });

        // Milestones - more complex, preserve structure
        document.querySelectorAll('.milestone').forEach((milestone, idx) => {
            const year = milestone.querySelector('.milestone-year');
            const card = milestone.querySelector('.milestone-card');
            const title = card?.querySelector('h3');
            const desc = card?.querySelector('p:not(.milestone-label)');

            if (title || desc) {
                data.milestones.push({
                    year: year?.textContent.trim() || '',
                    title: title?.textContent.trim() || '',
                    description: desc?.textContent.trim() || '',
                    // Preserve other fields from original
                });
            }
        });

        return data;
    }

    // Track if changes were made
    let isDirty = false;
    function markDirty() {
        isDirty = true;
        const saveBtn = document.getElementById('edit-save-btn');
        if (saveBtn) saveBtn.classList.add('has-changes');
    }

    // Create floating toolbar
    function createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.id = 'edit-toolbar';
        toolbar.innerHTML = `
            <div class="edit-toolbar-content">
                <span class="edit-mode-label">Edit Mode</span>
                <button id="edit-save-btn" class="edit-btn save">Save Changes</button>
                <button id="edit-cancel-btn" class="edit-btn cancel">Cancel</button>
            </div>
        `;
        document.body.appendChild(toolbar);

        // Save handler
        document.getElementById('edit-save-btn').onclick = saveChanges;

        // Cancel handler
        document.getElementById('edit-cancel-btn').onclick = () => {
            if (isDirty && !confirm('Discard changes?')) return;
            window.close();
        };
    }

    // Save changes to admin API
    async function saveChanges() {
        const saveBtn = document.getElementById('edit-save-btn');
        const originalText = saveBtn.textContent;
        saveBtn.textContent = 'Saving...';
        saveBtn.disabled = true;

        try {
            const data = collectData();
            console.log('[Edit Mode] Saving:', data);

            if (!adminUrl) {
                // No admin URL - show data for manual copy
                alert('Changes collected! Admin URL not configured.\n\nData:\n' + JSON.stringify(data, null, 2));
                return;
            }

            const response = await fetch(`${adminUrl}/api/sites/reyanmakes.github.io/content`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                },
                credentials: 'include',
                body: JSON.stringify(data)
            });

            if (response.ok) {
                isDirty = false;
                saveBtn.textContent = 'Saved!';
                saveBtn.classList.remove('has-changes');
                saveBtn.classList.add('saved');

                setTimeout(() => {
                    saveBtn.textContent = originalText;
                    saveBtn.classList.remove('saved');
                    saveBtn.disabled = false;
                }, 2000);
            } else {
                throw new Error(`Save failed: ${response.status}`);
            }
        } catch (err) {
            console.error('[Edit Mode] Save error:', err);
            alert('Failed to save: ' + err.message);
            saveBtn.textContent = originalText;
            saveBtn.disabled = false;
        }
    }

    // Add edit mode styles dynamically
    function addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Edit Mode Styles */
            .editable {
                outline: 2px dashed transparent;
                outline-offset: 4px;
                transition: outline-color 0.2s, background-color 0.2s;
                cursor: text;
                min-width: 20px;
                min-height: 1em;
            }
            .editable:hover {
                outline-color: rgba(99, 102, 241, 0.4);
            }
            .editable:focus {
                outline-color: #6366f1;
                outline-style: solid;
                background-color: rgba(99, 102, 241, 0.1);
            }

            /* Skill editing */
            .skill.editable {
                position: relative;
                padding-right: 24px !important;
            }
            .edit-delete-btn {
                position: absolute;
                right: 6px;
                top: 50%;
                transform: translateY(-50%);
                width: 16px;
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #ef4444;
                color: white;
                border-radius: 50%;
                font-size: 12px;
                cursor: pointer;
                opacity: 0;
                transition: opacity 0.2s;
            }
            .skill.editable:hover .edit-delete-btn {
                opacity: 1;
            }
            .edit-add-btn {
                background: transparent;
                border: 2px dashed rgba(255,255,255,0.3);
                color: rgba(255,255,255,0.6);
                padding: 0.5rem 1rem;
                border-radius: 20px;
                cursor: pointer;
                font-size: 0.85rem;
                transition: all 0.2s;
            }
            .edit-add-btn:hover {
                border-color: rgba(255,255,255,0.6);
                color: white;
            }

            /* Floating Toolbar */
            #edit-toolbar {
                position: fixed;
                bottom: 2rem;
                left: 50%;
                transform: translateX(-50%);
                z-index: 99999;
                animation: slideUp 0.3s ease;
            }
            @keyframes slideUp {
                from { transform: translateX(-50%) translateY(100px); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
            .edit-toolbar-content {
                display: flex;
                align-items: center;
                gap: 1rem;
                background: white;
                padding: 0.75rem 1.5rem;
                border-radius: 50px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.25);
            }
            .edit-mode-label {
                font-weight: 600;
                color: #6366f1;
                font-size: 0.9rem;
            }
            .edit-btn {
                padding: 0.6rem 1.25rem;
                border: none;
                border-radius: 25px;
                font-weight: 600;
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.2s;
            }
            .edit-btn.save {
                background: #6366f1;
                color: white;
            }
            .edit-btn.save:hover {
                background: #4f46e5;
                transform: translateY(-1px);
            }
            .edit-btn.save.has-changes {
                background: #f59e0b;
            }
            .edit-btn.save.saved {
                background: #10b981;
            }
            .edit-btn.cancel {
                background: #f3f4f6;
                color: #374151;
            }
            .edit-btn.cancel:hover {
                background: #e5e7eb;
            }
            .edit-btn:disabled {
                opacity: 0.7;
                cursor: not-allowed;
            }
        `;
        document.head.appendChild(style);
    }

    // Track changes
    function setupChangeTracking() {
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('editable')) {
                markDirty();
            }
        });
    }

    // Initialize
    function init() {
        addStyles();
        enableEditing();
        createToolbar();
        setupChangeTracking();

        // Warn before leaving with unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (isDirty) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        console.log('[Edit Mode] Ready - click on any highlighted element to edit');
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
