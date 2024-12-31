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
    const solveButton = document.getElementById('solveBtn');
    const generateButton = document.getElementById('generateBtn');
    
    if (!queueDisplay) return;
    
    if (selectedQuestions.size > 0) {
        queueDisplay.innerHTML = Array.from(selectedQuestions)
            .map(q => `<div class="selected-question p-2 border-bottom">${q}</div>`)
            .join('');
        if (solveButton) solveButton.disabled = false;
        if (generateButton) generateButton.disabled = false;
    } else {
        queueDisplay.innerHTML = '<p class="text-muted">No questions selected.</p>';
        if (solveButton) solveButton.disabled = true;
        if (generateButton) generateButton.disabled = true;
    }
    
    sessionStorage.setItem('selectedQuestions', JSON.stringify(Array.from(selectedQuestions)));
}

// Handle question selection
function toggleQuestion(checkbox) {
    const label = checkbox.nextElementSibling;
    let questionText = label.textContent.trim();
    
    // If there's a main question context (in parentheses), include it
    const mainQuestion = label.querySelector('.text-muted');
    if (mainQuestion) {
        const context = mainQuestion.textContent.replace(/[()]/g, '').trim();
        questionText = `${questionText} - ${context}`;
    }
    
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

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded, initializing exercise display');

    // Exercise collapse/expand handling
    document.querySelectorAll('.exercise-header').forEach(header => {
        console.log('Found exercise header:', header.textContent);
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            if (content) {
                const isExpanded = content.style.display === 'block';
                content.style.display = isExpanded ? 'none' : 'block';
                const icon = this.querySelector('.toggle-icon');
                if (icon) {
                    icon.textContent = isExpanded ? '+' : '-';
                }
            }
        });
    });

    // Initially show all exercise content for debugging
    document.querySelectorAll('.exercise-content').forEach(content => {
        content.style.display = 'block';
    });

    // Add checkbox event listeners
    document.querySelectorAll('.question-checkbox').forEach(checkbox => {
        console.log('Found question checkbox');
        checkbox.addEventListener('change', function() {
            const questionText = this.nextElementSibling.textContent.trim();
            console.log('Question toggled:', questionText);
            toggleQuestion(this, questionText);
        });
    });

    // Book selection handling
    const bookSelect = document.getElementById('bookSelect');
    if (bookSelect) {
        bookSelect.addEventListener('change', function() {
            console.log('Book selected:', this.value);
            handleBookSelection(this.value);
        });
    }

    // Add click handler for "Back to Questions" link
    const backLink = document.querySelector('a[href*="math_tools"]');
    if (backLink) {
        backLink.onclick = handleBackToQuestions;
    }
});

// Handle book selection
function handleBookSelection(selectedBook) {
    const chapterSelect = document.getElementById('chapterSelect');
    
    if (selectedBook && chapterSelect) {
        chapterSelect.disabled = false;
        
        fetch(`/get-chapters/${selectedBook}/`)
            .then(response => response.json())
            .then(data => {
                console.log('Received chapters:', data);
                populateChapterSelect(data.chapters);
            })
            .catch(error => {
                console.error('Error loading chapters:', error);
                chapterSelect.innerHTML = '<option value="">Error loading chapters</option>';
            });
    } else if (chapterSelect) {
        chapterSelect.disabled = true;
        chapterSelect.innerHTML = '<option value="">Select a chapter...</option>';
    }
}

// Populate chapter select
function populateChapterSelect(chapters) {
    const chapterSelect = document.getElementById('chapterSelect');
    chapterSelect.innerHTML = '<option value="">Select a chapter...</option>';
    
    chapters.forEach(chapter => {
        const option = document.createElement('option');
        option.value = chapter.id;
        option.textContent = chapter.name;
        chapterSelect.appendChild(option);
    });
}

// Update the question display
function updateQuestionDisplay() {
    console.log('Updating question display');
    const questionsContainer = document.getElementById('questionsList');
    
    if (!questionsContainer) {
        console.error('Questions container not found');
        return;
    }

    // Make sure all exercise contents are visible
    document.querySelectorAll('.exercise-content').forEach(content => {
        content.style.display = 'block';
    });

    // Make sure checkboxes are enabled
    document.querySelectorAll('.question-checkbox').forEach(checkbox => {
        checkbox.disabled = false;
    });
}


function solveSelected() {
    if (selectedQuestions.size === 0) {
        alert('Please select questions first.');
        return;
    }
    
    try {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/math-tools/solve/';
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        if (!csrfToken) {
            throw new Error('CSRF token not found');
        }
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
        
        // Add questions as JSON
        const questionsInput = document.createElement('input');
        questionsInput.type = 'hidden';
        questionsInput.name = 'questions';
        questionsInput.value = JSON.stringify(Array.from(selectedQuestions));
        form.appendChild(questionsInput);
        
        // Submit the form
        document.body.appendChild(form);
        form.submit();
    } catch (error) {
        console.error('Error submitting questions:', error);
        alert('Error submitting questions. Please try again.');
    }
}

function generateMore() {
    if (selectedQuestions.size === 0) {
        alert('Please select questions first.');
        return;
    }
    
    try {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/math-tools/generate-form/';  // Changed from /math-tools/generate/
        
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
    } catch (error) {
        console.error('Error:', error);
        alert('Error submitting form. Please try again.');
    }
}

// Clear selected questions when returning from solutions page
function handleBackToQuestions() {
    clearSelectedQuestions();
    window.location.href = document.querySelector('a[href*="math_tools"]').href;
    return false;  // Prevent default link behavior
}