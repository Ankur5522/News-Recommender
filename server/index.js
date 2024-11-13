const express = require("express");
const mongoose = require("mongoose");
const { fetchNewsArticle, processText } = require("./helpers/helpers");

const app = express();
const port = 5000;

app.use(express.json());

// Connect to MongoDB
mongoose
    .connect(
        "mongodb+srv://ac7351318355:ankur5522@cluster0.ua8ii.mongodb.net/SmartFeed?"
    )
    .then(() => {
        console.log("Connected to MongoDB");
    })
    .catch((error) => {
        console.error("Error connecting to MongoDB:", error);
    });

// Define routes
app.get("/", (req, res) => {
    res.send("Hello, World!");
});

// app.post('/process-text', (req, res) => {

//     const rawText = req.body.pageContent;
//     if (!rawText) {
//         return res.status(400).send('No text provided');
//     }

//     // Spawn a new Python process
//     const python = spawn('python', ['./pythonFiles/textProcessor.py', rawText]);

//     let pythonOutput = '';

//     // Capture Python output
//     python.stdout.on('data', (data) => {
//         pythonOutput += data.toString();
//     });

//     // Handle Python script errors
//     python.stderr.on('data', (data) => {
//         console.error(`Python error: ${data}`);
//         if (!res.headersSent) { // Only send a response if headers are not already sent
//             res.status(500).send('Python script error');
//         }
//     });

//     // On Python script completion
//     python.on('close', (code) => {
//         if (code !== 0) {
//             if (!res.headersSent) {
//                 return res.status(500).send('Error processing text');
//             }
//         }

//         // Parse the JSON response from Python
//         try {
//             const processedData = JSON.parse(pythonOutput);
//             if (!res.headersSent) { // Only send a response if headers are not already sent
//                 console.log(processedData);
//                 res.json({ processedText: processedData.processed_text });
//             }
//         } catch (error) {
//             if (!res.headersSent) { // Only send a response if headers are not already sent
//                 res.status(500).send('Error parsing Python output');
//             }
//         }
//     });
// });

// Start the server

app.post("/process-text", (req, res) => {
    const { url, timeSpent } = req.body;

    console.log("Received data:", req.body);

    fetchNewsArticle(url)
        .then((articleData) => {
            console.log("Fetched article:", articleData);
            const pageContent = articleData.title + ". " + articleData.text;
            if(articleData.text.length < 100) {
                console.log("Article too short, skipping processing");
                return res.status(400).json({ error: "Article too short" });
            }
            processText(pageContent, url)
                .then(({ result, tabUrl }) => {
                    // Combine result with timeSpent and tabUrl
                    const dataToSend = {
                        keywords: result.keywords,
                        entities: result.entities,
                        topics: result.topics,
                        url: url,
                        timeSpent,
                    };

                    console.log("Data processed:", dataToSend);
                })
                .catch((err) => {
                    console.error("Error in processing text:", err);
                    res.status(500).json({ error: "Text processing failed" });
                });
        })
        .catch((err) => {
            console.error("Error fetching article:", err);
            return res.status(500).json({ error: "Failed to fetch article" });
        });
});
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
