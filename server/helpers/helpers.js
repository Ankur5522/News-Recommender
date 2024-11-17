const { spawn } = require('child_process');

function fetchNewsArticle(url) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', ['pythonFiles/fetchArticle.py', url]);

        pythonProcess.stdout.on('data', (data) => {
            const result = JSON.parse(data.toString());
            resolve(result);
        });

        pythonProcess.stderr.on('data', (data) => {
            reject(data.toString());
        });
    });
}

function processText(text, tabUrl) {
    return new Promise((resolve, reject) => {
        // Use 'prime-run python' to run the Python script on the NVIDIA GPU
        const pythonProcess = spawn('python', ['pythonFiles/textProcessor.py']);

        // Send input text to Python process
        pythonProcess.stdin.write(text);
        pythonProcess.stdin.end();

        let outputData = '';

        // Collect output data
        pythonProcess.stdout.on('data', (data) => {
            console.log(`Received data: ${data}`);
            outputData += data.toString();
        });

        // Handle any errors from stderr
        pythonProcess.stderr.on('data', (data) => {
            console.error(`Error: ${data}`);
            reject(data.toString());
        });

        // Resolve promise when process completes
        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(outputData);
                    resolve({ result, tabUrl });
                } catch (err) {
                    reject(`Error parsing JSON: ${err}`);
                }
            } else {
                reject(`Process exited with code: ${code}`);
            }
        });
    });
}

const normalizeTimeSpent = (timeSpent, maxTime = 100) => {
    return Math.min(timeSpent / maxTime, 1); // Ensures it is within 0-1
};

const createGraph = (articleData) => {

    jsonData = JSON.stringify(articleData);

    const pythonProcess = spawn('python', ['pythonFiles/create_graph.py']);

    pythonProcess.stdin.write(jsonData);
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python output: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python script exited with code ${code}`);
        }
    });
};


const fetchCategory = (text) => {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', ['../pythonFiles/categoryPred.py'], {
            cwd: __dirname, // Set working directory
        });

        pythonProcess.stdin.write(text);
        pythonProcess.stdin.end();

        let outputData = '';

        pythonProcess.stdout.on('data', (data) => {
            console.log("Python STDOUT:", data.toString());
            outputData += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error("Python STDERR:", data.toString());
            reject(data.toString());
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    const result = JSON.parse(outputData);
                    resolve(result.category);
                } catch (err) {
                    reject(`Error parsing Python output: ${err.message}`);
                }
            } else {
                reject(`Python process exited with code: ${code}`);
            }
        });
    });
};





module.exports = {fetchNewsArticle, processText, createGraph, fetchCategory};