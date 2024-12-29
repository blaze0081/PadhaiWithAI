import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';

const AnalysisDashboard = () => {
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedStudent, setSelectedStudent] = useState('');
  const [students, setStudents] = useState([]);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAnalysisData = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/analysis-data/?class_name=${selectedClass}&student_id=${selectedStudent}`,
        {
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        }
      );
      const data = await response.json();
      setAnalysisData(data);
      setStudents(data.students);
    } catch (error) {
      console.error('Error fetching analysis data:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (selectedClass) {
      fetchAnalysisData();
    }
  }, [selectedClass]);

  useEffect(() => {
    if (selectedStudent) {
      fetchAnalysisData();
    }
  }, [selectedStudent]);

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-6">Student Progress Analysis</h1>
        
        <div className="flex gap-4 mb-6">
          <select 
            className="p-2 border rounded"
            value={selectedClass}
            onChange={(e) => {
              setSelectedClass(e.target.value);
              setSelectedStudent('');
            }}
          >
            <option value="">Select Class</option>
            {/* Class choices will be populated from Django context */}
          </select>
          
          {selectedClass && (
            <select
              className="p-2 border rounded"
              value={selectedStudent}
              onChange={(e) => setSelectedStudent(e.target.value)}
            >
              <option value="">All Students</option>
              {students.map(student => (
                <option key={student.id} value={student.id}>
                  {student.roll_number} - {student.name}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center">Loading...</div>
      ) : analysisData ? (
        <div className="space-y-8">
          {/* Individual Student Progress */}
          {selectedStudent && analysisData.student_progress.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Student Progress Over Time</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analysisData.student_progress}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="test_number" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="marks" 
                    stroke="#8884d8" 
                    name="Marks"
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Class Performance */}
          {selectedClass && analysisData.class_performance.length > 0 && (
            <div className="bg-white p-4 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Class Performance Overview</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analysisData.class_performance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="test_number" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="average" fill="#8884d8" name="Class Average" />
                  <Bar dataKey="max_mark" fill="#82ca9d" name="Highest Mark" />
                  <Bar dataKey="min_mark" fill="#ff8042" name="Lowest Mark" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center text-gray-500">
          Select a class to view analysis
        </div>
      )}
    </div>
  );
};

export default AnalysisDashboard;