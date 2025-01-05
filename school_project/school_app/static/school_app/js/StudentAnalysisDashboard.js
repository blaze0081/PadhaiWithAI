// static/school_app/js/StudentAnalysisDashboard.js

document.addEventListener('DOMContentLoaded', function() {
  const studentSelect = document.getElementById('studentSelect');
  const analysisContent = document.getElementById('analysisContent');

  // Fetch students when page loads
  fetchStudents();

  // Add change event listener to the select element
  studentSelect.addEventListener('change', function(e) {
      const selectedId = e.target.value;
      if (selectedId) {
          fetchStudentData(selectedId);
      } else {
          // Clear the analysis content if no student is selected
          analysisContent.innerHTML = '';
      }
  });

  async function fetchStudents() {
      try {
          const response = await fetch('/api/students/', {
              headers: {
                  'X-Requested-With': 'XMLHttpRequest'
              }
          });

          if (!response.ok) throw new Error('Failed to fetch students');

          const data = await response.json();
          if (data.students && Array.isArray(data.students)) {
              populateStudentSelect(data.students);
          }
      } catch (error) {
          console.error('Error:', error);
          showError('Failed to load students. Please refresh the page.');
      }
  }

  function populateStudentSelect(students) {
      studentSelect.innerHTML = '<option value="">Choose a student...</option>';
      students.sort((a, b) => a.name.localeCompare(b.name))
          .forEach(student => {
              const option = document.createElement('option');
              option.value = student.id;
              option.textContent = `${student.name} (Roll No: ${student.roll_number})`;
              studentSelect.appendChild(option);
          });
  }

  async function fetchStudentData(studentId) {
      try {
          const response = await fetch(`/api/student-analysis/${studentId}/`, {
              headers: {
                  'X-Requested-With': 'XMLHttpRequest'
              }
          });

          if (!response.ok) throw new Error('Failed to fetch student data');

          const data = await response.json();
          displayStudentAnalysis(data);
      } catch (error) {
          console.error('Error:', error);
          showError('Failed to load student analysis. Please try again.');
      }
  }

  function displayStudentAnalysis(data) {
      // Create the HTML content for student analysis
      const html = `
          <div class="card mb-4">
              <div class="card-header">
                  <h3 class="card-title mb-0">Student Information</h3>
              </div>
              <div class="card-body">
                  <div class="row">
                      <div class="col-md-4">
                          <p><strong>Name:</strong> ${data.name}</p>
                      </div>
                      <div class="col-md-4">
                          <p><strong>Roll Number:</strong> ${data.roll_number}</p>
                      </div>
                      <div class="col-md-4">
                          <p><strong>Class:</strong> ${data.class_name}</p>
                      </div>
                  </div>
              </div>
          </div>

          <div class="card mb-4">
              <div class="card-header">
                  <h3 class="card-title mb-0">Performance Statistics</h3>
              </div>
              <div class="card-body">
                  <div class="row">
                      <div class="col-md-3">
                          <p><strong>Average Marks:</strong> ${data.statistics.average_marks}</p>
                      </div>
                      <div class="col-md-3">
                          <p><strong>Highest Mark:</strong> ${data.statistics.highest_mark}</p>
                      </div>
                      <div class="col-md-3">
                          <p><strong>Lowest Mark:</strong> ${data.statistics.lowest_mark}</p>
                      </div>
                      <div class="col-md-3">
                          <p><strong>Total Tests:</strong> ${data.statistics.total_tests}</p>
                      </div>
                  </div>
              </div>
          </div>

          <div class="card">
              <div class="card-header">
                  <h3 class="card-title mb-0">Test Performance Details</h3>
              </div>
              <div class="card-body">
                  <div class="table-responsive">
                      <table class="table table-striped">
                          <thead>
                              <tr>
                                  <th>Test Name</th>
                                  <th>Subject</th>
                                  <th>Date</th>
                                  <th>Marks</th>
                                  <th>Class Average</th>
                              </tr>
                          </thead>
                          <tbody>
                              ${data.test_performance.map(test => `
                                  <tr>
                                      <td>${test.test_name}</td>
                                      <td>${test.subject}</td>
                                      <td>${test.date || 'N/A'}</td>
                                      <td>${test.marks}</td>
                                      <td>${test.class_average || 'N/A'}</td>
                                  </tr>
                              `).join('')}
                          </tbody>
                      </table>
                  </div>
              </div>
          </div>
      `;

      // Update the analysis content
      analysisContent.innerHTML = html;
  }

  function showError(message) {
      analysisContent.innerHTML = `
          <div class="alert alert-danger" role="alert">
              ${message}
          </div>
      `;
  }
});