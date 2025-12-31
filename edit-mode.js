/**
 * Edit Mode for Portfolio Site - Editor.js + AI Integration
 * Modern block-based editing with AI assistance
 */
(function() {
    const params = new URLSearchParams(location.search);
    const editMode = params.get('edit') === 'true';
    const adminUrl = params.get('admin') || '';
    const token = params.get('token') || '';
    const isEmbedded = params.get('embedded') === 'true' || window.parent !== window;

    if (!editMode) return;

    console.log('[Edit Mode] Activated with Editor.js');

    // Track state
    let isDirty = false;
    let aboutEditor = null;

    // ==================== SCRIPT LOADING ====================
    const EDITOR_JS_SCRIPTS = [
        'https://cdn.jsdelivr.net/npm/@editorjs/editorjs@2.28.2/dist/editorjs.umd.min.js',
        'https://cdn.jsdelivr.net/npm/@editorjs/header@2.8.1/dist/header.umd.min.js',
        'https://cdn.jsdelivr.net/npm/@editorjs/list@1.9.0/dist/list.umd.min.js',
        'https://cdn.jsdelivr.net/npm/@editorjs/quote@2.6.0/dist/quote.umd.min.js',
        'https://cdn.jsdelivr.net/npm/@editorjs/delimiter@1.4.0/dist/delimiter.umd.min.js'
    ];

    async function loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async function loadEditorJS() {
        console.log('[Edit Mode] Loading Editor.js...');
        for (const src of EDITOR_JS_SCRIPTS) {
            await loadScript(src);
        }
        console.log('[Edit Mode] Editor.js loaded');
    }

    // ==================== EDITOR INITIALIZATION ====================
    async function initAboutEditor() {
        const aboutContainer = document.querySelector('.hero-about');
        if (!aboutContainer) return;

        // Get current content and convert to blocks
        const paragraphs = aboutContainer.querySelectorAll('p');
        const blocks = Array.from(paragraphs).map(p => ({
            type: 'paragraph',
            data: { text: p.innerHTML }
        }));

        // Create editor holder
        aboutContainer.innerHTML = '<div id="about-editor"></div>';

        // Initialize Editor.js
        aboutEditor = new EditorJS({
            holder: 'about-editor',
            placeholder: 'Start writing your story...',
            tools: {
                header: {
                    class: Header,
                    config: {
                        placeholder: 'Enter a header',
                        levels: [2, 3, 4],
                        defaultLevel: 3
                    }
                },
                list: {
                    class: List,
                    inlineToolbar: true
                },
                quote: {
                    class: Quote,
                    config: {
                        quotePlaceholder: 'Enter a quote',
                        captionPlaceholder: 'Quote author'
                    }
                },
                delimiter: Delimiter
            },
            data: {
                blocks: blocks.length > 0 ? blocks : [
                    { type: 'paragraph', data: { text: 'Tell your story here...' } }
                ]
            },
            onChange: () => {
                markDirty();
                notifyParentOfChanges();
            }
        });

        await aboutEditor.isReady;
        console.log('[Edit Mode] About editor ready');
    }

    // ==================== SIMPLE EDITABLE ELEMENTS ====================
    // Keep simple contenteditable for hero title, subtitle, etc.
    const simpleEditables = [
        { selector: '.hero-title', path: 'hero.title' },
        { selector: '.hero-subtitle', path: 'hero.subtitle' },
        { selector: '.hero-skills h3', path: 'skillsTitle' },
        { selector: '.cta-button', path: 'hero.ctaText' },
        { selector: '.contact-description', path: 'contact.description' }
    ];

    function enableSimpleEditing() {
        simpleEditables.forEach(({ selector }) => {
            const el = document.querySelector(selector);
            if (el) {
                el.contentEditable = true;
                el.classList.add('editable');
                el.addEventListener('input', () => {
                    markDirty();
                    notifyParentOfChanges();
                });
            }
        });

        // Skills with add/delete
        enableSkillsEditing();
    }

    function enableSkillsEditing() {
        const grid = document.querySelector('.skills-grid');
        if (!grid) return;

        // Add button
        const addBtn = document.createElement('button');
        addBtn.className = 'edit-add-btn';
        addBtn.innerHTML = '+ Add Skill';
        addBtn.onclick = () => addSkill(grid);
        grid.appendChild(addBtn);

        // Make skills editable with delete
        grid.querySelectorAll('.skill').forEach(skill => {
            skill.contentEditable = true;
            skill.classList.add('editable');
            addDeleteButton(skill);
        });
    }

    function addSkill(grid) {
        const skill = document.createElement('div');
        skill.className = 'skill editable';
        skill.contentEditable = true;
        skill.textContent = 'New Skill';
        addDeleteButton(skill);

        const addBtn = grid.querySelector('.edit-add-btn');
        grid.insertBefore(skill, addBtn);
        skill.focus();

        // Select text
        const range = document.createRange();
        range.selectNodeContents(skill.firstChild);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);

        markDirty();
    }

    function addDeleteButton(skill) {
        const deleteBtn = document.createElement('span');
        deleteBtn.className = 'edit-delete-btn';
        deleteBtn.textContent = '×';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            skill.remove();
            markDirty();
            notifyParentOfChanges();
        };
        skill.appendChild(deleteBtn);
    }

    // ==================== DATA COLLECTION ====================
    async function collectData() {
        const data = {
            hero: {
                title: document.querySelector('.hero-title')?.textContent.trim() || '',
                subtitle: document.querySelector('.hero-subtitle')?.textContent.trim() || '',
                ctaText: document.querySelector('.cta-button')?.textContent.trim() || '',
                ctaLink: document.querySelector('.cta-button')?.getAttribute('href') || '#featured',
                social: {
                    youtube: {
                        url: document.querySelector('.social-pill.youtube')?.getAttribute('href') || '',
                        label: document.querySelector('.social-pill.youtube span')?.textContent.trim() || ''
                    }
                }
            },
            skillsTitle: document.querySelector('.hero-skills h3')?.textContent.trim() || '',
            skills: [],
            aboutBlocks: null,
            contact: [],
            milestones: []
        };

        // Collect skills
        document.querySelectorAll('.skill').forEach(skill => {
            const text = Array.from(skill.childNodes)
                .filter(n => n.nodeType === Node.TEXT_NODE)
                .map(n => n.textContent.trim())
                .join('');
            if (text) data.skills.push(text);
        });

        // Collect Editor.js blocks
        if (aboutEditor) {
            try {
                const editorData = await aboutEditor.save();
                data.aboutBlocks = editorData.blocks;
            } catch (e) {
                console.error('[Edit Mode] Failed to save editor:', e);
            }
        }

        // Collect contacts
        document.querySelectorAll('.contact-button').forEach(btn => {
            data.contact.push({
                label: btn.textContent.trim(),
                url: btn.getAttribute('href') || ''
            });
        });

        // Collect milestones
        document.querySelectorAll('.milestone').forEach(milestone => {
            const year = milestone.querySelector('.milestone-year')?.textContent.trim();
            const title = milestone.querySelector('.milestone-card h3')?.textContent.trim();
            const desc = milestone.querySelector('.milestone-card p:not(.milestone-label)')?.textContent.trim();
            if (title || desc) {
                data.milestones.push({ year, title, description: desc });
            }
        });

        return data;
    }

    // ==================== AI INTEGRATION ====================
    function createAIButton() {
        const aiBtn = document.createElement('button');
        aiBtn.id = 'ai-assist-btn';
        aiBtn.className = 'ai-assist-btn';
        aiBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>
            AI Assist
        `;
        aiBtn.onclick = showAIModal;
        document.body.appendChild(aiBtn);
    }

    function showAIModal() {
        // Remove existing modal
        document.getElementById('ai-modal')?.remove();

        const modal = document.createElement('div');
        modal.id = 'ai-modal';
        modal.className = 'ai-modal';
        modal.innerHTML = `
            <div class="ai-modal-content">
                <div class="ai-modal-header">
                    <h3>AI Assistant</h3>
                    <button class="ai-modal-close" onclick="this.closest('.ai-modal').remove()">×</button>
                </div>
                <div class="ai-modal-body">
                    <p>What would you like AI to help with?</p>
                    <textarea id="ai-prompt" placeholder="e.g., 'Write a professional bio for a high school maker' or 'Add a skills section about woodworking'"></textarea>
                    <div class="ai-suggestions">
                        <button class="ai-suggestion" data-prompt="Rewrite my bio to sound more professional">More professional</button>
                        <button class="ai-suggestion" data-prompt="Make my bio more casual and friendly">More casual</button>
                        <button class="ai-suggestion" data-prompt="Add a paragraph about my passion for making things">Add passion paragraph</button>
                        <button class="ai-suggestion" data-prompt="Suggest 5 relevant skills for a maker/builder">Suggest skills</button>
                    </div>
                </div>
                <div class="ai-modal-footer">
                    <button class="ai-cancel-btn" onclick="this.closest('.ai-modal').remove()">Cancel</button>
                    <button class="ai-generate-btn" onclick="generateWithAI()">Generate</button>
                </div>
                <div class="ai-loading" style="display:none">
                    <div class="ai-spinner"></div>
                    <span>AI is thinking...</span>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Suggestion button handlers
        modal.querySelectorAll('.ai-suggestion').forEach(btn => {
            btn.onclick = () => {
                document.getElementById('ai-prompt').value = btn.dataset.prompt;
            };
        });

        // Focus textarea
        document.getElementById('ai-prompt').focus();
    }

    // Make generateWithAI globally accessible
    window.generateWithAI = async function() {
        const prompt = document.getElementById('ai-prompt').value.trim();
        if (!prompt) return;

        const modal = document.getElementById('ai-modal');
        const loading = modal.querySelector('.ai-loading');
        const footer = modal.querySelector('.ai-modal-footer');

        loading.style.display = 'flex';
        footer.style.display = 'none';

        try {
            // Get current content for context
            const currentData = await collectData();

            const response = await fetch(`${adminUrl}/api/ai/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                },
                credentials: 'include',
                body: JSON.stringify({
                    prompt,
                    currentContent: currentData,
                    section: 'about'
                })
            });

            if (!response.ok) throw new Error('AI request failed');

            const result = await response.json();
            console.log('[AI] Generated:', result);

            // Apply AI-generated blocks
            if (result.blocks && aboutEditor) {
                // Get current blocks and add new ones
                const currentBlocks = (await aboutEditor.save()).blocks;
                const newBlocks = [...currentBlocks, ...result.blocks];

                // Clear and reinitialize editor with new content
                aboutEditor.destroy();
                aboutEditor = new EditorJS({
                    holder: 'about-editor',
                    tools: {
                        header: { class: Header, config: { levels: [2, 3, 4], defaultLevel: 3 } },
                        list: { class: List, inlineToolbar: true },
                        quote: { class: Quote },
                        delimiter: Delimiter
                    },
                    data: { blocks: result.replaceAll ? result.blocks : newBlocks },
                    onChange: () => { markDirty(); notifyParentOfChanges(); }
                });
                await aboutEditor.isReady;
                markDirty();
            }

            // Apply suggested skills if provided
            if (result.skills) {
                const grid = document.querySelector('.skills-grid');
                if (grid) {
                    result.skills.forEach(skillText => {
                        const skill = document.createElement('div');
                        skill.className = 'skill editable';
                        skill.contentEditable = true;
                        skill.textContent = skillText;
                        addDeleteButton(skill);
                        const addBtn = grid.querySelector('.edit-add-btn');
                        grid.insertBefore(skill, addBtn);
                    });
                    markDirty();
                }
            }

            modal.remove();
            notifyParentOfChanges();

        } catch (err) {
            console.error('[AI] Error:', err);
            alert('AI generation failed: ' + err.message);
            loading.style.display = 'none';
            footer.style.display = 'flex';
        }
    };

    // ==================== THEME/LAYOUT HANDLING ====================
    function updateTheme(themeName) {
        const themeId = 'dynamic-theme-css';
        let themeLink = document.getElementById(themeId);
        if (themeName === 'default' || !themeName) {
            if (themeLink) themeLink.remove();
        } else {
            if (!themeLink) {
                themeLink = document.createElement('link');
                themeLink.id = themeId;
                themeLink.rel = 'stylesheet';
                document.head.appendChild(themeLink);
            }
            themeLink.href = `themes/${themeName}.css?v=${Date.now()}`;
        }
    }

    function updateLayout(layoutName) {
        const layoutId = 'dynamic-layout-css';
        let layoutLink = document.getElementById(layoutId);
        document.body.classList.forEach(cls => {
            if (cls.startsWith('layout-')) document.body.classList.remove(cls);
        });
        if (layoutName === 'default' || !layoutName) {
            if (layoutLink) layoutLink.remove();
        } else {
            document.body.classList.add(`layout-${layoutName}`);
            if (!layoutLink) {
                layoutLink = document.createElement('link');
                layoutLink.id = layoutId;
                layoutLink.rel = 'stylesheet';
                document.head.appendChild(layoutLink);
            }
            layoutLink.href = `layouts/${layoutName}.css?v=${Date.now()}`;
        }
    }

    // ==================== PARENT COMMUNICATION ====================
    function markDirty() {
        isDirty = true;
    }

    function notifyParent(type, data) {
        if (window.parent && window.parent !== window) {
            window.parent.postMessage({ type, data }, '*');
        }
    }

    async function notifyParentOfChanges() {
        const data = await collectData();
        notifyParent('content-changed', data);
    }

    function setupParentCommunication() {
        window.addEventListener('message', (event) => {
            const { type, path, value, data } = event.data || {};

            if (type === 'update-content') {
                if (path === 'theme') updateTheme(value);
                else if (path === 'layout') updateLayout(value);
            }

            if (type === 'set-content' && data) {
                // Handle content updates from parent
            }
        });

        // Notify parent when ready
        setTimeout(async () => {
            notifyParent('edit-mode-ready', await collectData());
        }, 1000);
    }

    // ==================== STYLES ====================
    function addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Editable elements */
            .editable {
                outline: 2px dashed transparent;
                outline-offset: 4px;
                transition: outline-color 0.2s, background-color 0.2s;
                cursor: text;
                min-width: 20px;
                min-height: 1em;
            }
            .editable:hover { outline-color: rgba(99, 102, 241, 0.4); }
            .editable:focus {
                outline-color: #6366f1;
                outline-style: solid;
                background-color: rgba(99, 102, 241, 0.1);
            }

            /* Skill editing */
            .skill.editable { position: relative; padding-right: 24px !important; }
            .edit-delete-btn {
                position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
                width: 16px; height: 16px; display: flex; align-items: center; justify-content: center;
                background: #ef4444; color: white; border-radius: 50%; font-size: 12px;
                cursor: pointer; opacity: 0; transition: opacity 0.2s;
            }
            .skill.editable:hover .edit-delete-btn { opacity: 1; }
            .edit-add-btn {
                background: transparent; border: 2px dashed rgba(255,255,255,0.3);
                color: rgba(255,255,255,0.6); padding: 0.5rem 1rem; border-radius: 20px;
                cursor: pointer; font-size: 0.85rem; transition: all 0.2s;
            }
            .edit-add-btn:hover { border-color: rgba(255,255,255,0.6); color: white; }

            /* Editor.js container */
            #about-editor {
                background: rgba(255,255,255,0.05);
                border-radius: 12px;
                padding: 1rem;
                min-height: 200px;
            }
            #about-editor .ce-block__content { max-width: 100%; }
            #about-editor .ce-toolbar__content { max-width: 100%; }
            #about-editor .codex-editor__redactor { padding-bottom: 100px !important; }

            /* AI Assist Button */
            .ai-assist-btn {
                position: fixed; bottom: 2rem; right: 2rem; z-index: 99998;
                display: flex; align-items: center; gap: 0.5rem;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white; border: none; padding: 0.75rem 1.25rem;
                border-radius: 50px; font-weight: 600; font-size: 0.9rem;
                cursor: pointer; box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
                transition: all 0.2s;
            }
            .ai-assist-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(99, 102, 241, 0.5); }

            /* AI Modal */
            .ai-modal {
                position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.7); z-index: 99999;
                display: flex; align-items: center; justify-content: center;
                animation: fadeIn 0.2s ease;
            }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            .ai-modal-content {
                background: white; border-radius: 16px; width: 90%; max-width: 500px;
                box-shadow: 0 25px 50px rgba(0,0,0,0.3); overflow: hidden;
            }
            .ai-modal-header {
                display: flex; justify-content: space-between; align-items: center;
                padding: 1rem 1.5rem; border-bottom: 1px solid #e5e7eb;
            }
            .ai-modal-header h3 { margin: 0; color: #1f2937; }
            .ai-modal-close {
                background: none; border: none; font-size: 1.5rem;
                color: #6b7280; cursor: pointer;
            }
            .ai-modal-body { padding: 1.5rem; }
            .ai-modal-body p { margin: 0 0 1rem; color: #4b5563; }
            .ai-modal-body textarea {
                width: 100%; height: 100px; padding: 0.75rem; border: 1px solid #d1d5db;
                border-radius: 8px; font-size: 0.95rem; resize: none;
                font-family: inherit;
            }
            .ai-modal-body textarea:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.1); }
            .ai-suggestions {
                display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem;
            }
            .ai-suggestion {
                background: #f3f4f6; border: 1px solid #e5e7eb; padding: 0.5rem 0.75rem;
                border-radius: 20px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s;
            }
            .ai-suggestion:hover { background: #e5e7eb; border-color: #6366f1; }
            .ai-modal-footer {
                display: flex; justify-content: flex-end; gap: 0.75rem;
                padding: 1rem 1.5rem; border-top: 1px solid #e5e7eb;
            }
            .ai-cancel-btn {
                padding: 0.6rem 1.25rem; border: 1px solid #d1d5db;
                background: white; border-radius: 8px; cursor: pointer;
            }
            .ai-generate-btn {
                padding: 0.6rem 1.25rem; background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;
            }
            .ai-loading {
                display: flex; align-items: center; justify-content: center; gap: 0.75rem;
                padding: 2rem; color: #6366f1;
            }
            .ai-spinner {
                width: 24px; height: 24px; border: 3px solid #e5e7eb;
                border-top-color: #6366f1; border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
        `;
        document.head.appendChild(style);
    }

    // ==================== INITIALIZATION ====================
    async function init() {
        addStyles();

        // Load Editor.js
        await loadEditorJS();

        // Initialize editors
        await initAboutEditor();
        enableSimpleEditing();

        // Add AI button
        createAIButton();

        // Setup communication
        setupParentCommunication();

        // Warn before leaving with unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (isDirty) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        console.log('[Edit Mode] Ready with Editor.js + AI');
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
