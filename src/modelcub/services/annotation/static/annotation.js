// src/modelcub/services/annotation/static/annotation.js
// Complete Annotation Studio Implementation

class AnnotationStudio {
    constructor() {
        this.canvas = document.getElementById('annotationCanvas');
        this.ctx = this.canvas.getContext('2d');

        // State
        this.images = [];
        this.currentIndex = 0;
        this.currentImage = null;
        this.annotations = [];
        this.selectedClass = null;
        this.currentTool = 'bbox';
        this.isDrawing = false;
        this.startPoint = null;
        this.currentAnnotation = null;
        this.selectedAnnotation = null;
        this.showGrid = false;
        this.showLabels = true;
        this.autoSave = true;
        this.classes = [];

        // History for undo/redo
        this.history = [];
        this.historyIndex = -1;

        // Shortcuts
        this.shortcuts = {};
        this.toolCycle = ['bbox', 'polygon', 'select'];
        this.currentToolIndex = 0;

        // Clipboard
        this.clipboard = null;

        this.init();
    }

    async init() {
        try {
            const debugResponse = await fetch('/api/debug');
            const debugInfo = await debugResponse.json();
            console.log('Debug info:', debugInfo);

            await this.loadImages();
            await this.loadClasses();
            await this.loadShortcuts();
            this.setupEventListeners();
            this.setupKeyboardShortcuts();
            this.setupClassManagement();
            this.setupShortcutsModal();

            if (this.images.length > 0) {
                await this.loadImage(0);
            } else {
                this.showError('No images found in data directory');
            }
        } catch (error) {
            console.error('Initialization error:', error);
            this.showError('Failed to initialize: ' + error.message);
        } finally {
            document.getElementById('loadingScreen').style.display = 'none';
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        if (!errorDiv) {
            const canvas = document.getElementById('annotationCanvas');
            canvas.style.display = 'none';
            const wrapper = canvas.parentElement;
            const error = document.createElement('div');
            error.className = 'error-message';
            error.textContent = message;
            wrapper.appendChild(error);
        } else {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

    async loadImages() {
        try {
            const response = await fetch('/api/images');
            if (!response.ok) {
                throw new Error('Failed to load images: ' + response.statusText);
            }

            this.images = await response.json();
            console.log('Loaded images:', this.images.length);

            document.getElementById('totalImages').textContent = this.images.length;
            document.getElementById('totalCount').textContent = this.images.length;

            const imageList = document.getElementById('imageList');
            imageList.innerHTML = '';

            this.images.forEach((img, index) => {
                const item = document.createElement('div');
                item.className = 'image-item';
                item.dataset.index = index;

                const name = document.createElement('div');
                name.className = 'image-item-name';
                name.textContent = img.name;
                item.appendChild(name);

                if (img.has_annotations) {
                    const badge = document.createElement('div');
                    badge.className = 'annotation-badge';
                    badge.textContent = '✓';
                    item.appendChild(badge);
                }

                item.addEventListener('click', () => this.loadImage(index));
                imageList.appendChild(item);
            });

            await this.updateStats();
        } catch (error) {
            console.error('Failed to load images:', error);
            this.showError('Failed to load images: ' + error.message);
        }
    }

    async loadClasses() {
        try {
            const response = await fetch('/api/classes');
            this.classes = await response.json();
            this.updateClassButtons();
        } catch (error) {
            console.error('Failed to load classes:', error);
            this.classes = ['object'];
        }
    }

    async loadShortcuts() {
        try {
            const response = await fetch('/api/shortcuts');
            this.shortcuts = await response.json();
        } catch (error) {
            console.error('Failed to load shortcuts:', error);
        }
    }

    updateClassButtons() {
        const classGrid = document.getElementById('classGrid');
        classGrid.innerHTML = '';

        this.classes.forEach((cls, index) => {
            const btn = document.createElement('button');
            btn.className = 'class-btn';
            btn.textContent = index < 9 ? `${index + 1}. ${cls}` : cls;
            btn.title = index < 9 ? `Press ${index + 1} to select` : '';
            btn.addEventListener('click', () => this.selectClass(cls, btn));
            classGrid.appendChild(btn);
        });

        if (this.selectedClass && this.classes.includes(this.selectedClass)) {
            const btns = classGrid.querySelectorAll('.class-btn');
            const index = this.classes.indexOf(this.selectedClass);
            this.selectClass(this.selectedClass, btns[index]);
        } else if (this.classes.length > 0) {
            const firstBtn = classGrid.querySelector('.class-btn');
            this.selectClass(this.classes[0], firstBtn);
        }
    }

    selectClass(cls, btn) {
        this.selectedClass = cls;
        document.querySelectorAll('.class-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        this.updateStatusBar();
    }

    async loadImage(index) {
        if (index < 0 || index >= this.images.length) return;

        if (this.autoSave && this.currentImage) {
            await this.saveAnnotations();
        }

        this.currentIndex = index;
        const imageData = this.images[index];

        console.log('Loading image:', imageData);

        document.querySelectorAll('.image-item').forEach(item => {
            item.classList.toggle('active', parseInt(item.dataset.index) === index);
        });

        const img = new Image();
        img.crossOrigin = 'anonymous';

        img.onload = () => {
            console.log('Image loaded successfully');
            this.currentImage = img;
            this.resizeCanvas();
            this.render();
            this.loadAnnotations(imageData.id);
        };

        img.onerror = (error) => {
            console.error('Failed to load image:', error);
            this.showError(`Failed to load image: ${imageData.name}`);
        };

        const imageUrl = `/api/image/${encodeURIComponent(imageData.id)}`;
        console.log('Image URL:', imageUrl);
        img.src = imageUrl;

        document.getElementById('currentIndex').textContent = index + 1;
        document.getElementById('prevBtn').disabled = index === 0;
        document.getElementById('nextBtn').disabled = index === this.images.length - 1;
    }

    async loadAnnotations(imageId) {
        try {
            const response = await fetch(`/api/annotations/${encodeURIComponent(imageId)}`);
            const data = await response.json();
            this.annotations = data.annotations || [];

            // Initialize history
            this.history = [JSON.stringify(this.annotations)];
            this.historyIndex = 0;

            this.updateAnnotationList();
            this.render();
        } catch (error) {
            console.error('Failed to load annotations:', error);
            this.annotations = [];
        }
    }

    async saveAnnotations() {
        if (this.currentIndex >= this.images.length) return;

        const imageData = this.images[this.currentIndex];

        try {
            const response = await fetch(`/api/annotations/${encodeURIComponent(imageData.id)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    annotations: this.annotations,
                    width: this.canvas.width,
                    height: this.canvas.height
                })
            });

            if (!response.ok) {
                throw new Error('Failed to save annotations');
            }

            imageData.has_annotations = this.annotations.length > 0;

            const item = document.querySelector(`.image-item[data-index="${this.currentIndex}"]`);
            if (item) {
                const badge = item.querySelector('.annotation-badge');
                if (this.annotations.length > 0 && !badge) {
                    const newBadge = document.createElement('div');
                    newBadge.className = 'annotation-badge';
                    newBadge.textContent = '✓';
                    item.appendChild(newBadge);
                } else if (this.annotations.length === 0 && badge) {
                    badge.remove();
                }
            }

            await this.updateStats();
        } catch (error) {
            console.error('Failed to save annotations:', error);
        }
    }

    async updateStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();

            document.getElementById('annotatedImages').textContent = stats.annotated_images;
            document.getElementById('progressPercent').textContent =
                Math.round(stats.completion_rate) + '%';
        } catch (error) {
            console.error('Failed to update stats:', error);
        }
    }

    resizeCanvas() {
        if (!this.currentImage) return;

        const container = this.canvas.parentElement;
        const maxWidth = container.clientWidth - 40;
        const maxHeight = container.clientHeight - 40;

        const scale = Math.min(
            maxWidth / this.currentImage.width,
            maxHeight / this.currentImage.height,
            1
        );

        this.canvas.width = this.currentImage.width * scale;
        this.canvas.height = this.currentImage.height * scale;

        this.scale = scale;
    }

    render() {
        if (!this.currentImage) return;

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.currentImage, 0, 0, this.canvas.width, this.canvas.height);

        if (this.showGrid) {
            this.drawGrid();
        }

        this.annotations.forEach(ann => {
            this.drawAnnotation(ann, ann === this.selectedAnnotation);
        });

        if (this.currentAnnotation) {
            this.drawAnnotation(this.currentAnnotation, true);
        }
    }

    drawGrid() {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;

        const gridSize = 50;

        for (let x = 0; x <= this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        for (let y = 0; y <= this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    drawAnnotation(ann, isSelected) {
        const color = isSelected ? '#10b981' : '#6366f1';

        if (ann.type === 'bbox') {
            const [x1, y1] = ann.points[0];
            const [x2, y2] = ann.points[1];

            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

            if (this.showLabels) {
                this.ctx.fillStyle = color;
                this.ctx.fillRect(x1, y1 - 20, ann.label.length * 8 + 10, 20);
                this.ctx.fillStyle = 'white';
                this.ctx.font = '12px sans-serif';
                this.ctx.fillText(ann.label, x1 + 5, y1 - 5);
            }

            if (isSelected) {
                const corners = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]];
                corners.forEach(([x, y]) => {
                    this.ctx.fillStyle = color;
                    this.ctx.fillRect(x - 4, y - 4, 8, 8);
                });
            }
        } else if (ann.type === 'polygon') {
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            ann.points.forEach((point, i) => {
                if (i === 0) {
                    this.ctx.moveTo(point[0], point[1]);
                } else {
                    this.ctx.lineTo(point[0], point[1]);
                }
            });
            this.ctx.closePath();
            this.ctx.stroke();

            if (this.showLabels && ann.points.length > 0) {
                const [x, y] = ann.points[0];
                this.ctx.fillStyle = color;
                this.ctx.fillRect(x, y - 20, ann.label.length * 8 + 10, 20);
                this.ctx.fillStyle = 'white';
                this.ctx.font = '12px sans-serif';
                this.ctx.fillText(ann.label, x + 5, y - 5);
            }

            if (isSelected) {
                ann.points.forEach(([x, y]) => {
                    this.ctx.fillStyle = color;
                    this.ctx.fillRect(x - 4, y - 4, 8, 8);
                });
            }
        }
    }

    updateAnnotationList() {
        const list = document.getElementById('annotationList');
        list.innerHTML = '';

        if (this.annotations.length === 0) {
            list.innerHTML = '<div style="color: var(--text-dim); text-align: center; padding: 20px;">No annotations yet</div>';
            return;
        }

        this.annotations.forEach((ann, index) => {
            const item = document.createElement('div');
            item.className = 'annotation-item';

            const label = document.createElement('div');
            label.className = 'annotation-label';
            label.textContent = `${ann.label} (${ann.type})`;
            item.appendChild(label);

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.textContent = 'Delete';
            deleteBtn.addEventListener('click', () => this.deleteAnnotation(index));
            item.appendChild(deleteBtn);

            item.addEventListener('click', () => {
                this.selectedAnnotation = ann;
                this.render();
            });

            list.appendChild(item);
        });
    }

    deleteAnnotation(index) {
        this.saveState();
        this.annotations.splice(index, 1);
        this.selectedAnnotation = null;
        this.updateAnnotationList();
        this.render();

        if (this.autoSave) {
            this.saveAnnotations();
        }
    }

    saveState() {
        const state = JSON.stringify(this.annotations);

        if (this.historyIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.historyIndex + 1);
        }

        this.history.push(state);
        this.historyIndex++;

        if (this.history.length > 50) {
            this.history.shift();
            this.historyIndex--;
        }
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.annotations = JSON.parse(this.history[this.historyIndex]);
            this.updateAnnotationList();
            this.render();
            this.showNotification('Undo');

            if (this.autoSave) {
                this.saveAnnotations();
            }
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.annotations = JSON.parse(this.history[this.historyIndex]);
            this.updateAnnotationList();
            this.render();
            this.showNotification('Redo');

            if (this.autoSave) {
                this.saveAnnotations();
            }
        }
    }

    cycleTool() {
        this.currentToolIndex = (this.currentToolIndex + 1) % this.toolCycle.length;
        const tool = this.toolCycle[this.currentToolIndex];

        const toolBtn = document.querySelector(`[data-tool="${tool}"]`);
        if (toolBtn) {
            toolBtn.click();
            this.showNotification(`Tool: ${tool.toUpperCase()}`);
        }
    }

    selectClassByIndex(index) {
        if (index >= 0 && index < this.classes.length) {
            const classGrid = document.getElementById('classGrid');
            const btns = classGrid.querySelectorAll('.class-btn');
            this.selectClass(this.classes[index], btns[index]);
            this.showNotification(`Class: ${this.classes[index]}`);
        }
    }

    toggleLabels() {
        this.showLabels = !this.showLabels;
        this.render();
        this.showNotification(this.showLabels ? 'Labels ON' : 'Labels OFF');
    }

    fitToScreen() {
        if (this.currentImage) {
            this.resizeCanvas();
            this.render();
            this.showNotification('Fit to screen');
        }
    }

    updateStatusBar() {
        document.getElementById('statusTool').textContent =
            this.currentTool.charAt(0).toUpperCase() + this.currentTool.slice(1);
        document.getElementById('statusClass').textContent =
            this.selectedClass || 'None';
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: var(--secondary);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }

    setupShortcutsModal() {
        const modal = document.getElementById('shortcutsModal');
        const closeBtn = document.getElementById('closeShortcutsModal');
        const grid = document.getElementById('shortcutsGrid');

        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });

        for (const [category, shortcuts] of Object.entries(this.shortcuts)) {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'shortcuts-category';

            const title = document.createElement('h3');
            title.textContent = category;
            categoryDiv.appendChild(title);

            shortcuts.forEach(shortcut => {
                const item = document.createElement('div');
                item.className = 'shortcut-item';

                const key = document.createElement('span');
                key.className = 'shortcut-key';
                let keyText = shortcut.key;
                if (shortcut.modifiers && shortcut.modifiers.length) {
                    keyText = shortcut.modifiers.join('+') + '+' + keyText;
                }
                key.textContent = keyText;

                const desc = document.createElement('span');
                desc.className = 'shortcut-desc';
                desc.textContent = shortcut.description;

                item.appendChild(desc);
                item.appendChild(key);
                categoryDiv.appendChild(item);
            });

            grid.appendChild(categoryDiv);
        }
    }

    setupClassManagement() {
        const modal = document.getElementById('classModal');
        const openBtn = document.getElementById('manageClassesBtn');
        const closeBtn = document.getElementById('closeClassModal');
        const addBtn = document.getElementById('addClassBtn');
        const input = document.getElementById('newClassName');

        openBtn.addEventListener('click', () => {
            this.showClassManager();
        });

        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });

        addBtn.addEventListener('click', () => {
            this.addClass(input.value);
        });

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addClass(input.value);
            }
        });
    }

    async showClassManager() {
        const modal = document.getElementById('classModal');
        const classList = document.getElementById('classList');

        classList.innerHTML = '';

        this.classes.forEach((cls, index) => {
            const item = document.createElement('div');
            item.className = 'class-list-item';
            item.draggable = true;

            const number = document.createElement('div');
            number.className = 'class-number';
            number.textContent = index < 9 ? (index + 1) : '';

            const name = document.createElement('input');
            name.className = 'class-name';
            name.value = cls;
            name.readOnly = true;

            const actions = document.createElement('div');
            actions.className = 'class-actions';

            const removeBtn = document.createElement('button');
            removeBtn.className = 'btn-remove';
            removeBtn.textContent = 'Remove';
            removeBtn.addEventListener('click', () => this.removeClass(cls));

            actions.appendChild(removeBtn);
            item.appendChild(number);
            item.appendChild(name);
            item.appendChild(actions);
            classList.appendChild(item);

            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', index);
                item.style.opacity = '0.4';
            });

            item.addEventListener('dragend', (e) => {
                item.style.opacity = '1';
            });

            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
            });

            item.addEventListener('drop', async (e) => {
                e.preventDefault();
                const fromIndex = parseInt(e.dataTransfer.getData('text/plain'));
                const toIndex = index;

                if (fromIndex !== toIndex) {
                    await this.reorderClasses(fromIndex, toIndex);
                }
            });
        });

        modal.classList.add('active');
    }

    async addClass(name) {
        name = name.trim();
        if (!name) return;

        try {
            const response = await fetch('/api/classes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });

            if (response.ok) {
                const data = await response.json();
                this.classes = data.classes;
                this.updateClassButtons();
                this.showClassManager();
                document.getElementById('newClassName').value = '';
                this.showNotification(`Added class: ${name}`);
            } else {
                const error = await response.json();
                alert(error.error || 'Failed to add class');
            }
        } catch (error) {
            console.error('Failed to add class:', error);
        }
    }

    async removeClass(name) {
        if (!confirm(`Remove class "${name}"?`)) return;

        try {
            const response = await fetch(`/api/classes/${encodeURIComponent(name)}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                const data = await response.json();
                this.classes = data.classes;
                this.updateClassButtons();
                this.showClassManager();
                this.showNotification(`Removed class: ${name}`);
            }
        } catch (error) {
            console.error('Failed to remove class:', error);
        }
    }

    async reorderClasses(fromIndex, toIndex) {
        const newOrder = [...this.classes];
        const [moved] = newOrder.splice(fromIndex, 1);
        newOrder.splice(toIndex, 0, moved);

        try {
            const response = await fetch('/api/classes/reorder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ classes: newOrder })
            });

            if (response.ok) {
                const data = await response.json();
                this.classes = data.classes;
                this.updateClassButtons();
                this.showClassManager();
            }
        } catch (error) {
            console.error('Failed to reorder classes:', error);
        }
    }

    setupEventListeners() {
        document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tool-btn[data-tool]').forEach(b =>
                    b.classList.remove('active'));
                btn.classList.add('active');
                this.currentTool = btn.dataset.tool;
                this.canvas.style.cursor = this.currentTool === 'select' ? 'pointer' : 'crosshair';
                this.updateStatusBar();
            });
        });

        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));

        document.getElementById('prevBtn').addEventListener('click', () => {
            this.loadImage(this.currentIndex - 1);
        });

        document.getElementById('nextBtn').addEventListener('click', () => {
            this.loadImage(this.currentIndex + 1);
        });

        document.getElementById('clearBtn').addEventListener('click', () => {
            if (confirm('Clear all annotations for this image?')) {
                this.saveState();
                this.annotations = [];
                this.updateAnnotationList();
                this.render();
                if (this.autoSave) {
                    this.saveAnnotations();
                }
            }
        });

        document.getElementById('gridBtn').addEventListener('click', () => {
            this.showGrid = !this.showGrid;
            document.getElementById('gridBtn').classList.toggle('active', this.showGrid);
            this.render();
        });

        document.getElementById('autoSaveBtn').addEventListener('click', () => {
            this.autoSave = !this.autoSave;
            const btn = document.getElementById('autoSaveBtn');
            btn.textContent = this.autoSave ? '💾 Auto-save ON' : '💾 Auto-save OFF';
            btn.style.background = this.autoSave ? '' : 'var(--warning)';
        });

        document.querySelectorAll('.export-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const format = btn.dataset.format;
                const response = await fetch(`/api/export/${format}`);

                if (format === 'coco') {
                    const data = await response.json();
                    const blob = new Blob([JSON.stringify(data, null, 2)],
                        { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `annotations_${format}.json`;
                    a.click();
                } else {
                    const data = await response.text();
                    const blob = new Blob([data], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `annotations_${format}.txt`;
                    a.click();
                }
            });
        });

        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.render();
        });

        document.getElementById('shortcutsHint').addEventListener('click', () => {
            document.getElementById('shortcutsModal').classList.add('active');
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            const key = e.key;
            const ctrl = e.ctrlKey || e.metaKey;
            const shift = e.shiftKey;

            if (key === '?' || key === '/') {
                e.preventDefault();
                document.getElementById('shortcutsModal').classList.add('active');
                return;
            }

            if (key === 'ArrowLeft' && this.currentIndex > 0) {
                e.preventDefault();
                this.loadImage(this.currentIndex - 1);
            } else if (key === 'ArrowRight' && this.currentIndex < this.images.length - 1) {
                e.preventDefault();
                this.loadImage(this.currentIndex + 1);
            } else if (key === 'Home') {
                e.preventDefault();
                this.loadImage(0);
            } else if (key === 'End') {
                e.preventDefault();
                this.loadImage(this.images.length - 1);
            }

            else if (key === 'b' || key === 'B') {
                e.preventDefault();
                document.querySelector('.tool-btn[data-tool="bbox"]').click();
            } else if (key === 'p' || key === 'P') {
                e.preventDefault();
                document.querySelector('.tool-btn[data-tool="polygon"]').click();
            } else if ((key === 's' || key === 'S' || key === 'v' || key === 'V') && !ctrl) {
                e.preventDefault();
                document.querySelector('.tool-btn[data-tool="select"]').click();
            } else if (key === 'Tab') {
                e.preventDefault();
                this.cycleTool();
            }

            else if (key >= '1' && key <= '9') {
                e.preventDefault();
                const index = parseInt(key) - 1;
                this.selectClassByIndex(index);
            }

            else if (key === 'g' || key === 'G') {
                e.preventDefault();
                document.getElementById('gridBtn').click();
            } else if (key === 'h' || key === 'H') {
                e.preventDefault();
                this.toggleLabels();
            } else if (key === 'f' || key === 'F') {
                e.preventDefault();
                this.fitToScreen();
            } else if (key === '0') {
                e.preventDefault();
                this.fitToScreen();
            }

            else if (key === 'Delete' || key === 'Backspace') {
                e.preventDefault();
                if (this.selectedAnnotation) {
                    const index = this.annotations.indexOf(this.selectedAnnotation);
                    if (index !== -1) {
                        this.deleteAnnotation(index);
                    }
                }
            } else if (key === 'Escape') {
                e.preventDefault();
                this.selectedAnnotation = null;
                this.currentAnnotation = null;
                this.isDrawing = false;
                this.render();
            } else if (key === 'a' || key === 'A' && !ctrl) {
                e.preventDefault();
                this.showNotification('Select all');
            }

            else if (ctrl && key === 'z') {
                e.preventDefault();
                if (shift) {
                    this.redo();
                } else {
                    this.undo();
                }
            } else if (ctrl && key === 'y') {
                e.preventDefault();
                this.redo();
            } else if (ctrl && key === 's') {
                e.preventDefault();
                this.saveAnnotations();
                this.showNotification('Saved');
            }

            this.updateStatusBar();
        });
    }

    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (this.currentTool === 'select') {
            this.selectedAnnotation = this.getAnnotationAt(x, y);
            this.render();
        } else if (this.currentTool === 'bbox') {
            if (!this.selectedClass) {
                alert('Please select a class first');
                return;
            }

            this.isDrawing = true;
            this.startPoint = [x, y];
            this.currentAnnotation = {
                id: 'ann_' + Date.now(),
                type: 'bbox',
                label: this.selectedClass,
                points: [[x, y], [x, y]],
                confidence: 1.0
            };
        } else if (this.currentTool === 'polygon') {
            if (!this.selectedClass) {
                alert('Please select a class first');
                return;
            }

            if (!this.currentAnnotation) {
                this.currentAnnotation = {
                    id: 'ann_' + Date.now(),
                    type: 'polygon',
                    label: this.selectedClass,
                    points: [],
                    confidence: 1.0
                };
            }

            this.currentAnnotation.points.push([x, y]);

            if (e.button === 2 || (this.currentAnnotation.points.length > 2 &&
                this.isNearFirstPoint(x, y))) {
                this.saveState();
                this.annotations.push(this.currentAnnotation);
                this.currentAnnotation = null;
                this.updateAnnotationList();
                if (this.autoSave) {
                    this.saveAnnotations();
                }
            }

            this.render();
        }
    }

    handleMouseMove(e) {
        if (!this.isDrawing || !this.currentAnnotation) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (this.currentTool === 'bbox') {
            this.currentAnnotation.points[1] = [x, y];
            this.render();
        }
    }

    handleMouseUp(e) {
        if (!this.isDrawing || !this.currentAnnotation) return;

        if (this.currentTool === 'bbox') {
            this.isDrawing = false;

            const [x1, y1] = this.currentAnnotation.points[0];
            const [x2, y2] = this.currentAnnotation.points[1];

            if (Math.abs(x2 - x1) > 10 && Math.abs(y2 - y1) > 10) {
                this.currentAnnotation.points = [
                    [Math.min(x1, x2), Math.min(y1, y2)],
                    [Math.max(x1, x2), Math.max(y1, y2)]
                ];

                this.saveState();
                this.annotations.push(this.currentAnnotation);
                this.updateAnnotationList();

                if (this.autoSave) {
                    this.saveAnnotations();
                }
            }

            this.currentAnnotation = null;
            this.render();
        }
    }

    getAnnotationAt(x, y) {
        for (let i = this.annotations.length - 1; i >= 0; i--) {
            const ann = this.annotations[i];

            if (ann.type === 'bbox') {
                const [x1, y1] = ann.points[0];
                const [x2, y2] = ann.points[1];

                if (x >= x1 && x <= x2 && y >= y1 && y <= y2) {
                    return ann;
                }
            } else if (ann.type === 'polygon') {
                if (this.isPointInPolygon(x, y, ann.points)) {
                    return ann;
                }
            }
        }

        return null;
    }

    isPointInPolygon(x, y, points) {
        let inside = false;

        for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
            const xi = points[i][0], yi = points[i][1];
            const xj = points[j][0], yj = points[j][1];

            const intersect = ((yi > y) !== (yj > y))
                && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);

            if (intersect) inside = !inside;
        }

        return inside;
    }

    isNearFirstPoint(x, y) {
        if (!this.currentAnnotation || this.currentAnnotation.points.length === 0) {
            return false;
        }

        const [fx, fy] = this.currentAnnotation.points[0];
        const distance = Math.sqrt((x - fx) ** 2 + (y - fy) ** 2);
        return distance < 10;
    }
}

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

const studio = new AnnotationStudio();