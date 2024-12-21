// Store selected questions in session storage
let selectedQuestions = new Set(
    JSON.parse(sessionStorage.getItem('selectedQuestions')) || []
);

// Initialize MathJax
window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']]
    },
    svg: {
        fontCache: 'global'
    }
};

// Update UI based on selected questions
function updateQuestionQueue() {
    const queueDisplay = document.getElementById('selectedQuestions');
    const solveButton = document.getElementById('solveButton');
    const generateButton = document.getElementById('generateButton');
    
    if (selectedQuestions.size > 0) {
        queueDisplay.innerHTML = Array.from(selectedQuestions)
            .map(q => `<div class="selected-question">${q}</div>`)
            .join('');
        solveButton.disabled = false;
        generateButton.disabled = false;
    } else {
        queueDisplay.innerHTML = '<p>No questions selected.</p>';
        solveButton.disabled = true;
        generateButton.disabled = true;
    }
    
    // Save to session storage
    sessionStorage.setItem('selectedQuestions', JSON.stringify(Array.from(selectedQuestions)));
}

// Handle question selection
function toggleQuestion(checkbox, questionText) {
    if (checkbox.checked) {
        selectedQuestions.add(questionText);
    } else {
        selectedQuestions.delete(questionText);
    }
    updateQuestionQueue();
}

// Clear all selected questions
function clearSelectedQuestions() {
    selectedQuestions.clear();
    document.querySelectorAll('.question-checkbox').forEach(cb => cb.checked = false);
    updateQuestionQueue();
    sessionStorage.removeItem('selectedQuestions');
}

// Handle language selection change
document.querySelectorAll('input[name="language"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const chapterSelect = document.getElementById('chapterSelect');
        // Optionally trigger chapter reload based on language
        if (chapterSelect.value) {
            document.getElementById('optionsForm').submit();
        }
    });
});

// Handle chapter selection change
document.getElementById('chapterSelect')?.addEventListener('change', function() {
    document.getElementById('optionsForm').submit();
});

// Solve selected questions
function solveSelected() {
    if (selectedQuestions.size === 0) {
        alert('Please select questions first.');
        return;
    }
    
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/math-tools/solve/';
    
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
    form.appendChild(csrfInput);
    
    const questionsInput = document.createElement('input');
    questionsInput.type = 'hidden';
    questionsInput.name = 'questions';
    questionsInput.value = JSON.stringify(Array.from(selectedQuestions));
    form.appendChild(questionsInput);
    
    document.body.appendChild(form);
    form.submit();
}

// Generate more questions
function generateMore() {
    if (selectedQuestions.size === 0) {
        alert('Please select questions first.');
        return;
    }
    
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/math-tools/generate/';
    
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
    form.appendChild(csrfInput);
    
    const questionsInput = document.createElement('input');
    questionsInput.type = 'hidden';
    questionsInput.name = 'questions';
    questionsInput.value = JSON.stringify(Array.from(selectedQuestions));
    form.appendChild(questionsInput);
    
    document.body.appendChild(form);
    form.submit();
}

// Filter questions based on search input
function filterQuestions() {
    const searchInput = document.getElementById('questionSearch');
    const searchText = searchInput.value.toLowerCase();
    const questions = document.querySelectorAll('.question-item');
    
    questions.forEach(question => {
        const text = question.textContent.toLowerCase();
        if (text.includes(searchText)) {
            question.style.display = '';
        } else {
            question.style.display = 'none';
        }
    });
}

// Load saved selections on page load
document.addEventListener('DOMContentLoaded', function() {
    // Book and Chapter Select Handling
    const bookSelect = document.getElementById('bookSelect');
    const chapterSelect = document.getElementById('chapterSelect');

    if (bookSelect) {
        bookSelect.addEventListener('change', function() {
            const selectedBook = this.value;
            
            if (selectedBook) {
                // Enable chapter select
                chapterSelect.disabled = false;
                
                // Fetch chapters for selected book using AJAX
                fetch(`/get-chapters/${selectedBook}/`)
                    .then(response => response.json())
                    .then(data => {
                        // Clear existing options
                        chapterSelect.innerHTML = '<option value="">Select a chapter...</option>';
                        
                        // Add new options
                        data.chapters.forEach(chapter => {
                            const option = document.createElement('option');
                            option.value = chapter.id;
                            option.textContent = chapter.name;
                            chapterSelect.appendChild(option);
                        });
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        chapterSelect.innerHTML = '<option value="">Error loading chapters</option>';
                    });
            } else {
                // Disable and reset chapter select if no book is selected
                chapterSelect.disabled = true;
                chapterSelect.innerHTML = '<option value="">Select a chapter...</option>';
            }
        });
    }

    // Restore checked state of checkboxes
    selectedQuestions.forEach(questionText => {
        const checkbox = Array.from(document.querySelectorAll('.question-checkbox'))
            .find(cb => cb.nextElementSibling.textContent.trim() === questionText);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
    
    updateQuestionQueue();
    
    // Add search input event listener
    const searchInput = document.getElementById('questionSearch');
    if (searchInput) {
        searchInput.addEventListener('input', filterQuestions);
    }

    // Exercise collapse/expand handling
    document.querySelectorAll('.exercise-header').forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const isExpanded = content.style.display !== 'none';
            content.style.display = isExpanded ? 'none' : 'block';
            this.querySelector('.toggle-icon').textContent = isExpanded ? '+' : '-';
        });
    });

    // Add checkbox event listeners
    document.querySelectorAll('.question-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            toggleQuestion(this, this.nextElementSibling.textContent.trim());
        });
    });
});

// Handle exercise collapse/expand
document.querySelectorAll('.exercise-header').forEach(header => {
    header.addEventListener('click', function() {
        const content = this.nextElementSibling;
        const isExpanded = content.style.display !== 'none';
        content.style.display = isExpanded ? 'none' : 'block';
        this.querySelector('.toggle-icon').textContent = isExpanded ? '+' : '-';
    });
});

