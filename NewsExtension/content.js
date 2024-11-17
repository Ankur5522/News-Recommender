let startTime = null;
let totalTimeSpent = 0;
let isTabActive = true;
let dataSent = false; // Flag to prevent multiple requests

function trackTime() {
    console.log('Tracking time...');

    if (!startTime) {
        startTime = new Date().getTime();
    }

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            pauseTime();
        } else {
            resumeTime();
        }
    });

    window.addEventListener('beforeunload', () => handlePageExit());
    window.addEventListener('pagehide', () => handlePageExit());
}

function pauseTime() {
    if (!isTabActive) return;
    const endTime = new Date().getTime();
    totalTimeSpent += endTime - startTime;
    isTabActive = false;
    console.log(`Tab inactive. Time paused at: ${totalTimeSpent / 1000} seconds`);
}

function resumeTime() {
    if (isTabActive) return;
    startTime = new Date().getTime();
    isTabActive = true;
    console.log('Tab active again. Resuming time tracking...');
}

function sendTrackingData() {
    const totalElapsedTime = totalTimeSpent + (isTabActive ? new Date().getTime() - startTime : 0);
    if (dataSent) return; // Check if data has already been sent
    chrome.runtime.sendMessage({
        action: 'sendTrackingData',
        data: {
            timeSpent: totalElapsedTime,
            url: window.location.href
        }
    });
    dataSent = true; // Set the flag to true after sending data
}

function handlePageExit() {
    pauseTime();
    sendTrackingData();
}

// Listen for messages from the background script (start or stop tracking)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'startTracking') {
        trackTime();
    } else if (message.action === 'stopTracking') {
        console.log('Tracking stopped');
        pauseTime();
        sendTrackingData();
        document.removeEventListener('visibilitychange', pauseTime);
        window.removeEventListener('beforeunload', handlePageExit);
        window.removeEventListener('pagehide', handlePageExit);
    }
});

// Automatically start tracking if the extension is enabled
window.onload = () => {
    chrome.storage.local.get('extensionEnabled', (result) => {
        if (result.extensionEnabled) {
            trackTime();
        }
    });
};
