import React from 'react';

export const Card = ({ children }) => (
  <div className="bg-white shadow-md rounded-lg overflow-hidden">{children}</div>
);

export const CardHeader = ({ children }) => (
  <div className="px-4 py-5 border-b border-gray-200 sm:px-6">{children}</div>
);

export const CardContent = ({ children }) => (
  <div className="px-4 py-5 sm:p-6">{children}</div>
);