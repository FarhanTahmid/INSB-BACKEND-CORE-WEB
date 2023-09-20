function showTab(tabId) {
    // Hide all tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tabContent => {
        tabContent.style.display = 'none';
    });

    // Deactivate all tabs
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });

    // Show the selected tab content
    const selectedTabContent = document.getElementById(tabId);
    if (selectedTabContent) {
        selectedTabContent.style.display = 'block';
    }

    // Activate the clicked tab
    const selectedTab = document.querySelector(`.tab[data-tab="${tabId}"]`);
    if (selectedTab) {
        selectedTab.classList.toggle('active');
    }
}

// Show the initial tab
showTab('tab1');