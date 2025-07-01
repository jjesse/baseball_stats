/**
 * Interactive Table Library for MLB Stats Dashboard
 * Adds sorting, filtering, and search functionality to existing tables
 */

class InteractiveTable {
    constructor(tableId, options = {}) {
        this.table = document.getElementById(tableId);
        this.options = {
            enableSearch: true,
            enableSort: true,
            enableFilter: true,
            searchPlaceholder: "Search players...",
            itemsPerPage: 25,
            ...options
        };
        
        this.originalData = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        
        this.init();
    }
    
    init() {
        if (!this.table) return;
        
        // Store original table data
        this.storeOriginalData();
        
        // Create interactive controls
        this.createControls();
        
        // Add sorting to headers
        this.addSortingToHeaders();
        
        // Initial render
        this.renderTable();
    }
    
    storeOriginalData() {
        const rows = Array.from(this.table.querySelectorAll('tbody tr'));
        this.originalData = rows.map(row => {
            const cells = Array.from(row.querySelectorAll('td'));
            return {
                element: row.cloneNode(true),
                data: cells.map(cell => ({
                    text: cell.textContent.trim(),
                    numeric: this.isNumeric(cell.textContent.trim())
                }))
            };
        });
        this.filteredData = [...this.originalData];
    }
    
    createControls() {
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'interactive-controls';
        controlsDiv.innerHTML = `
            <div class="table-controls">
                ${this.options.enableSearch ? `
                    <div class="search-container">
                        <input type="text" 
                               id="${this.table.id}_search" 
                               placeholder="${this.options.searchPlaceholder}"
                               class="table-search">
                        <span class="search-icon">🔍</span>
                    </div>
                ` : ''}
                
                ${this.options.enableFilter ? `
                    <div class="filter-container">
                        <select id="${this.table.id}_teamFilter" class="table-filter">
                            <option value="">All Teams</option>
                        </select>
                        <select id="${this.table.id}_statFilter" class="table-filter">
                            <option value="">All Stats</option>
                            <option value="elite">Elite (Top 10%)</option>
                            <option value="good">Good (Top 25%)</option>
                            <option value="average">Average (25-75%)</option>
                            <option value="below">Below Average (Bottom 25%)</option>
                        </select>
                    </div>
                ` : ''}
                
                <div class="results-info">
                    <span id="${this.table.id}_results">Showing ${this.filteredData.length} players</span>
                </div>
            </div>
            
            <div class="pagination-controls">
                <button id="${this.table.id}_prevPage" class="page-btn">← Previous</button>
                <span id="${this.table.id}_pageInfo" class="page-info">Page 1</span>
                <button id="${this.table.id}_nextPage" class="page-btn">Next →</button>
            </div>
        `;
        
        this.table.parentNode.insertBefore(controlsDiv, this.table);
        
        // Add event listeners
        this.addEventListeners();
        
        // Populate team filter
        this.populateTeamFilter();
    }
    
    addEventListeners() {
        // Search
        if (this.options.enableSearch) {
            const searchInput = document.getElementById(`${this.table.id}_search`);
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
        
        // Filters
        if (this.options.enableFilter) {
            const teamFilter = document.getElementById(`${this.table.id}_teamFilter`);
            const statFilter = document.getElementById(`${this.table.id}_statFilter`);
            
            teamFilter.addEventListener('change', () => this.applyFilters());
            statFilter.addEventListener('change', () => this.applyFilters());
        }
        
        // Pagination
        document.getElementById(`${this.table.id}_prevPage`).addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.renderTable();
            }
        });
        
        document.getElementById(`${this.table.id}_nextPage`).addEventListener('click', () => {
            const totalPages = Math.ceil(this.filteredData.length / this.options.itemsPerPage);
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.renderTable();
            }
        });
    }
    
    addSortingToHeaders() {
        if (!this.options.enableSort) return;
        
        const headers = this.table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.style.userSelect = 'none';
            header.style.position = 'relative';
            
            // Add sort indicator
            const sortIndicator = document.createElement('span');
            sortIndicator.className = 'sort-indicator';
            sortIndicator.innerHTML = ' ↕️';
            header.appendChild(sortIndicator);
            
            header.addEventListener('click', () => {
                this.handleSort(index, header);
            });
        });
    }
    
    handleSort(columnIndex, headerElement) {
        // Toggle sort direction if same column, otherwise default to ascending
        if (this.sortColumn === columnIndex) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortDirection = 'asc';
            this.sortColumn = columnIndex;
        }
        
        // Update all header indicators
        this.table.querySelectorAll('.sort-indicator').forEach(indicator => {
            indicator.innerHTML = ' ↕️';
        });
        
        // Update current header indicator
        const indicator = headerElement.querySelector('.sort-indicator');
        indicator.innerHTML = this.sortDirection === 'asc' ? ' ↑' : ' ↓';
        
        // Sort the data
        this.filteredData.sort((a, b) => {
            const aValue = a.data[columnIndex];
            const bValue = b.data[columnIndex];
            
            let comparison = 0;
            if (aValue.numeric && bValue.numeric) {
                const aNum = parseFloat(aValue.text) || 0;
                const bNum = parseFloat(bValue.text) || 0;
                comparison = aNum - bNum;
            } else {
                comparison = aValue.text.localeCompare(bValue.text);
            }
            
            return this.sortDirection === 'asc' ? comparison : -comparison;
        });
        
        this.currentPage = 1;
        this.renderTable();
    }
    
    handleSearch(searchTerm) {
        const term = searchTerm.toLowerCase();
        
        if (term === '') {
            this.filteredData = [...this.originalData];
        } else {
            this.filteredData = this.originalData.filter(row => {
                return row.data.some(cell => 
                    cell.text.toLowerCase().includes(term)
                );
            });
        }
        
        this.currentPage = 1;
        this.applyFilters();
    }
    
    applyFilters() {
        let filtered = [...this.filteredData];
        
        // Team filter
        const teamFilter = document.getElementById(`${this.table.id}_teamFilter`);
        if (teamFilter && teamFilter.value) {
            filtered = filtered.filter(row => {
                const teamCell = row.data[1]; // Assuming team is in column 1
                return teamCell && teamCell.text === teamFilter.value;
            });
        }
        
        // Stat performance filter (simplified - you can enhance this)
        const statFilter = document.getElementById(`${this.table.id}_statFilter`);
        if (statFilter && statFilter.value) {
            // This is a simplified version - you'd want to implement specific logic
            // for each stat type based on what constitutes "elite", "good", etc.
        }
        
        this.filteredData = filtered;
        this.currentPage = 1;
        this.renderTable();
    }
    
    populateTeamFilter() {
        const teamFilter = document.getElementById(`${this.table.id}_teamFilter`);
        if (!teamFilter) return;
        
        const teams = new Set();
        this.originalData.forEach(row => {
            if (row.data[1]) { // Assuming team is in column 1
                teams.add(row.data[1].text);
            }
        });
        
        Array.from(teams).sort().forEach(team => {
            if (team && team !== '') {
                const option = document.createElement('option');
                option.value = team;
                option.textContent = team;
                teamFilter.appendChild(option);
            }
        });
    }
    
    renderTable() {
        const tbody = this.table.querySelector('tbody');
        tbody.innerHTML = '';
        
        // Calculate pagination
        const startIndex = (this.currentPage - 1) * this.options.itemsPerPage;
        const endIndex = startIndex + this.options.itemsPerPage;
        const pageData = this.filteredData.slice(startIndex, endIndex);
        
        // Render rows
        pageData.forEach(row => {
            tbody.appendChild(row.element.cloneNode(true));
        });
        
        // Update pagination info
        this.updatePaginationInfo();
        
        // Update results count
        const resultsSpan = document.getElementById(`${this.table.id}_results`);
        if (resultsSpan) {
            resultsSpan.textContent = `Showing ${pageData.length} of ${this.filteredData.length} players`;
        }
    }
    
    updatePaginationInfo() {
        const totalPages = Math.ceil(this.filteredData.length / this.options.itemsPerPage);
        const pageInfo = document.getElementById(`${this.table.id}_pageInfo`);
        const prevBtn = document.getElementById(`${this.table.id}_prevPage`);
        const nextBtn = document.getElementById(`${this.table.id}_nextPage`);
        
        if (pageInfo) {
            pageInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        }
        
        if (prevBtn) {
            prevBtn.disabled = this.currentPage === 1;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentPage === totalPages || totalPages === 0;
        }
    }
    
    isNumeric(value) {
        return !isNaN(parseFloat(value)) && isFinite(value);
    }
}

// Auto-initialize tables when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Look for tables with class 'interactive-table'
    const tables = document.querySelectorAll('table.interactive-table');
    tables.forEach(table => {
        new InteractiveTable(table.id);
    });
});

// Export for manual initialization
window.InteractiveTable = InteractiveTable;