import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardContent } from './components/ui/card';

const Dashboard = () => {
  // Data for various charts
  const symptomsData = [
    { name: "Excessive worrying or fear", value: 63 },
    { name: "Avoiding social situations", value: 59 },
    { name: "Fatigue or sleep problems", value: 61 },
    { name: "Feelings of sadness or isolation", value: 59 },
    { name: "Problems concentrating", value: 46 },
    { name: "Sudden mood changes", value: 49 },
  ];

  const supportMethodsData = [
    { name: "Speaking to friends", value: 66 },
    { name: "Distractions (TV, reading)", value: 63 },
    { name: "Sleeping", value: 51 },
    { name: "Physical Activity", value: 49 },
    { name: "Speaking to parents", value: 31 },
    { name: "Meditation", value: 25 },
  ];

  const platformPreferencesData = [
    { name: "In-person", value: 75 },
    { name: "Mobile app", value: 34 },
    { name: "Chat services", value: 15 },
    { name: "Website", value: 13 },
  ];

  const trustFactorsData = [
    { name: "Data Privacy", value: 66 },
    { name: "Anonymity Options", value: 56 },
    { name: "Data Deletion Policies", value: 51 },
  ];

  const ageGroupData = [
    { name: "18-21", value: 17 },
    { name: "21-25", value: 35 },
    { name: "26-30", value: 22 },
    { name: "30-35", value: 12 },
    { name: "35+", value: 13 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

  return (
    <div className="p-4 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-center">Sukoon Survey Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Common Symptoms</h2>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={symptomsData} layout="vertical" margin={{ left: 200 }}>
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={180} />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8">
                  {symptomsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Preferred Support Methods</h2>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={supportMethodsData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {supportMethodsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Platform Preferences</h2>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={platformPreferencesData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#82ca9d">
                  {platformPreferencesData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Trust Factors for AI-based Tools</h2>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={trustFactorsData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {trustFactorsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Age Distribution</h2>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={ageGroupData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {ageGroupData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Key Insights</h2>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5">
              <li>65% of respondents experience excessive worrying or fear</li>
              <li>Speaking to friends (66%) is the most common coping method</li>
              <li>Data privacy (66%) is the top concern for AI-based mental health tools</li>
              <li>The 21-25 age group (36%) forms the largest user base</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;


// import React from 'react';
// import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
// import { Card, CardHeader, CardContent } from './components/ui/card';

// const Dashboard = () => {
//   // Data for various charts
//   const symptomsData = [
//     { name: "Excessive worrying or fear", value: 65 },
//     { name: "Avoiding social situations", value: 59 },
//     { name: "Fatigue or sleep problems", value: 60 },
//     { name: "Feelings of sadness or isolation", value: 60 },
//     { name: "Problems concentrating", value: 46 },
//     { name: "Sudden mood changes", value: 49 },
//   ];

//   const supportMethodsData = [
//     { name: "Speaking to friends", value: 66 },
//     { name: "Distractions (TV, reading)", value: 64 },
//     { name: "Sleeping", value: 50 },
//     { name: "Physical Activity", value: 49 },
//     { name: "Speaking to parents", value: 31 },
//     { name: "Meditation", value: 25 },
//   ];

//   const platformPreferencesData = [
//     { name: "In-person", value: 75 },
//     { name: "Mobile app", value: 33 },
//     { name: "Chat services", value: 15 },
//     { name: "Website", value: 13 },
//   ];

//   const trustFactorsData = [
//     { name: "Data Privacy", value: 66 },
//     { name: "Anonymity Options", value: 56 },
//     { name: "Data Deletion Policies", value: 51 },
//   ];

//   const ageGroupData = [
//     { name: "18-21", value: 17 },
//     { name: "21-25", value: 36 },
//     { name: "26-30", value: 21 },
//     { name: "30-35", value: 12 },
//     { name: "35+", value: 13 },
//   ];

//   const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

//   return (
//     <div className="p-4 bg-gray-100 min-h-screen">
//       <h1 className="text-3xl font-bold mb-6 text-center">Mental Health App Survey Dashboard</h1>

//       <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//         <Card>
//           <CardHeader>
//             <h2 className="text-xl font-semibold">Common Symptoms</h2>
//           </CardHeader>
//           <CardContent>
//             <ResponsiveContainer width="100%" height={300}>
//               <BarChart data={symptomsData}>
//                 <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
//                 <YAxis />
//                 <Tooltip />
//                 <Bar dataKey="value" fill="#8884d8">
//                   {symptomsData.map((entry, index) => (
//                     <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
//                   ))}
//                 </Bar>
//               </BarChart>
//             </ResponsiveContainer>
//           </CardContent>
//         </Card>

//         <Card>
//           <CardHeader>
//             <h2 className="text-xl font-semibold">Preferred Support Methods</h2>
//           </CardHeader>
//           <CardContent>
//             <ResponsiveContainer width="100%" height={300}>
//               <PieChart>
//                 <Pie
//                   data={supportMethodsData}
//                   cx="50%"
//                   cy="50%"
//                   labelLine={false}
//                   outerRadius={80}
//                   fill="#8884d8"
//                   dataKey="value"
//                   label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
//                 >
//                   {supportMethodsData.map((entry, index) => (
//                     <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
//                   ))}
//                 </Pie>
//                 <Tooltip />
//               </PieChart>
//             </ResponsiveContainer>
//           </CardContent>
//         </Card>

//         <Card>
//           <CardHeader>
//             <h2 className="text-xl font-semibold">Platform Preferences</h2>
//           </CardHeader>
//           <CardContent>
//             <ResponsiveContainer width="100%" height={300}>
//               <BarChart data={platformPreferencesData}>
//                 <XAxis dataKey="name" />
//                 <YAxis />
//                 <Tooltip />
//                 <Bar dataKey="value" fill="#82ca9d">
//                   {platformPreferencesData.map((entry, index) => (
//                     <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
//                   ))}
//                 </Bar>
//               </BarChart>
//             </ResponsiveContainer>
//           </CardContent>
//         </Card>

//         <Card>
//           <CardHeader>
//             <h2 className="text-xl font-semibold">Trust Factors for AI-based Tools</h2>
//           </CardHeader>
//           <CardContent>
//             <ResponsiveContainer width="100%" height={300}>
//               <PieChart>
//                 <Pie
//                   data={trustFactorsData}
//                   cx="50%"
//                   cy="50%"
//                   labelLine={false}
//                   outerRadius={80}
//                   fill="#8884d8"
//                   dataKey="value"
//                   label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
//                 >
//                   {trustFactorsData.map((entry, index) => (
//                     <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
//                   ))}
//                 </Pie>
//                 <Tooltip />
//               </PieChart>
//             </ResponsiveContainer>
//           </CardContent>
//         </Card>

//         <Card>
//           <CardHeader>
//             <h2 className="text-xl font-semibold">Age Distribution</h2>
//           </CardHeader>
//           <CardContent>
//             <ResponsiveContainer width="100%" height={300}>
//               <PieChart>
//                 <Pie
//                   data={ageGroupData}
//                   cx="50%"
//                   cy="50%"
//                   labelLine={false}
//                   outerRadius={80}
//                   fill="#8884d8"
//                   dataKey="value"
//                   label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
//                 >
//                   {ageGroupData.map((entry, index) => (
//                     <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
//                   ))}
//                 </Pie>
//                 <Tooltip />
//               </PieChart>
//             </ResponsiveContainer>
//           </CardContent>
//         </Card>

//         <Card>
//           <CardHeader>
//             <h2 className="text-xl font-semibold">Key Insights</h2>
//           </CardHeader>
//           <CardContent>
//             <ul className="list-disc pl-5">
//               <li>65% of respondents experience excessive worrying or fear</li>
//               <li>75% prefer in-person support over digital platforms</li>
//               <li>Speaking to friends (66%) is the most common coping method</li>
//               <li>Data privacy (66%) is the top concern for AI-based mental health tools</li>
//               <li>The 21-25 age group (36%) forms the largest user base</li>
//             </ul>
//           </CardContent>
//         </Card>
//       </div>
//     </div>
//   );
// };

// export default Dashboard;