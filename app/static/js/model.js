// /app/assets/dashboard-core.js

/**
 * PRODUCTION-READY HR DASHBOARD - CORE FUNCTIONALITY
 * =================================================
 */

class HRDashboard {
    // Individual chart rendering methods
    renderRiskHeatmap() {
        const data = [this.state.dashboardData.charts.riskHeatmap];
        const layout = { ...this.chartConfigs.theme.layout, title: '' };
        return Plotly.newPlot('risk-heatmap-chart', data, layout, this.chartConfigs);
    }

    renderWorkforceROI() {
        const data = this.state.dashboardData.charts.workforceROI;
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            xaxis: { title: 'Average Salary' },
            yaxis: { title: 'Risk Score' }
        };
        return Plotly.newPlot('workforce-roi-chart', data, layout, this.chartConfigs);
    }

    renderAttritionForecast() {
        const data = [this.state.dashboardData.charts.attritionForecast];
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            xaxis: { title: 'Month' },
            yaxis: { title: 'Attrition Rate (%)' }
        };
        return Plotly.newPlot('attrition-forecast-chart', data, layout, this.chartConfigs);
    }

    renderAttritionAnalysis() {
        const data = [this.state.dashboardData.charts.attritionAnalysis];
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            xaxis: { title: 'Department' },
            yaxis: { title: 'Attrition Rate' }
        };
        return Plotly.newPlot('attrition-analysis-chart', data, layout, this.chartConfigs);
    }

    renderRecruitmentPerformance() {
        const data = this.state.dashboardData.charts.recruitmentPerformance;
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            xaxis: { title: 'Days to Fill' },
            yaxis: { title: 'Conversion Rate' }
        };
        return Plotly.newPlot('recruitment-performance-chart', data, layout, this.chartConfigs);
    }

    renderEmployeeEngagement() {
        const data = this.state.dashboardData.charts.employeeEngagement;
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            barmode: 'group',
            xaxis: { title: 'Department' },
            yaxis: { title: 'Average Score' }
        };
        return Plotly.newPlot('employee-engagement-chart', data, layout, this.chartConfigs);
    }

    renderPerformanceAnalytics() {
        const data = [this.state.dashboardData.charts.performanceAnalytics];
        const layout = { ...this.chartConfigs.theme.layout, title: '' };
        return Plotly.newPlot('performance-analytics-chart', data, layout, this.chartConfigs);
    }

    renderWorkforceDemographics() {
        const data = [this.state.dashboardData.charts.workforceDemographics];
        const layout = { ...this.chartConfigs.theme.layout, title: '' };
        return Plotly.newPlot('workforce-demographics-chart', data, layout, this.chartConfigs);
    }

    renderCompensationIntelligence() {
        const data = this.state.dashboardData.charts.compensationIntelligence;
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            xaxis: { title: 'Average Salary' },
            yaxis: { title: 'Risk Score' }
        };
        return Plotly.newPlot('compensation-intelligence-chart', data, layout, this.chartConfigs);
    }

    renderLearningROI() {
        const data = [this.state.dashboardData.charts.learningROI];
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            xaxis: { title: 'Training Hours' },
            yaxis: { title: 'Score' }
        };
        return Plotly.newPlot('learning-roi-chart', data, layout, this.chartConfigs);
    }

    renderManagerPerformance() {
        const data = this.state.dashboardData.charts.managerPerformance;
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            xaxis: { title: 'Manager Satisfaction' },
            yaxis: { title: 'Team Risk Score' }
        };
        return Plotly.newPlot('manager-performance-chart', data, layout, this.chartConfigs);
    }

    renderTalentPipeline() {
        const data = [this.state.dashboardData.charts.talentPipeline];
        const layout = { ...this.chartConfigs.theme.layout, title: '' };
        return Plotly.newPlot('talent-pipeline-chart', data, layout, this.chartConfigs);
    }

    renderJourneyMapping() {
        const data = [this.state.dashboardData.charts.journeyMapping];
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            xaxis: { title: 'Tenure' },
            yaxis: { title: 'Job Satisfaction' }
        };
        return Plotly.newPlot('journey-mapping-chart', data, layout, this.chartConfigs);
    }

    renderCompensationAnalytics() {
        const data = [this.state.dashboardData.charts.compensationAnalytics];
        const layout = { 
            ...this.chartConfigs.theme.layout, 
            title: '',
            xaxis: { title: 'Job Role', tickangle: -45 },
            yaxis: { title: 'Average Salary' }
        };
        return Plotly.newPlot('compensation-analytics-chart', data, layout, this.chartConfigs);
    }
    constructor() {
        this.initializeState();
        this.initializeEventListeners();
        this.loadDashboardData();
    }

    initializeState() {
        this.state = {
            sidebarOpen: window.innerWidth > 1200,
            currentSection: 'executive',
            refreshInterval: 30000, // 30 seconds
            lastUpdated: new Date(),
            dashboardData: null,
            charts: {},
            realTimeEnabled: true
        };
        
        // Store chart configurations
        this.chartConfigs = {
            theme: {
                layout: {
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { family: 'Inter, sans-serif', color: '#374151' }
                },
                colorway: ['#2563eb', '#059669', '#dc2626', '#d97706', '#7c3aed', '#0891b2'],
                margin: { t: 20, r: 20, b: 40, l: 40 }
            },
            responsive: true,
            displayModeBar: false
        };
    }

    initializeEventListeners() {
        // DOM ready
        document.addEventListener('DOMContentLoaded', () => {
            this.hideLoadingOverlay();
            this.setupNavigationHandlers();
            this.setupResizeHandler();
            this.setupTooltips();
            this.updateTimestamp();
            this.startRealTimeUpdates();
        });

        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // Navigation links
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToSection(link.dataset.section);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'r':
                        e.preventDefault();
                        this.refreshDashboard();
                        break;
                    case 'b':
                        e.preventDefault();
                        this.toggleSidebar();
                        break;
                }
            }
        });
    }

    hideLoadingOverlay() {
        setTimeout(() => {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.style.opacity = '0';
                setTimeout(() => overlay.remove(), 300);
            }
        }, 1000);
    }

    setupNavigationHandlers() {
        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });

        // Update active navigation on scroll
        this.setupScrollSpy();
    }

    setupScrollSpy() {
        const sections = document.querySelectorAll('.dashboard-section');
        const navLinks = document.querySelectorAll('.sidebar-link');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.id.replace('-', '');
                    const activeLink = document.querySelector(`[data-section="${sectionId}"]`);
                    
                    // Remove active class from all links
                    navLinks.forEach(link => link.classList.remove('active'));
                    
                    // Add active class to current link
                    if (activeLink) {
                        activeLink.classList.add('active');
                        this.state.currentSection = sectionId;
                    }
                }
            });
        }, { threshold: 0.3 });

        sections.forEach(section => observer.observe(section));
    }

    setupResizeHandler() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
                this.redrawCharts();
            }, 250);
        });
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        }
    }

    handleResize() {
        const isMobile = window.innerWidth < 1200;
        if (isMobile && this.state.sidebarOpen) {
            this.closeSidebar();
        }
    }

    toggleSidebar() {
        this.state.sidebarOpen = !this.state.sidebarOpen;
        this.updateSidebarState();
    }

    updateSidebarState() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('main-content');
        
        if (this.state.sidebarOpen) {
            sidebar?.classList.add('active');
            mainContent?.classList.add('sidebar-open');
        } else {
            sidebar?.classList.remove('active');
            mainContent?.classList.remove('sidebar-open');
        }
        
        // Redraw charts after sidebar animation
        setTimeout(() => this.redrawCharts(), 300);
    }

    closeSidebar() {
        this.state.sidebarOpen = false;
        this.updateSidebarState();
    }

    navigateToSection(sectionId) {
        const target = document.getElementById(`${sectionId.replace(/([A-Z])/g, '-$1').toLowerCase()}`);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        // Close sidebar on mobile after navigation
        if (window.innerWidth < 1200) {
            this.closeSidebar();
        }
    }

    async loadDashboardData() {
        try {
            // Simulate API call - replace with actual endpoint
            const response = await this.fetchDashboardData();
            this.state.dashboardData = response;
            await this.renderAllCharts();
            this.updateKPIs();
            this.updateTimestamp();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showErrorNotification('Failed to load dashboard data');
        }
    }

    async fetchDashboardData() {
        // Mock data - replace with actual API calls
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    kpis: {
                        replacementCost: 2850,
                        recruitingSpend: 180,
                        revenueAtRisk: 1245,
                        currentAttrition: 14.2,
                        newHires: 23,
                        openPositions: 15,
                        interviewsToday: 38,
                        exitInterviews: 7
                    },
                    charts: this.generateMockChartData()
                });
            }, 500);
        });
    }

    generateMockChartData() {
        // Generate realistic mock data for all charts
        const departments = ['Tech', 'Product', 'Data'];
        const roles = ['Data Scientist', 'Software Engineer', 'Product Manager', 'Data Analyst'];
        
        return {
            riskHeatmap: this.generateHeatmapData(departments, roles),
            workforceROI: this.generateScatterData(departments),
            attritionForecast: this.generateTimeSeriesData(12),
            attritionAnalysis: this.generateBarData(departments),
            recruitmentPerformance: this.generateScatterData(roles),
            employeeEngagement: this.generateGroupedBarData(departments),
            performanceAnalytics: this.generatePieData(['Excellent', 'Good', 'Average', 'Poor']),
            workforceDemographics: this.generateSunburstData(),
            compensationIntelligence: this.generateScatterData(roles),
            learningROI: this.generateLineData(['0-20h', '21-40h', '41-60h', '61-80h', '80+h']),
            managerPerformance: this.generateScatterData(['Manager A', 'Manager B', 'Manager C']),
            riskMonitoring: this.generateTableData(),
            talentPipeline: this.generateFunnelData(['Junior', 'Mid', 'Senior', 'Lead']),
            journeyMapping: this.generateLineData(['<1yr', '1-3yrs', '3-5yrs', '5+yrs']),
            compensationAnalytics: this.generateBarWithErrorData(roles),
            workforcePlanning: this.generateTimeSeriesData(12)
        };
    }

    // Data generation helper methods
    generateHeatmapData(departments, roles) {
        const z = departments.map(() => roles.map(() => Math.random() * 0.8 + 0.1));
        return { x: roles, y: departments, z, type: 'heatmap', colorscale: 'RdYlGn', reversescale: true };
    }

    generateScatterData(categories) {
        return categories.map(cat => ({
            x: [Math.random() * 100000 + 40000],
            y: [Math.random() * 0.8 + 0.1],
            mode: 'markers',
            name: cat,
            type: 'scatter'
        }));
    }

    generateTimeSeriesData(months) {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return {
            x: monthNames.slice(0, months),
            y: Array.from({length: months}, () => Math.random() * 10 + 10),
            type: 'scatter',
            mode: 'lines+markers'
        };
    }

    generateBarData(categories) {
        return {
            x: categories,
            y: categories.map(() => Math.random() * 0.3 + 0.05),
            type: 'bar'
        };
    }

    generateGroupedBarData(categories) {
        return [
            {
                x: categories,
                y: categories.map(() => Math.random() * 2 + 3),
                name: 'Job Satisfaction',
                type: 'bar'
            },
            {
                x: categories,
                y: categories.map(() => Math.random() * 2 + 3),
                name: 'Work-Life Balance',
                type: 'bar'
            }
        ];
    }

    generatePieData(labels) {
        return {
            labels: labels,
            values: labels.map(() => Math.random() * 30 + 10),
            type: 'pie'
        };
    }

    generateSunburstData() {
        return {
            ids: ['Tech', 'Tech/Male', 'Tech/Female', 'Product', 'Product/Male', 'Product/Female'],
            labels: ['Tech', 'Male', 'Female', 'Product', 'Male', 'Female'],
            parents: ['', 'Tech', 'Tech', '', 'Product', 'Product'],
            values: [100, 60, 40, 80, 45, 35],
            type: 'sunburst'
        };
    }

    generateLineData(categories) {
        return {
            x: categories,
            y: categories.map(() => Math.random() * 2 + 3),
            type: 'scatter',
            mode: 'lines+markers'
        };
    }

    generateTableData() {
        const roles = ['Data Scientist', 'Product Manager', 'Software Engineer'];
        return roles.map((role, i) => ({
            employeeId: 1000 + i,
            jobRole: role,
            department: i < 2 ? 'Tech' : 'Product',
            riskScore: (Math.random() * 0.3 + 0.7).toFixed(3)
        }));
    }

    generateFunnelData(levels) {
        const values = levels.map((_, i) => 100 - i * 20);
        return {
            y: levels,
            x: values,
            type: 'funnel'
        };
    }

    generateBarWithErrorData(categories) {
        return {
            x: categories,
            y: categories.map(() => Math.random() * 50000 + 60000),
            error_y: {
                type: 'data',
                array: categories.map(() => Math.random() * 10000 + 5000)
            },
            type: 'bar'
        };
    }

    async renderAllCharts() {
        if (!this.state.dashboardData?.charts) return;

        const chartPromises = [
            this.renderRiskHeatmap(),
            this.renderWorkforceROI(),
            this.renderAttritionForecast(),
            this.renderAttritionAnalysis(),
            this.renderRecruitmentPerformance(),
            this.renderEmployeeEngagement(),
            this.renderPerformanceAnalytics(),
            this.renderWorkforceDemographics(),
            this.renderCompensationIntelligence(),
            this.renderLearningROI(),
            this.renderManagerPerformance(),
            this.renderTalentPipeline(),
            this.renderJourneyMapping(),
            this.renderCompensationAnalytics(),
            this.renderWorkforcePlanning()
        ];

        await Promise.all(chartPromises);
        this.renderRiskMonitoringTable();
    }

    renderWorkforcePlanning() {
        const data = [this.state.dashboardData.charts.workforcePlanning];
        const layout = { ...this.chartConfigs.theme.layout, title: '', xaxis: { title: 'Month' }, yaxis: { title: 'Headcount' } };
        return Plotly.newPlot('workforce-planning-chart', data, layout, this.chartConfigs);
    }

    renderRiskMonitoringTable() {
        const tableData = this.state.dashboardData.charts.riskMonitoring;
        const container = document.getElementById('risk-monitoring-table');
        if (!container) return;
        let html = '<table class="table table-hover"><thead><tr>' +
            '<th>Employee ID</th><th>Job Role</th><th>Department</th><th>Risk Score</th></tr></thead><tbody>';
        tableData.forEach(row => {
            html += `<tr><td>${row.employeeId}</td><td>${row.jobRole}</td><td>${row.department}</td><td>${row.riskScore}</td></tr>`;
        });
        html += '</tbody></table>';
        container.innerHTML = html;
    }

    updateKPIs() {
        const kpis = this.state.dashboardData.kpis;
        const kpiContainer = document.getElementById('financial-kpis');
        if (!kpiContainer) return;
        kpiContainer.innerHTML = '';
        const kpiList = [
            { label: 'Replacement Cost', value: kpis.replacementCost, icon: 'fa-money-bill-wave', class: 'success' },
            { label: 'Recruiting Spend', value: kpis.recruitingSpend, icon: 'fa-search-dollar', class: 'info' },
            { label: 'Revenue at Risk', value: kpis.revenueAtRisk, icon: 'fa-exclamation-triangle', class: 'danger' },
            { label: 'Current Attrition (%)', value: kpis.currentAttrition, icon: 'fa-user-minus', class: 'warning' }
        ];
        kpiList.forEach(kpi => {
            kpiContainer.innerHTML += `
                <div class="col-md-3 mb-3">
                    <div class="kpi-card ${kpi.class}">
                        <div class="kpi-value"><i class="fas ${kpi.icon} me-2"></i>${kpi.value}</div>
                        <div class="kpi-label">${kpi.label}</div>
                    </div>
                </div>
            `;
        });
    }

    updateTimestamp() {
        const tsElem = document.getElementById('last-updated-time');
        if (tsElem) {
            const now = new Date();
            tsElem.textContent = now.toLocaleString();
        }
    }

    showErrorNotification(msg) {
        alert(msg); // Replace with custom toast/notification if desired
    }

    refreshDashboard() {
        this.loadDashboardData();
    }

    startRealTimeUpdates() {
        if (!this.state.realTimeEnabled) return;
        setInterval(() => {
            this.refreshDashboard();
        }, this.state.refreshInterval);
    }
}

// Move chart rendering methods inside the class