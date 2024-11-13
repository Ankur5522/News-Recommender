const toggleTracking = document.getElementById('toggleTracking');
const statusText = document.getElementById('statusText');

// Retrieve the current state from Chrome storage and update the UI
chrome.storage.local.get('extensionEnabled', (result) => {
    const isEnabled = result.extensionEnabled || false;
    toggleTracking.checked = isEnabled;
    updateStatusText(isEnabled);
});

// Update the status text based on the toggle state
function updateStatusText(isEnabled) {
    if (isEnabled) {
        statusText.textContent = 'Extension is Enabled';
    } else {
        statusText.textContent = 'Extension is Disabled';
    }
}

// Listen for toggle changes
toggleTracking.addEventListener('change', () => {
    const isEnabled = toggleTracking.checked;
    
    // Update Chrome storage with the new state
    chrome.storage.local.set({ extensionEnabled: isEnabled }, () => {
        console.log(`Extension is now ${isEnabled ? 'enabled' : 'disabled'}`);
        chrome.runtime.sendMessage({
            action: isEnabled ? 'enableTracking' : 'disableTracking'
        });
    });

    updateStatusText(isEnabled);
});

// Manual data send button
document.getElementById('sendData').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        let activeTab = tabs[0];
        console.log('Manual send for URL:', activeTab.url);
        fetch('https://your-api-url.com/manual-send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: activeTab.url })
        }).then(response => console.log('Data sent manually!'))
          .catch(error => console.error('Error sending data:', error));
    });
});
