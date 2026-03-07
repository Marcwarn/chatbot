// Admin Costs Dashboard - JavaScript
// Beautiful, functional cost monitoring with Swedish language support

// Global variables
let costBreakdownChart = null;
let costTrendChart = null;
let autoRefreshInterval = null;

// Sample data (will be replaced with real API calls)
const SAMPLE_DATA = {
    summary: {
        today: 12.50,
        todayChange: 15,
        month: 342.80,
        budget: 500.00,
        projected: 480.00
    },
    breakdown: {
        labels: ['AI-Rapporter', 'Chatt', 'Databas', 'Hosting', 'Övervakning'],
        data: [280.40, 45.20, 10.00, 5.00, 2.20],
        colors: ['#667eea', '#764ba2', '#10b981', '#3b82f6', '#f59e0b']
    },
    trends: {
        dates: [],
        costs: [],
        forecast: []
    },
    drivers: [
        {
            name: 'Big Five Rapportgenerering',
            detail: 'AI-drivna personlighetsrapporter',
            usage: '1,247 rapporter',
            cost: 215.50,
            percent: 62.9,
            trend: 'up',
            trendValue: 12,
            cacheable: false
        },
        {
            name: 'DISC Rapportgenerering',
            detail: 'AI-drivna DISC-rapporter',
            usage: '385 rapporter',
            cost: 64.90,
            percent: 18.9,
            trend: 'neutral',
            trendValue: 2,
            cacheable: false
        },
        {
            name: 'Chattkonversationer',
            detail: '85% cache-träfffrekvens 🎯',
            usage: '5,823 meddelanden',
            cost: 45.20,
            percent: 13.2,
            trend: 'down',
            trendValue: -23,
            cacheable: true,
            highlight: true
        },
        {
            name: 'Databaslagring',
            detail: 'PostgreSQL',
            usage: '2.4 GB',
            cost: 10.00,
            percent: 2.9,
            trend: 'neutral',
            trendValue: 0,
            cacheable: false
        },
        {
            name: 'Hosting & CDN',
            detail: 'Vercel',
            usage: '28.5K requests',
            cost: 5.00,
            percent: 1.5,
            trend: 'neutral',
            trendValue: 1,
            cacheable: false
        }
    ],
    tokens: {
        input: 24500000,
        output: 17800000,
        inputCost: 73.50,
        outputCost: 267.00,
        totalAICost: 340.50,
        avgTokensBigFive: 3245,
        avgTokensDISC: 2890,
        avgTokensChat: 185,
        cacheHitRate: 85
    },
    optimizations: [
        {
            impact: 'high',
            title: 'Öka Cache-TTL för Rapporter',
            current: 'För närvarande: 1 timme',
            recommended: 'Rekommenderat: 24 timmar',
            savings: 450,
            explanation: 'Många användare återbesöker rapporter inom 24 timmar. Längre cachning minskar duplicerade AI-anrop utan att påverka aktualitet.',
            implemented: false
        },
        {
            impact: 'medium',
            title: 'Optimera Rapport-Promptlängd',
            current: 'Nuvarande: 2,000 tokens',
            recommended: 'Rekommenderat: 1,200 tokens',
            savings: 180,
            explanation: 'Systemprompter kan kondenseras utan kvalitetsförlust. Tester visar att 40% kortare prompter ger samma kvalitet.',
            implemented: false
        },
        {
            impact: 'implemented',
            title: 'Chattmeddelandecachning',
            current: 'Cache-träfffrekvens: 85%',
            recommended: '',
            savings: 320,
            explanation: 'Vanliga frågor cachas, vilket minskar API-anrop med 85%.',
            implemented: true
        },
        {
            impact: 'medium',
            title: 'Implementera Redis-Cache',
            current: 'Ingen cache konfigurerad',
            recommended: 'Redis för snabb cachning',
            savings: 200,
            explanation: 'Redis kan cacha frekventa databassökningar och minska API-anrop ytterligare.',
            implemented: false
        }
    ]
};

// Generate 30 days of trend data
function generateTrendData() {
    const dates = [];
    const costs = [];
    const forecast = [];
    const today = new Date();

    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        dates.push(date.toLocaleDateString('sv-SE', { month: 'short', day: 'numeric' }));

        // Generate realistic cost data with some variation
        const baseCost = 11 + Math.random() * 4;
        const variation = Math.sin(i / 3) * 2;
        costs.push(parseFloat((baseCost + variation).toFixed(2)));
    }

    // Generate forecast for next 7 days
    const lastCost = costs[costs.length - 1];
    for (let i = 1; i <= 7; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() + i);
        dates.push(date.toLocaleDateString('sv-SE', { month: 'short', day: 'numeric' }));
        costs.push(null);
        forecast.push(parseFloat((lastCost + i * 0.3).toFixed(2)));
    }

    return { dates, costs, forecast };
}

// Initialize dashboard
async function loadCostDashboard() {
    try {
        updateLastUpdated();

        // Try to load real data from API
        // For now, use sample data
        const trendData = generateTrendData();
        SAMPLE_DATA.trends = trendData;

        updateSummaryCards(SAMPLE_DATA.summary);
        renderPieChart(SAMPLE_DATA.breakdown);
        renderTrendChart(SAMPLE_DATA.trends);
        renderCostDrivers(SAMPLE_DATA.drivers);
        renderTokenAnalytics(SAMPLE_DATA.tokens);
        renderOptimizations(SAMPLE_DATA.optimizations);

    } catch (error) {
        console.error('Failed to load cost dashboard:', error);
        showError('Kunde inte ladda kostnadsinformation');
    }
}

// Update summary cards
function updateSummaryCards(summary) {
    // Today
    document.getElementById('todayCost').textContent = `$${summary.today.toFixed(2)}`;
    const todayChangeEl = document.getElementById('todayChange');
    todayChangeEl.textContent = `${summary.todayChange > 0 ? '+' : ''}${summary.todayChange}% vs igår`;
    todayChangeEl.className = summary.todayChange > 0 ? 'change positive' : 'change negative';

    // Month
    document.getElementById('monthCost').textContent = `$${summary.month.toFixed(2)}`;
    const monthPercent = ((summary.month / summary.budget) * 100).toFixed(1);
    document.getElementById('monthProgress').textContent = `${monthPercent}% av budget`;

    // Projected
    document.getElementById('projectedCost').textContent = `$${summary.projected.toFixed(2)}`;
    const projectedPercent = ((summary.projected / summary.budget) * 100).toFixed(0);
    const alertEl = document.getElementById('projectedAlert');
    if (projectedPercent >= 95) {
        alertEl.textContent = `⚠️ ${projectedPercent}% av budget`;
        alertEl.style.color = '#ef4444';
    } else if (projectedPercent >= 80) {
        alertEl.textContent = `⚡ ${projectedPercent}% av budget`;
        alertEl.style.color = '#f59e0b';
    } else {
        alertEl.textContent = `✅ ${projectedPercent}% av budget`;
        alertEl.style.color = '#10b981';
    }

    // Budget
    document.getElementById('budgetAmount').textContent = `$${summary.budget.toFixed(2)}`;
    const statusEl = document.getElementById('budgetStatus');
    if (summary.projected <= summary.budget) {
        statusEl.textContent = 'Inom budget';
        statusEl.className = 'status';
    } else {
        statusEl.textContent = 'Risk att överskrida';
        statusEl.className = 'status warning';
    }

    // Update budget progress bar
    updateBudgetProgress(summary.month, summary.projected, summary.budget);
}

// Update budget progress bar
function updateBudgetProgress(current, projected, budget) {
    const currentPercent = (current / budget) * 100;
    const progressFill = document.getElementById('budgetProgressFill');
    const progressText = document.getElementById('budgetProgressText');

    progressFill.style.width = `${Math.min(currentPercent, 100)}%`;
    progressText.textContent = `${currentPercent.toFixed(1)}%`;

    // Color coding
    if (currentPercent >= 100) {
        progressFill.className = 'progress-fill danger';
    } else if (currentPercent >= 80) {
        progressFill.className = 'progress-fill warning';
    } else {
        progressFill.className = 'progress-fill';
    }

    // Update text
    document.getElementById('budgetUsedText').textContent = `$${current.toFixed(2)} / $${budget.toFixed(2)} månadsbudget`;
    const projectedPercent = ((projected / budget) * 100).toFixed(0);
    document.getElementById('budgetProjectionText').textContent = `Prognos: $${projected.toFixed(2)} (${projectedPercent}%)`;
}

// Render pie chart
function renderPieChart(breakdown) {
    const ctx = document.getElementById('costBreakdownChart');

    if (costBreakdownChart) {
        costBreakdownChart.destroy();
    }

    costBreakdownChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: breakdown.labels,
            datasets: [{
                data: breakdown.data,
                backgroundColor: breakdown.colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percent = ((value / total) * 100).toFixed(1);
                            return `${label}: $${value.toFixed(2)} (${percent}%)`;
                        }
                    }
                }
            }
        }
    });

    // Update legend with percentages
    updateBreakdownLegend(breakdown);
}

// Update breakdown legend
function updateBreakdownLegend(breakdown) {
    const total = breakdown.data.reduce((a, b) => a + b, 0);
    const legendEl = document.getElementById('breakdownLegend');

    legendEl.innerHTML = breakdown.labels.map((label, i) => {
        const value = breakdown.data[i];
        const percent = ((value / total) * 100).toFixed(1);
        const color = breakdown.colors[i];

        return `
            <div class="legend-item">
                <div class="legend-color" style="background: ${color}"></div>
                <span><strong>${label}:</strong> $${value.toFixed(2)} (${percent}%)</span>
            </div>
        `;
    }).join('');
}

// Render trend chart
function renderTrendChart(trends) {
    const ctx = document.getElementById('costTrendChart');

    if (costTrendChart) {
        costTrendChart.destroy();
    }

    const budgetPerDay = 500 / 30; // $16.67 per day

    costTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: trends.dates,
            datasets: [
                {
                    label: 'Faktisk kostnad',
                    data: trends.costs,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 3,
                    pointHoverRadius: 6
                },
                {
                    label: 'Prognos',
                    data: trends.forecast.map((v, i) => i < trends.costs.filter(c => c !== null).length ? null : v),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderDash: [5, 5],
                    tension: 0.4,
                    fill: false,
                    pointRadius: 3
                },
                {
                    label: 'Budget/dag',
                    data: new Array(trends.dates.length).fill(budgetPerDay),
                    borderColor: '#ef4444',
                    borderDash: [10, 5],
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            if (value === null) return null;
                            return `${label}: $${value.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

// Render cost drivers table
function renderCostDrivers(drivers) {
    const tbody = document.getElementById('costDriversBody');

    tbody.innerHTML = drivers.map(driver => {
        const trendArrow = driver.trend === 'up' ? '↗' : driver.trend === 'down' ? '↘' : '→';
        const trendText = `${trendArrow} ${driver.trendValue > 0 ? '+' : ''}${driver.trendValue}%`;
        const rowClass = driver.highlight ? 'highlight-savings' : '';

        return `
            <tr class="${rowClass}">
                <td>
                    <strong>${driver.name}</strong>
                    <div class="service-detail">${driver.detail}</div>
                </td>
                <td>${driver.usage}</td>
                <td class="cost-cell">$${driver.cost.toFixed(2)}</td>
                <td>${driver.percent.toFixed(1)}%</td>
                <td class="trend ${driver.trend}">${trendText}${driver.cacheable && driver.trend === 'down' ? ' (cache fungerar!)' : ''}</td>
                <td>
                    ${!driver.implemented ? '<button class="optimize-btn" onclick="optimizeFeature(\'' + driver.name + '\')">Optimera</button>' : ''}
                    <button class="details-btn" onclick="showDriverDetails('${driver.name}')">Detaljer</button>
                </td>
            </tr>
        `;
    }).join('');
}

// Render token analytics
function renderTokenAnalytics(tokens) {
    // Input tokens
    document.getElementById('inputTokens').textContent = formatNumber(tokens.input);
    document.getElementById('inputTokenCost').textContent = `$${tokens.inputCost.toFixed(2)} (${formatNumber(tokens.input)} × $0.003)`;

    // Output tokens
    document.getElementById('outputTokens').textContent = formatNumber(tokens.output);
    document.getElementById('outputTokenCost').textContent = `$${tokens.outputCost.toFixed(2)} (${formatNumber(tokens.output)} × $0.015)`;

    // Total AI cost
    document.getElementById('totalAICost').textContent = `$${tokens.totalAICost.toFixed(2)}`;
    const totalCost = SAMPLE_DATA.summary.month;
    const aiPercent = ((tokens.totalAICost / totalCost) * 100).toFixed(1);
    document.getElementById('aiCostPercent').textContent = `${aiPercent}% av totalkostnad`;

    // Efficiency metrics
    document.getElementById('avgTokensBigFive').textContent = formatNumber(tokens.avgTokensBigFive);
    document.getElementById('avgTokensDISC').textContent = formatNumber(tokens.avgTokensDISC);
    document.getElementById('avgTokensChat').textContent = formatNumber(tokens.avgTokensChat);
    document.getElementById('cacheHitRate').textContent = `${tokens.cacheHitRate}%`;
}

// Render optimizations
function renderOptimizations(optimizations) {
    const grid = document.getElementById('optimizationsGrid');

    grid.innerHTML = optimizations.map(opt => {
        const impactClass = opt.impact;
        const badge = opt.impact === 'high' ? '💰 Hög Påverkan' :
                     opt.impact === 'medium' ? '📊 Medel Påverkan' :
                     '✅ Implementerad';

        return `
            <div class="optimization-card ${impactClass}">
                <div class="badge">${badge}</div>
                <h3>${opt.title}</h3>
                <p>${opt.current}${opt.recommended ? ' | ' + opt.recommended : ''}</p>
                <div class="savings">
                    <strong>Uppskattad besparing: $${opt.savings}/månad</strong>
                </div>
                <div class="explanation">
                    ${opt.explanation}
                </div>
                ${!opt.implemented ? `<button class="apply-btn" onclick="applyOptimization('${opt.title}')">Tillämpa Optimering</button>` : ''}
            </div>
        `;
    }).join('');
}

// Format large numbers
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Update last updated timestamp
function updateLastUpdated() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('sv-SE');
    const dateStr = now.toLocaleDateString('sv-SE');
    document.getElementById('lastUpdated').textContent = `${dateStr} ${timeStr}`;
}

// Export cost report
async function exportCostReport() {
    try {
        const csvContent = generateCostReportCSV();
        downloadCSV(csvContent, `kostnadsrapport-${new Date().toISOString().split('T')[0]}.csv`);
        showSuccess('Rapport exporterad framgångsrikt!');
    } catch (error) {
        console.error('Export failed:', error);
        showError('Kunde inte exportera rapport');
    }
}

// Generate CSV content
function generateCostReportCSV() {
    let csv = 'Kostnadsrapport - Persona Admin\n\n';
    csv += 'Sammanfattning\n';
    csv += `Idag,$${SAMPLE_DATA.summary.today.toFixed(2)}\n`;
    csv += `Denna månad,$${SAMPLE_DATA.summary.month.toFixed(2)}\n`;
    csv += `Prognos,$${SAMPLE_DATA.summary.projected.toFixed(2)}\n`;
    csv += `Budget,$${SAMPLE_DATA.summary.budget.toFixed(2)}\n\n`;

    csv += 'Kostnadsdrivare\n';
    csv += 'Funktion,Användning,Kostnad,Procent,Trend\n';
    SAMPLE_DATA.drivers.forEach(driver => {
        csv += `"${driver.name}",${driver.usage},$${driver.cost.toFixed(2)},${driver.percent.toFixed(1)}%,${driver.trendValue}%\n`;
    });

    return csv;
}

// Download CSV
function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Save alert settings
function saveAlertSettings() {
    const settings = {
        alert50: document.getElementById('alert50').checked,
        alert80: document.getElementById('alert80').checked,
        alert100: document.getElementById('alert100').checked,
        alertProjected: document.getElementById('alertProjected').checked
    };

    localStorage.setItem('costAlertSettings', JSON.stringify(settings));
    showSuccess('Varningsinställningar sparade!');
}

// Update budget
function updateBudget() {
    const newBudget = parseFloat(document.getElementById('monthlyBudget').value);

    if (isNaN(newBudget) || newBudget <= 0) {
        showError('Vänligen ange en giltig budget');
        return;
    }

    SAMPLE_DATA.summary.budget = newBudget;
    updateSummaryCards(SAMPLE_DATA.summary);
    localStorage.setItem('monthlyBudget', newBudget);
    showSuccess(`Budget uppdaterad till $${newBudget.toFixed(2)}/månad`);
}

// Apply optimization
function applyOptimization(title) {
    if (confirm(`Vill du tillämpa optimeringen: ${title}?`)) {
        showSuccess(`Optimering "${title}" kommer att tillämpas. Detta kan ta några minuter.`);
        // In production, this would call an API endpoint
    }
}

// Show driver details
function showDriverDetails(name) {
    alert(`Visar detaljer för: ${name}\n\n(Detta skulle öppna en detaljerad vy i produktionsversionen)`);
}

// Optimize feature
function optimizeFeature(name) {
    alert(`Optimerar: ${name}\n\n(Detta skulle öppna optimeringsalternativ i produktionsversionen)`);
}

// Show service details
function showServiceDetails(service) {
    alert(`Visar tjänstedetaljer för: ${service}\n\n(Detta skulle öppna detaljerad tjänsteövervakning i produktionsversionen)`);
}

// Setup Redis
function setupRedis() {
    if (confirm('Vill du konfigurera Redis-cachning? Detta kommer att kräva serveråtkomst.')) {
        showSuccess('Redis-konfiguration initierad. Kontakta systemadministratören för att slutföra installationen.');
    }
}

// Show success message
function showSuccess(message) {
    // Simple alert for now - in production, use a toast notification
    alert('✅ ' + message);
}

// Show error message
function showError(message) {
    // Simple alert for now - in production, use a toast notification
    alert('❌ ' + message);
}

// Load saved settings
function loadSavedSettings() {
    // Load alert settings
    const alertSettings = localStorage.getItem('costAlertSettings');
    if (alertSettings) {
        const settings = JSON.parse(alertSettings);
        document.getElementById('alert50').checked = settings.alert50;
        document.getElementById('alert80').checked = settings.alert80;
        document.getElementById('alert100').checked = settings.alert100;
        document.getElementById('alertProjected').checked = settings.alertProjected;
    }

    // Load budget
    const savedBudget = localStorage.getItem('monthlyBudget');
    if (savedBudget) {
        const budget = parseFloat(savedBudget);
        document.getElementById('monthlyBudget').value = budget;
        SAMPLE_DATA.summary.budget = budget;
    }
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSavedSettings();
    loadCostDashboard();

    // Auto-refresh every 5 minutes
    autoRefreshInterval = setInterval(loadCostDashboard, 5 * 60 * 1000);
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});
