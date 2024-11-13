let startTime = null;
let totalTimeSpent = 0;
let isTabActive = true;

function trackTime() {
    console.log('Tracking time...');

    if (!startTime) {
        startTime = new Date().getTime();
    }

    // Track visibility changes (tab becoming inactive/active)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            pauseTime();
        } else {
            resumeTime();
        }
    });

    // Track when the tab is about to be closed
    window.addEventListener('beforeunload', () => {
        pauseTime();
        sendTrackingData();  // Send the tracking data before the page is unloaded
    });

    // Also handle pagehide event as a fallback
    window.addEventListener('pagehide', () => {
        pauseTime();
        sendTrackingData();  // Send data when the page is hidden
    });
}

function pauseTime() {
    if (!isTabActive) return;  // If already inactive, do nothing
    const endTime = new Date().getTime();
    totalTimeSpent += endTime - startTime;
    isTabActive = false;
    console.log(`Tab became inactive. Time paused at: ${totalTimeSpent / 1000} seconds`);
}

function resumeTime() {
    if (isTabActive) return;  // If already active, do nothing
    startTime = new Date().getTime();  // Reset start time to current time
    isTabActive = true;
    console.log('Tab became active again. Resuming time tracking...');
}

function logElapsedTime() {
    const totalElapsedTime = totalTimeSpent + (isTabActive ? new Date().getTime() - startTime : 0);
    const minutes = Math.floor(totalElapsedTime / 60000);
    const seconds = Math.floor((totalElapsedTime % 60000) / 1000);

    console.log(`Time spent on the webpage: ${minutes} minutes ${seconds} seconds`);
}

function sendTrackingData() {
    const totalElapsedTime = totalTimeSpent + (isTabActive ? new Date().getTime() - startTime : 0);

    chrome.runtime.sendMessage({
        action: 'sendTrackingData',
        data: {
            timeSpent: totalElapsedTime,  // Send the total time spent
            url: window.location.href
        }
    });
}

// Listen for messages from the background script (start or stop tracking)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'startTracking') {
        trackTime();
    } else if (message.action === 'stopTracking') {
        console.log('Tracking stopped');
        pauseTime();  // Pause time immediately when tracking stops
        sendTrackingData();  // Send data right when tracking is stopped
        document.removeEventListener('visibilitychange', pauseTime);
        window.removeEventListener('beforeunload', sendTrackingData);
        window.removeEventListener('pagehide', sendTrackingData);
    }
});

// Automatically start tracking when the extension is enabled
window.onload = () => {
    chrome.storage.local.get('extensionEnabled', (result) => {
        if (result.extensionEnabled) {
            trackTime();
        }
    });
};
