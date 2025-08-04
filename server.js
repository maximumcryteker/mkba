const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware to parse JSON POST data
app.use(express.json());

// Serve static files (e.g., stroop.html)
app.use(express.static('.'));

// Handle POST request to save results
app.post('/save-results', (req, res) => {
  const data = req.body;

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = path.join(__dirname, 'data', `results_${timestamp}.json`);

  fs.writeFile(filename, JSON.stringify(data, null, 2), err => {
    if (err) {
      console.error('Error saving file:', err);
      return res.status(500).send('Error saving file');
    }
    console.log('Saved:', filename);
    res.send('Saved successfully');
  });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
