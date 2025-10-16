/**
 * IELTS Listening Test JavaScript
 * Handles test flow, audio playback, and answer submission
 */

// Global variables
let currentTest = null;
let currentQuestionIndex = 0;
let currentSection = 1;
let userAnswers = {};
let flaggedQuestions = new Set();
let testTimer = null;
let timeRemaining = 1800; // 30 minutes in seconds
let testStartTime = null;
let audioURLs = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTest();
});

// ============================================================================
// TEST INITIALIZATION
// ============================================================================

async function initializeTest() {
    // Get test ID from URL or session
    const urlParams = new URLSearchParams(window.location.search);
    const testId = urlParams.get('test_id') || 'academic-listening-test-1';
    
    try {
        // Fetch test data
        const response = await fetch(`/api/listening/test/${testId}`);
        const data = await response.json();
        
        if (data.success) {
            currentTest = data.test;
            loadTest(data);
            startTimer();
        } else {
            showError('Failed to load test');
        }
    } catch (error) {
        console.error('Error loading test:', error);
        showError('Failed to load test. Please refresh the page.');
    }
}

function loadTest(data) {
    // Set test title
    document.querySelector('.test-title').textContent = data.test.title || 'IELTS Listening Test';
    
    // Store questions
    currentTest.questions = data.questions;
    
    // Initialize question grid
    initializeQuestionGrid();
    
    // Load first section audio
    loadSectionAudio(1);
    
    // Display first question
    displayQuestion(0);
    
    // Restore progress if exists
    if (data.progress && data.progress.answers) {
        userAnswers = data.progress.answers;
        updateQuestionGrid();
    }
}

// ============================================================================
// TIMER MANAGEMENT
// ============================================================================

function startTimer() {
    testStartTime = Date.now();
    
    testTimer = setInterval(() => {
        timeRemaining--;
        updateTimerDisplay();
        
        // Auto-save progress every 30 seconds
        if (timeRemaining % 30 === 0) {
            saveProgress();
        }
        
        // Warning at 5 minutes
        if (timeRemaining === 300) {
            document.getElementById('timer').classList.add('warning');
            showNotification('5 minutes remaining!', 'warning');
        }
        
        // Danger at 1 minute
        if (timeRemaining === 60) {
            document.getElementById('timer').classList.remove('warning');
            document.getElementById('timer').classList.add('danger');
            showNotification('1 minute remaining!', 'danger');
        }
        
        // Auto-submit at 0
        if (timeRemaining <= 0) {
            clearInterval(testTimer);
            autoSubmitTest();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    document.getElementById('timer').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// ============================================================================
// AUDIO MANAGEMENT
// ============================================================================

function loadSectionAudio(sectionNum) {
    const section = currentTest.sections.find(s => s.section_number === sectionNum);
    if (!section) return;
    
    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.src = section.audio_url || '';
    
    // Update section info
    document.getElementById('currentSection').textContent = sectionNum;
    document.getElementById('sectionTitle').textContent = section.title;
    
    // Update section tabs
    document.querySelectorAll('.section-tab').forEach(tab => {
        tab.classList.remove('active');
        if (parseInt(tab.dataset.section) === sectionNum) {
            tab.classList.add('active');
        }
    });
    
    // Auto-play audio when section loads (if allowed by browser)
    audioPlayer.play().catch(e => {
        console.log('Auto-play prevented. User must click play.');
    });
}

// ============================================================================
// QUESTION DISPLAY & NAVIGATION
// ============================================================================

function displayQuestion(index) {
    if (index < 0 || index >= 40) return;
    
    currentQuestionIndex = index;
    const questionNum = index + 1;
    const question = currentTest.questions[index];
    
    // Update question number
    document.getElementById('questionNumber').textContent = questionNum;
    
    // Update question type
    document.getElementById('questionType').textContent = 
        formatQuestionType(question.question_type);
    
    // Calculate and update section
    const newSection = Math.ceil(questionNum / 10);
    if (newSection !== currentSection) {
        currentSection = newSection;
        loadSectionAudio(currentSection);
    }
    
    // Display question content
    displayQuestionContent(question);
    
    // Update navigation buttons
    updateNavigationButtons();
    
    // Update question grid
    updateQuestionGrid();
}

function displayQuestionContent(question) {
    const container = document.getElementById('questionContent');
    let html = '';
    
    // Add instructions if present
    if (question.instructions) {
        html += `<div class="alert alert-info">${question.instructions}</div>`;
    }
    
    // Add question text
    html += `<div class="question-text">${question.question_text || ''}</div>`;
    
    // Add visual aid if needed (for map questions)
    if (question.requires_visual || (currentSection === 2 && questionNum >= 15 && questionNum <= 20)) {
        const section = currentTest.sections.find(s => s.section_number === 2);
        if (section && section.visual_aid_url) {
            html += `
                <div class="map-container">
                    <h5 style="margin-bottom: 15px;">Use the map below to answer questions 15-20:</h5>
                    <img src="${section.visual_aid_url}" 
                         alt="Bellingham Castle Map" 
                         style="max-width: 100%; height: auto; border: 2px solid #dee2e6; border-radius: 8px;">
                </div>
            `;
        }
    }
    
    // Add answer input based on question type
    const questionNum = currentQuestionIndex + 1;
    const existingAnswer = userAnswers[questionNum] || '';
    
    switch(question.question_type) {
        case 'multiple_choice':
            html += generateMultipleChoice(question, existingAnswer);
            break;
        case 'map_labeling':
            html += generateMapLabeling(question, existingAnswer);
            break;
        case 'matching':
            html += generateMatching(question, existingAnswer);
            break;
        default:
            // Form completion, sentence completion, note completion
            html += generateTextInput(question, existingAnswer);
    }
    
    container.innerHTML = html;
}

function generateMultipleChoice(question, existingAnswer) {
    let html = '<div class="multiple-choice-options">';
    
    const options = question.options || ['A', 'B', 'C'];
    options.forEach(option => {
        const isSelected = existingAnswer === option;
        html += `
            <div class="choice-option ${isSelected ? 'selected' : ''}" 
                 onclick="selectChoice('${option}')" data-option="${option}">
                <strong>${option}.</strong> 
                <span>${getOptionText(question, option)}</span>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

function generateMapLabeling(question, existingAnswer) {
    let html = '<div class="multiple-choice-options">';
    
    const options = question.options || ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    html += '<p>Select the letter (A-H) that corresponds to this location on the map:</p>';
    
    options.forEach(option => {
        const isSelected = existingAnswer === option;
        html += `
            <button class="btn ${isSelected ? 'btn-primary' : 'btn-outline-primary'} m-1" 
                    onclick="selectChoice('${option}')" data-option="${option}">
                ${option}
            </button>
        `;
    });
    
    html += '</div>';
    return html;
}

function generateMatching(question, existingAnswer) {
    let html = '<div class="matching-options">';
    
    if (question.option_descriptions) {
        html += '<div class="mb-3">';
        for (const [key, desc] of Object.entries(question.option_descriptions)) {
            html += `<div><strong>${key}:</strong> ${desc}</div>`;
        }
        html += '</div>';
    }
    
    html += '<div class="multiple-choice-options">';
    const options = question.options || ['A', 'B', 'C'];
    options.forEach(option => {
        const isSelected = existingAnswer === option;
        html += `
            <button class="btn ${isSelected ? 'btn-primary' : 'btn-outline-secondary'} m-1" 
                    onclick="selectChoice('${option}')" data-option="${option}">
                ${option}
            </button>
        `;
    });
    
    html += '</div></div>';
    return html;
}

function generateTextInput(question, existingAnswer) {
    const maxWords = question.max_words || '';
    const placeholder = maxWords ? `Maximum ${maxWords} word(s)` : 'Enter your answer';
    
    return `
        <input type="text" 
               class="form-control answer-input ${existingAnswer ? 'answered' : ''}" 
               id="answerInput"
               value="${existingAnswer}"
               placeholder="${placeholder}"
               onchange="saveAnswer(this.value)"
               maxlength="${maxWords ? maxWords * 15 : 100}">
    `;
}

function getOptionText(question, option) {
    // This would normally come from the question data
    // For now, return placeholder text
    return `Option ${option}`;
}

function formatQuestionType(type) {
    const types = {
        'multiple_choice': 'Multiple Choice',
        'form_completion': 'Form Completion',
        'sentence_completion': 'Sentence Completion',
        'note_completion': 'Note Completion',
        'map_labeling': 'Map Labeling',
        'matching': 'Matching'
    };
    return types[type] || 'Question';
}

// ============================================================================
// ANSWER MANAGEMENT
// ============================================================================

function selectChoice(option) {
    const questionNum = currentQuestionIndex + 1;
    userAnswers[questionNum] = option;
    
    // Update UI
    document.querySelectorAll('.choice-option, .btn').forEach(el => {
        if (el.dataset && el.dataset.option) {
            if (el.dataset.option === option) {
                el.classList.add('selected', 'btn-primary');
                el.classList.remove('btn-outline-primary', 'btn-outline-secondary');
            } else {
                el.classList.remove('selected', 'btn-primary');
                if (el.classList.contains('btn')) {
                    el.classList.add('btn-outline-primary');
                }
            }
        }
    });
    
    updateQuestionGrid();
    saveProgress();
}

function saveAnswer(value) {
    const questionNum = currentQuestionIndex + 1;
    if (value.trim()) {
        userAnswers[questionNum] = value.trim();
    } else {
        delete userAnswers[questionNum];
    }
    
    updateQuestionGrid();
    saveProgress();
}

// ============================================================================
// NAVIGATION
// ============================================================================

function previousQuestion() {
    if (currentQuestionIndex > 0) {
        displayQuestion(currentQuestionIndex - 1);
    }
}

function nextQuestion() {
    if (currentQuestionIndex < 39) {
        displayQuestion(currentQuestionIndex + 1);
    }
}

function jumpToQuestion(questionNum) {
    displayQuestion(questionNum - 1);
}

function flagQuestion() {
    const questionNum = currentQuestionIndex + 1;
    
    if (flaggedQuestions.has(questionNum)) {
        flaggedQuestions.delete(questionNum);
        document.getElementById('flagBtn').textContent = '🚩 Flag for Review';
    } else {
        flaggedQuestions.add(questionNum);
        document.getElementById('flagBtn').textContent = '✓ Flagged';
    }
    
    updateQuestionGrid();
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    // Previous button
    prevBtn.disabled = currentQuestionIndex === 0;
    
    // Next/Submit button
    if (currentQuestionIndex === 39) {
        nextBtn.classList.add('d-none');
        submitBtn.classList.remove('d-none');
    } else {
        nextBtn.classList.remove('d-none');
        submitBtn.classList.add('d-none');
    }
    
    // Flag button
    const questionNum = currentQuestionIndex + 1;
    if (flaggedQuestions.has(questionNum)) {
        document.getElementById('flagBtn').textContent = '✓ Flagged';
    } else {
        document.getElementById('flagBtn').textContent = '🚩 Flag for Review';
    }
}

// ============================================================================
// QUESTION GRID
// ============================================================================

function initializeQuestionGrid() {
    const grid = document.getElementById('questionGrid');
    let html = '';
    
    for (let i = 1; i <= 40; i++) {
        html += `
            <div class="question-indicator" 
                 id="indicator-${i}"
                 onclick="jumpToQuestion(${i})">
                ${i}
            </div>
        `;
    }
    
    grid.innerHTML = html;
}

function updateQuestionGrid() {
    for (let i = 1; i <= 40; i++) {
        const indicator = document.getElementById(`indicator-${i}`);
        if (!indicator) continue;
        
        // Reset classes
        indicator.className = 'question-indicator';
        
        // Current question
        if (i === currentQuestionIndex + 1) {
            indicator.classList.add('current');
        }
        
        // Answered question
        if (userAnswers[i]) {
            indicator.classList.add('answered');
        }
        
        // Flagged question
        if (flaggedQuestions.has(i)) {
            indicator.classList.add('flagged');
        }
    }
}

// ============================================================================
// PROGRESS SAVING
// ============================================================================

async function saveProgress() {
    try {
        const response = await fetch('/api/listening/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                test_id: currentTest.test_id,
                current_question: currentQuestionIndex + 1,
                answers: userAnswers,
                time_remaining: timeRemaining
            })
        });
        
        if (!response.ok) {
            console.error('Failed to save progress');
        }
    } catch (error) {
        console.error('Error saving progress:', error);
    }
}

// ============================================================================
// TEST SUBMISSION
// ============================================================================

async function submitTest() {
    // Confirm submission
    const unanswered = 40 - Object.keys(userAnswers).length;
    if (unanswered > 0) {
        const confirmed = confirm(`You have ${unanswered} unanswered questions. Submit anyway?`);
        if (!confirmed) return;
    }
    
    // Stop timer
    if (testTimer) {
        clearInterval(testTimer);
    }
    
    try {
        // Submit answers
        const response = await fetch('/api/listening/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                test_id: currentTest.test_id,
                answers: userAnswers
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result);
        } else {
            showError('Failed to submit test');
        }
    } catch (error) {
        console.error('Error submitting test:', error);
        showError('Failed to submit test. Please try again.');
    }
}

function autoSubmitTest() {
    showNotification('Time is up! Submitting your test...', 'info');
    submitTest();
}

function displayResults(result) {
    // Update modal with results
    document.getElementById('bandScore').textContent = result.band_score.toFixed(1);
    document.getElementById('correctScore').textContent = result.score.correct;
    document.getElementById('incorrectScore').textContent = result.score.incorrect;
    document.getElementById('percentageScore').textContent = result.score.percentage + '%';
    
    // Display section performance
    let sectionHTML = '<div class="row">';
    result.section_performance.forEach(section => {
        sectionHTML += `
            <div class="col-md-3">
                <div class="score-item">
                    <div class="score-label">Section ${section.section}</div>
                    <div class="score-value">${section.score}/${section.total}</div>
                </div>
            </div>
        `;
    });
    sectionHTML += '</div>';
    document.getElementById('sectionPerformance').innerHTML = sectionHTML;
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
    modal.show();
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showNotification(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function showError(message) {
    showNotification(message, 'danger');
}

function proceedToNext() {
    // Navigate to reading test or full test results
    window.location.href = '/reading-test';
}