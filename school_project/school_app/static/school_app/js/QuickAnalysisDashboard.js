// school_app/static/school_app/js/components/QuickAnalysisDashboard.js

import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const QuickAnalysisDashboard = () => {
  const [selectedClass, setSelectedClass] = useState('');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAnalysisData = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/analysis-data/?class_name=${selectedClass}`,
        {
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        }
      );
      const data = await response.json();
      setAnalysisData(data);
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

  return (
    <div className="p-4">
      <div className="mb-4">
        <select 
          className="form-select"
          value={selectedClass}
          onChange={(e) => setSelectedClass(e.target.value)}
        >
          <option value="">Select Class</option>
          {/* Class choices will be populated from Django context */}
        </select>
      </div>

      {loading ? (
        <div className="text-center">Loading...</div>
      ) : analysisData?.class_performance?.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={analysisData.class_performance}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="test_number" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="average" 
              stroke="#8884d8" 
              name="Class Average"
            />
            <Line 
              type="monotone" 
              dataKey="max_mark" 
              stroke="#82ca9d" 
              name="Highest Mark"
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="text-center text-gray-500">
          Select a class to view performance overview
        </div>
      )}
    </div>
  );
};

export default QuickAnalysisDashboard;