// Handle dynamic form generation for templates
function initTemplateForm() {
    const addSectionBtn = document.getElementById('add-section');
    const sectionsContainer = document.getElementById('sections-container');
    
    if (addSectionBtn) {
        addSectionBtn.addEventListener('click', () => {
            const sectionIndex = sectionsContainer.children.length;
            const sectionHtml = `
                <div class="section-container mb-4 p-3 border rounded">
                    <h4>Section ${sectionIndex + 1}</h4>
                    <div class="mb-3">
                        <label class="form-label">Title</label>
                        <input type="text" class="form-control" name="sections[${sectionIndex}][title]" required>
                    </div>
                    <div class="questions-container">
                        <!-- Questions will be added here -->
                    </div>
                    <button type="button" class="btn btn-secondary add-question" data-section="${sectionIndex}">
                        Add Question
                    </button>
                </div>
            `;
            sectionsContainer.insertAdjacentHTML('beforeend', sectionHtml);
        });
    }
    
    // Delegate event handling for dynamically added elements
    document.addEventListener('click', (e) => {
        if (e.target.matches('.add-question')) {
            const sectionIndex = e.target.dataset.section;
            const questionsContainer = e.target.previousElementSibling;
            const questionIndex = questionsContainer.children.length;
            
            const questionHtml = `
                <div class="question-container mb-3">
                    <div class="mb-2">
                        <label class="form-label">Question Text</label>
                        <input type="text" class="form-control" 
                               name="sections[${sectionIndex}][questions][${questionIndex}][text]" required>
                    </div>
                    <div class="mb-2">
                        <label class="form-label">Question Type</label>
                        <select class="form-select" 
                                name="sections[${sectionIndex}][questions][${questionIndex}][type]" required>
                            <option value="text">Text</option>
                            <option value="textarea">Long Text</option>
                            <option value="number">Number</option>
                            <option value="select">Select</option>
                        </select>
                    </div>
                </div>
            `;
            questionsContainer.insertAdjacentHTML('beforeend', questionHtml);
        }
    });
}

// Handle audio player controls
function initAudioPlayers() {
    const players = document.querySelectorAll('.audio-player');
    players.forEach(player => {
        const audio = player.querySelector('audio');
        const playBtn = player.querySelector('.play-btn');
        
        if (playBtn && audio) {
            playBtn.addEventListener('click', () => {
                if (audio.paused) {
                    audio.play();
                    playBtn.textContent = 'Pause';
                } else {
                    audio.pause();
                    playBtn.textContent = 'Play';
                }
            });
        }
    });
}

// Initialize all components when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initTemplateForm();
    initAudioPlayers();
});
