const { spawn } = require('child_process');

function fetchNewsArticle(url) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', ['./pythonFiles/fetchArticle.py', url]);

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

        const pythonProcess = spawn('python', ['./pythonFiles/textProcessor.py']);

        pythonProcess.stdin.write(text);
        pythonProcess.stdin.end();

        pythonProcess.stdout.on('data', (data) => {
            const result = JSON.parse(data.toString());
            resolve({ result, tabUrl });
        });

        pythonProcess.stderr.on('data', (data) => {
            reject(data.toString());
        });
    });
}

module.exports = {fetchNewsArticle, processText};