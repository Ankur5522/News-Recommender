// Listen for enable/disable tracking messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'enableTracking') {
        setupWebNavigationListener();
        console.log('Tracking enabled');
    } else if (message.action === 'disableTracking') {
        removeWebNavigationListener();
        console.log('Tracking disabled');
    } else if (message.action === 'sendTrackingData') {
        console.log('Received tracking data:', message.data);
        console.log('Sending data to server...');
        const { timeSpent, url } = message.data;

        fetch('http://localhost:5000/process-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url,
                timeSpent,
                timestamp: Date.now()
            })
        })
        .then(response => console.log('Data sent successfully!', response))
        .catch(error => console.error('Error sending data:', error));
    }
});
