const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const { fetchNewsArticle, processText, fetchCategory, createGraph } = require("./helpers/helpers");
const News = require("./schema/schema");
const createGraphFromData = require("./helpers/createGraph");


const app = express();
const port = 5000;

app.use(express.json());
app.use(cors());

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

app.post("/process-text", async (req, res) => {
    const { url, timeSpent } = req.body;

    try {

        // Step 1: Fetch the news article
        const articleData = await fetchNewsArticle(url);

        // Combine the title and text for processing
        const pageContent = articleData.title + ". " + articleData.text;

        // Check if the article is too short
        if (articleData.text.length < 500) {
            console.log("Article too short, skipping processing");
            return res.status(400).json({ error: "Article too short" });
        }

        // Step 2: Run `fetchCategory` and `processText` in parallel
        // const [category, { result, tabUrl }] = await Promise.all([
        //     fetchCategory(pageContent), // Fetch category
        //     processText(pageContent, url), // Process text
        // ]);

        const category = await fetchCategory(pageContent);

        const { result, tabUrl} = await processText(pageContent, url);

        // Combine result with additional data
        const dataToSend = {
            tags: result.tags,
            url: url,
            category: category,
            timeSpent,
        };

        // Step 3: Save data to MongoDB
        const news = new News(dataToSend);
        await news.save();
        console.log("Data saved to MongoDB:", dataToSend);

        // (Optional) Step 4: Create the graph
        // await createGraph(result.tags, url, timeSpent);

        // Send success response
        res.status(200).json({ message: "Text processed and graph updated" });
    } catch (err) {
        console.error("Error processing text:", err);
        res.status(500).json({ error: "An error occurred while processing the text" });
    }
});


app.get('/create-graph', async (req, res) => {
    try {
        const articleData = await News.find();

        await createGraph(articleData);

        res.status(200).json({ message: 'Graph creation completed successfully' });
    } catch (error) {
        console.error('Error creating the graph:', error);
        res.status(500).json({ error: 'Failed to create graph' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
