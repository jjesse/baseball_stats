const utils = globalThis.MLBUtils;

if (!utils) {
    throw new Error('MLBUtils is not available. Ensure assets/shared.js is loaded before this module.');
}

export const {
    buildFooterText,
    createFooterUpdater,
    escapeHtml,
    exportSectionToCsv,
    fetchJsonWithRetry,
    formatTimestamp,
    getFavorites,
    initDarkModeToggle,
    isFavorite,
    makeSortableHeadersAccessible,
    setupAccessibleTabs,
    toggleFavorite,
    updateCanonicalUrls
} = utils;
