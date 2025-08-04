// const express = require('express');
// const fs = require('fs');
// const path = require('path');

// const app = express();
// const PORT = 3000;

// // Middleware to parse JSON POST data
// app.use(express.json());

// // Serve static files (e.g., stroop.html)
// app.use(express.static('.'));

// // Handle POST request to save results
// app.post('/save-results', (req, res) => {
//   const data = req.body;

//   const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
//   const filename = path.join(__dirname, 'data', `results_${timestamp}.json`);

//   fs.writeFile(filename, JSON.stringify(data, null, 2), err => {
//     if (err) {
//       console.error('Error saving file:', err);
//       return res.status(500).send('Error saving file');
//     }
//     console.log('Saved:', filename);
//     res.send('Saved successfully');
//   });
// });

// app.listen(PORT, () => {
//   console.log(`Server running at http://localhost:${PORT}`);
// });

const express = require('express');
const fs = require('fs');
const path = require('path');
const { Parser } = require('json2csv');

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static('.'));

// POST handler
app.post('/save-results', (req, res) => {
  const data = req.body;
  const dir = path.join(__dirname, 'data');

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonFilename = path.join(dir, `results_${timestamp}.json`);
  const csvFilename = path.join(dir, `results_${timestamp}.csv`);

  // Save JSON
  fs.writeFileSync(jsonFilename, JSON.stringify(data, null, 2));

  // Prepare CSV from taskResults array
  try {
    // Flatten questionnaire answers as key-value pairs in CSV
    // Combine questionnaire and taskResults for CSV:
    // Let's save taskResults in CSV and add timestamp & maybe participant info
    const fields = ['timestamp', 'shape', 'color', 'key', 'time', 'correct'];
    const rows = data.taskResults.map(tr => ({
      timestamp: data.timestamp,
      shape: tr.shape,
      color: tr.color,
      key: tr.key,
      time: tr.time,
      correct: tr.correct
    }));

    const json2csvParser = new Parser({ fields });
    const csv = json2csvParser.parse(rows);

    fs.writeFileSync(csvFilename, csv);
  } catch (err) {
    console.error('Error creating CSV:', err);
    return res.status(500).send('Error creating CSV');
  }

  console.log('Saved JSON and CSV:', jsonFilename, csvFilename);
  res.send('Saved successfully');
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
