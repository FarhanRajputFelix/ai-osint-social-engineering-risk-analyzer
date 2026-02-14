/**
 * AI-Based OSINT Correlation & Social Engineering Exposure Analysis System
 * Frontend Application Logic
 * Handles API calls, dynamic rendering, and interactive visualizations.
 */

// ─── API Configuration ─────────────────────────────────────────
const API_BASE = window.location.origin;

// ─── Particle Background ───────────────────────────────────────
function initParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    for (let i = 0; i < 30; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        p.style.left = Math.random() * 100 + '%';
        p.style.animationDelay = Math.random() * 8 + 's';
        p.style.animationDuration = (6 + Math.random() * 6) + 's';
        container.appendChild(p);
    }
}

// ─── Navigation ────────────────────────────────────────────────
function showSection(name) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));

    const section = document.getElementById('section-' + name);
    if (section) section.classList.add('active');

    const nav = document.getElementById('nav-' + name);
    if (nav) nav.classList.add('active');

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ─── Tab Switching ─────────────────────────────────────────────
function switchTab(tabName) {
    document.querySelectorAll('.analysis-tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + tabName).classList.add('active');

    document.querySelectorAll('[id^="panel-"]').forEach(p => {
        if (['panel-full', 'panel-image', 'panel-username'].includes(p.id)) {
            p.style.display = 'none';
        }
    });
    document.getElementById('panel-' + tabName).style.display = 'block';
}

// ─── Image Preview ─────────────────────────────────────────────
function previewImage(input, previewId, imgId) {
    const preview = document.getElementById(previewId);
    const img = document.getElementById(imgId);

    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            img.src = e.target.result;
            preview.classList.add('active');
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// ─── Drag & Drop Setup ────────────────────────────────────────
function setupDropZones() {
    const zones = document.querySelectorAll('.dropzone');
    zones.forEach(zone => {
        zone.addEventListener('dragover', e => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });
        zone.addEventListener('drop', e => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            const fileInput = zone.parentElement.querySelector('input[type="file"]');
            if (fileInput && e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    });
}

// ─── Loading Overlay ───────────────────────────────────────────
function showLoading(text) {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingText.textContent = text || 'Processing analysis...';
    overlay.classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

// ─── Loading Messages Rotation ─────────────────────────────────
const loadingMessages = [
    'Initializing AI analysis engines...',
    'Scanning cross-platform databases...',
    'Running face detection algorithms...',
    'Computing perceptual image hashes...',
    'Analyzing username patterns...',
    'Correlating cross-platform data...',
    'Fusing multi-modal intelligence...',
    'Assessing social engineering vectors...',
    'Generating risk assessment report...',
    'Compiling aggregated profile data...',
];

let loadingInterval = null;
function startLoadingMessages() {
    let idx = 0;
    const el = document.getElementById('loadingText');
    loadingInterval = setInterval(() => {
        el.textContent = loadingMessages[idx % loadingMessages.length];
        idx++;
    }, 1500);
}

function stopLoadingMessages() {
    if (loadingInterval) clearInterval(loadingInterval);
}

// ─── Safe API Response Handler ─────────────────────────────────

async function handleApiResponse(response) {
    const text = await response.text();
    let data;
    try {
        data = JSON.parse(text);
    } catch (e) {
        // Server returned non-JSON (e.g. plain "Internal Server Error")
        throw new Error(text || `Server error (HTTP ${response.status})`);
    }
    if (!response.ok) {
        throw new Error(data.detail || data.error || data.message || `Analysis failed (HTTP ${response.status})`);
    }
    return data;
}

// ─── API Calls ─────────────────────────────────────────────────

async function runFullAnalysis(event) {
    event.preventDefault();

    const username = document.getElementById('full-username').value.trim();
    if (!username) return alert('Please enter a username or name');

    const bio = document.getElementById('full-bio').value;
    const url = document.getElementById('full-url').value;
    const location = document.getElementById('full-location').value;
    const occupation = document.getElementById('full-job').value;
    const imageInput = document.getElementById('full-image');

    const formData = new FormData();
    formData.append('username', username);
    formData.append('bio', bio || '');
    formData.append('profile_url', url || '');
    formData.append('location', location || '');
    formData.append('occupation', occupation || '');

    if (imageInput.files.length > 0) {
        formData.append('image', imageInput.files[0]);
    }

    showLoading('Starting deep OSINT investigation...');
    startLoadingMessages();

    try {
        const response = await fetch(`${API_BASE}/api/analyze/full`, {
            method: 'POST',
            body: formData,
        });
        const data = await handleApiResponse(response);
        renderFullResults(data);
    } catch (error) {
        alert('Analysis Error: ' + error.message);
    } finally {
        stopLoadingMessages();
        hideLoading();
    }
}

// Redundant functions removed to simplify UI flow


// ─── Results Rendering ─────────────────────────────────────────

function renderFullResults(data) {
    const risk = data.risk_assessment;
    const corr = data.correlation;

    // Session info
    document.getElementById('report-session').textContent = data.session_id.substring(0, 8) + '...';
    document.getElementById('report-timestamp').textContent = new Date(data.timestamp).toLocaleString();
    document.getElementById('results-subtitle').textContent = 'Full OSINT Correlation Analysis Report';

    // Executive Summary
    const summary = risk?.executive_summary || corr?.data_fusion_summary || 'Analysis complete.';
    document.getElementById('exec-summary-text').textContent = summary;

    // Risk Gauge
    const overall = risk?.overall_risk || { score: 0, level: 'Unknown', headline: '', description: '' };
    drawRiskGauge(overall.score, overall.color || '#00f0ff');
    animateCounter('riskScore', overall.score);
    document.getElementById('riskLevel').textContent = overall.level;
    document.getElementById('riskLevel').style.background = (overall.color || '#00f0ff') + '22';
    document.getElementById('riskLevel').style.color = overall.color || '#00f0ff';
    document.getElementById('riskHeadline').textContent = overall.headline || '';
    document.getElementById('riskDescription').textContent = overall.description || '';

    // Exposure Metrics
    const metrics = risk?.exposure_metrics || {};
    renderMetrics(metrics);

    // Aggregated Profile
    renderAggregatedProfile(data);

    // Platform Intelligence
    const platforms = corr?.combined_platform_intelligence || [];
    renderPlatformGrid(platforms);

    // Correlation Details
    const corrDetails = corr?.correlation_details || [];
    renderCorrelationDetails(corrDetails);

    // Attack Vectors
    const attacks = risk?.attack_vector_assessment || [];
    renderAttackVectors(attacks);

    // Recommendations
    const recs = risk?.defensive_recommendations || [];
    renderRecommendations(recs);

    showSection('results');
}

function renderImageResults(data) {
    document.getElementById('report-session').textContent = data.session_id.substring(0, 8) + '...';
    document.getElementById('report-timestamp').textContent = new Date(data.timestamp).toLocaleString();
    document.getElementById('results-subtitle').textContent = 'Image Similarity Analysis Report';

    // Summary
    document.getElementById('exec-summary-text').textContent = data.analysis_summary || 'Image analysis complete.';

    // Risk gauge from image reuse score
    const reuseScore = data.image_reuse_score || { score: 0, level: 'Low' };
    const color = getColorForLevel(reuseScore.level);
    drawRiskGauge(reuseScore.score, color);
    animateCounter('riskScore', reuseScore.score);
    document.getElementById('riskLevel').textContent = reuseScore.level;
    document.getElementById('riskLevel').style.background = color + '22';
    document.getElementById('riskLevel').style.color = color;
    document.getElementById('riskHeadline').textContent = 'Image Reuse Risk Assessment';
    document.getElementById('riskDescription').textContent = reuseScore.description || '';

    // Metrics from image data
    const face = data.face_detection || {};
    const meta = data.image_metadata || {};
    renderMetrics({
        platforms_exposed: (data.cross_platform_matches || []).length,
        total_data_points_exposed: face.faces_found || 0,
        critical_platforms: (data.cross_platform_matches || []).filter(m => m.similarity_score > 90).length,
        digital_footprint_score: reuseScore.score,
    });

    // Hide aggregated profile for image-only
    document.getElementById('aggregatedProfile').style.display = 'none';

    // Platform matches
    const platforms = (data.cross_platform_matches || []).map(m => ({
        platform: m.platform,
        icon: m.icon,
        color: m.color,
        image_similarity: m.similarity_score,
        username_confidence: null,
        combined_score: m.similarity_score,
        combined_risk: m.similarity_score > 85 ? 'Critical' : m.similarity_score > 70 ? 'High' : m.similarity_score > 50 ? 'Medium' : 'Low',
        data_points: m.data_gathered || {},
        profile_url: m.profile_url, // Pass profile URL
        data_points: m.data_gathered, // Pass gathered data for persona display
    }));
    renderPlatformGrid(platforms);

    // [NEW] Render Metadata
    if (data.image_metadata) {
        renderMetadata(data.image_metadata);
    }

    // [NEW] Show Aggregated Profile (Persona) if valid
    const mainMatch = platforms[0];
    if (mainMatch && mainMatch.data_points && (mainMatch.data_points.display_name !== 'Unknown Subject' || mainMatch.data_points.bio_template)) {
        // Construct a pseudo-aggregated profile for the image persona
        renderAggregatedProfileDirect({
            total_platforms_found: platforms.length,
            exact_username_matches: 0,
            cross_platform_consistency: 'N/A',
            digital_footprint_size: 'Derived from Image',
            overall_activity: 'Inferred',
            public_profiles: platforms.length,
            display_name_override: mainMatch.data_points.display_name,
            bio_override: mainMatch.data_points.bio_template
        });
    } else {
        document.getElementById('aggregatedProfile').style.display = 'none';
    }
    document.getElementById('attackCard').style.display = 'none';
    document.getElementById('recCard').style.display = 'none';

    showSection('results');
}

function renderUsernameResults(data) {
    document.getElementById('report-session').textContent = data.session_id.substring(0, 8) + '...';
    document.getElementById('report-timestamp').textContent = new Date(data.timestamp).toLocaleString();
    document.getElementById('results-subtitle').textContent = 'Username Correlation Analysis Report';

    // Summary
    document.getElementById('exec-summary-text').textContent = data.analysis_summary || 'Username analysis complete.';

    // Risk gauge
    const corr = data.correlation_score || { score: 0, level: 'Low' };
    const color = getColorForLevel(corr.level);
    drawRiskGauge(corr.score, color);
    animateCounter('riskScore', corr.score);
    document.getElementById('riskLevel').textContent = corr.level;
    document.getElementById('riskLevel').style.background = color + '22';
    document.getElementById('riskLevel').style.color = color;
    document.getElementById('riskHeadline').textContent = 'Username Correlation Confidence';
    document.getElementById('riskDescription').textContent = corr.description || '';

    // Aggregated profile data  
    const agg = data.aggregated_profile;
    if (agg) {
        renderAggregatedProfileDirect(agg);
    } else {
        document.getElementById('aggregatedProfile').style.display = 'none';
    }

    // Metrics
    const patternAnalysis = data.pattern_analysis || {};
    renderMetrics({
        platforms_exposed: (data.platform_matches || []).length,
        total_data_points_exposed: patternAnalysis.patterns_detected?.length || 0,
        critical_platforms: (data.platform_matches || []).filter(m => m.confidence > 85).length,
        digital_footprint_score: corr.score,
    });

    // Platform matches
    const platforms = (data.platform_matches || []).map(m => ({
        platform: m.platform,
        icon: m.icon,
        color: m.color,
        image_similarity: null,
        username_confidence: m.confidence,
        username_exact: m.exact_match,
        combined_score: m.confidence,
        combined_risk: m.confidence > 85 ? 'Critical' : m.confidence > 70 ? 'High' : m.confidence > 50 ? 'Medium' : 'Low',
        data_points: m.gathered_data || {},
        profile_url: m.profile_url, // Pass profile URL
    }));
    renderPlatformGrid(platforms);

    // Hide attack/rec for username-only
    document.getElementById('corrDetailsCard').style.display = 'none';
    document.getElementById('attackCard').style.display = 'none';
    document.getElementById('recCard').style.display = 'none';

    showSection('results');
}

// ─── Component Renderers ───────────────────────────────────────

function renderMetrics(metrics) {
    const container = document.getElementById('metricsRow');
    container.innerHTML = '';

    const items = [
        { icon: '🌐', label: 'Platforms Found', value: metrics.platforms_exposed ?? '--', color: 'var(--accent-cyan)' },
        { icon: '🔴', label: 'Critical Risk', value: metrics.critical_platforms ?? '--', color: 'var(--accent-red)' },
        { icon: '📊', label: 'Data Points Exposed', value: metrics.total_data_points_exposed ?? '--', color: 'var(--accent-orange)' },
        { icon: '🔍', label: 'Footprint Score', value: metrics.digital_footprint_score ?? '--', color: 'var(--accent-purple)' },
    ];

    items.forEach(item => {
        const el = document.createElement('div');
        el.className = 'metric-card';
        el.innerHTML = `
            <div class="metric-icon">${item.icon}</div>
            <div class="metric-value" style="color:${item.color}">${item.value}</div>
            <div class="metric-label">${item.label}</div>
        `;
        container.appendChild(el);
    });
}

function renderAggregatedProfile(data) {
    const container = document.getElementById('aggregatedProfile');
    const grid = document.getElementById('aggGrid');

    // Try to find aggregated data from correlation or username analysis
    let aggData = null;
    if (data.correlation?.combined_platform_intelligence?.length > 0) {
        const platforms = data.correlation.combined_platform_intelligence;
        const total = platforms.length;
        const critical = platforms.filter(p => p.combined_risk === 'Critical').length;
        const high = platforms.filter(p => p.combined_risk === 'High').length;

        let dataPoints = 0;
        platforms.forEach(p => {
            const dp = p.data_points || {};
            dataPoints += Object.values(dp).filter(v => v && v !== 'Redacted (CEH-Safe)' && v !== null).length;
        });

        aggData = {
            total_platforms_found: total,
            critical_platforms: critical,
            high_risk_platforms: high,
            total_data_points: dataPoints,
        };
    }

    if (data.username_analysis?.aggregated_profile) {
        const uAgg = data.username_analysis.aggregated_profile;
        aggData = {
            total_platforms_found: uAgg.total_platforms_found || aggData?.total_platforms_found || 0,
            exact_matches: uAgg.exact_username_matches || 0,
            consistency: uAgg.cross_platform_consistency || 0,
            footprint: uAgg.digital_footprint_size || 'Unknown',
            activity: uAgg.overall_activity || 'Unknown',
            ...(aggData || {}),
        };
    }

    if (!aggData) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'block';
    grid.innerHTML = '';

    const stats = [
        { label: 'Platforms Found', value: aggData.total_platforms_found ?? '--', color: 'var(--accent-cyan)' },
        { label: 'Exact Matches', value: aggData.exact_matches ?? '--', color: 'var(--accent-blue)' },
        { label: 'Consistency', value: (aggData.consistency ?? '--') + '%', color: 'var(--accent-purple)' },
        { label: 'Footprint Size', value: aggData.footprint ?? '--', color: 'var(--accent-orange)' },
        { label: 'Activity Level', value: aggData.activity ?? '--', color: 'var(--accent-green)' },
        { label: 'Data Points', value: aggData.total_data_points ?? '--', color: 'var(--accent-red)' },
    ];

    stats.forEach(stat => {
        const el = document.createElement('div');
        el.className = 'agg-stat';
        el.innerHTML = `
            <div class="agg-stat-value" style="color:${stat.color}">${stat.value}</div>
            <div class="agg-stat-label">${stat.label}</div>
        `;
        grid.appendChild(el);
    });
}

function renderAggregatedProfileDirect(agg) {
    const container = document.getElementById('aggregatedProfile');
    const grid = document.getElementById('aggGrid');
    container.style.display = 'block';
    grid.innerHTML = '';

    const stats = [
        { label: 'Platforms Found', value: agg.total_platforms_found ?? '--', color: 'var(--accent-cyan)' },
        { label: 'Exact Matches', value: agg.exact_username_matches ?? '--', color: 'var(--accent-blue)' },
        { label: 'Consistency', value: (agg.cross_platform_consistency ?? '--') + '%', color: 'var(--accent-purple)' },
        { label: 'Footprint Size', value: agg.digital_footprint_size ?? '--', color: 'var(--accent-orange)' },
        { label: 'Activity Level', value: agg.overall_activity ?? '--', color: 'var(--accent-green)' },
        { label: 'Public Profiles', value: agg.public_profiles ?? '--', color: 'var(--accent-red)' },
    ];

    stats.forEach(stat => {
        const el = document.createElement('div');
        el.className = 'agg-stat';
        el.innerHTML = `
            <div class="agg-stat-value" style="color:${stat.color}">${stat.value}</div>
            <div class="agg-stat-label">${stat.label}</div>
        `;
        grid.appendChild(el);
    });
}

function renderPlatformGrid(platforms) {
    const container = document.getElementById('platformGrid');
    container.innerHTML = '';

    if (!platforms.length) {
        container.innerHTML = '<p style="color:var(--text-muted); text-align:center; padding:20px;">No platform data available.</p>';
        return;
    }

    platforms.forEach(platform => {
        const risk = (platform.combined_risk || 'Low').toLowerCase();
        const el = document.createElement('div');
        el.className = `platform-card risk-${risk}`;

        const dataPoints = platform.data_points || {};
        let dataHTML = '';

        // Display Name & Basic Info
        if (dataPoints.display_name) {
            dataHTML += `<div style="margin-bottom:8px; font-weight:600; color:var(--text-primary);">${dataPoints.display_name}</div>`;
        }

        // Bio Snippet
        if (dataPoints.bio_text) {
            dataHTML += `<div style="margin-bottom:8px; font-size:12px; color:var(--text-muted); font-style:italic;">"${dataPoints.bio_text}"</div>`;
        }

        const dataItems = [
            { key: 'bio_available', label: 'Bio Available' },
            { key: 'profile_image_available', label: 'Profile Photo' },
            { key: 'location_visible', label: 'Location' },
            { key: 'posts_public', label: 'Public Posts' },
            { key: 'connections_visible', label: 'Connections' },
            { key: 'verification_status', label: 'Verified Account' },
        ];

        dataItems.forEach(item => {
            if (item.key in dataPoints) {
                const val = dataPoints[item.key];
                if (val === null || val === undefined) return;
                const isTrue = val === true || (typeof val === 'string' && val.length > 0);

                // Don't show "Bio Available" if we already showed the text
                if (item.key === 'bio_available' && dataPoints.bio_text) return;

                dataHTML += `
                    <div class="platform-data-item">
                        <span class="${isTrue ? 'check' : 'cross'}">${isTrue ? '✓' : '✗'}</span>
                        ${item.label}
                    </div>
                `;
            }
        });

        // Add specific data values if available
        if (dataPoints.location) {
            dataHTML += `<div class="platform-data-item" style="color:var(--text-secondary);">📍 ${dataPoints.location}</div>`;
        }
        if (dataPoints.connections_count) {
            dataHTML += `<div class="platform-data-item" style="color:var(--text-secondary);">👥 ${dataPoints.connections_count} Connections</div>`;
        }
        if (dataPoints.joined_date) {
            dataHTML += `<div class="platform-data-item" style="color:var(--text-muted); font-size:11px;">🕒 Joined: ${dataPoints.joined_date}</div>`;
        }


        const imgScore = platform.image_similarity != null ? `Img: ${platform.image_similarity}%` : '';
        const usrScore = platform.username_confidence != null ? `Usr: ${platform.username_confidence}%` : '';
        const scoreLabels = [imgScore, usrScore].filter(Boolean).join(' · ');

        // Profile Link Button
        let profileAction = '';
        if (platform.profile_url) {
            profileAction = `
                <a href="${platform.profile_url}" target="_blank" class="platform-link-btn">
                    Visit Profile ↗
                </a>
            `;
        }

        el.innerHTML = `
            <div class="platform-header">
                <div class="platform-name">
                    <span class="platform-name-icon">${platform.icon || '🌐'}</span>
                    ${platform.platform}
                </div>
                <span class="platform-badge badge-${risk}">${platform.combined_risk || 'Unknown'}</span>
            </div>
            <div class="platform-data">${dataHTML}</div>
            
            ${profileAction}

            <div class="platform-score">
                <div style="font-size:12px; color:var(--text-muted); min-width:80px;">${scoreLabels}</div>
                <div class="score-bar">
                    <div class="score-bar-fill ${risk}" style="width:${platform.combined_score || 0}%"></div>
                </div>
                <div class="score-value" style="color:${getColorForLevel(platform.combined_risk)}">${platform.combined_score || 0}%</div>
            </div>
        `;

        container.appendChild(el);
    });
}

function renderCorrelationDetails(details) {
    const card = document.getElementById('corrDetailsCard');
    const container = document.getElementById('corrDetails');

    if (!details.length) {
        card.style.display = 'none';
        return;
    }

    card.style.display = 'block';
    container.innerHTML = '';

    details.forEach(detail => {
        const impact = (detail.impact || 'Medium').toLowerCase();
        const el = document.createElement('div');
        el.className = 'corr-item';
        el.innerHTML = `
            <span class="corr-impact badge-${impact === 'critical' ? 'critical' : impact}">${detail.impact}</span>
            <div class="corr-text">
                <div class="corr-factor">${detail.factor}</div>
                <div class="corr-desc">${detail.description}</div>
            </div>
        `;
        container.appendChild(el);
    });
}

function renderAttackVectors(attacks) {
    const card = document.getElementById('attackCard');
    const container = document.getElementById('attackVectors');

    if (!attacks.length) {
        card.style.display = 'none';
        return;
    }

    card.style.display = 'block';
    container.innerHTML = '';

    attacks.forEach(attack => {
        const risk = (attack.risk_level || 'Medium').toLowerCase();
        const el = document.createElement('div');
        el.className = 'attack-card';
        el.innerHTML = `
            <div class="attack-header">
                <span class="attack-icon">${attack.icon || '⚔️'}</span>
                <div>
                    <div class="attack-name">${attack.name}</div>
                    <span class="platform-badge badge-${risk}" style="font-size:10px;">${attack.risk_level}</span>
                </div>
            </div>
            <div class="attack-desc">${attack.description}</div>
            <div class="attack-feasibility">
                <span style="font-size:12px; color:var(--text-muted);">Feasibility</span>
                <div class="score-bar">
                    <div class="score-bar-fill ${risk}" style="width:${attack.feasibility_score}%"></div>
                </div>
                <span class="score-value" style="color:${getColorForLevel(attack.risk_level)}">${attack.feasibility_score}%</span>
            </div>
            <div class="attack-mitigation">${attack.mitigation || ''}</div>
        `;
        container.appendChild(el);
    });
}

function renderRecommendations(recs) {
    const card = document.getElementById('recCard');
    const container = document.getElementById('recommendations');

    if (!recs.length) {
        card.style.display = 'none';
        return;
    }

    card.style.display = 'block';
    container.innerHTML = '';

    recs.forEach(rec => {
        const priority = (rec.priority || 'Medium').toLowerCase();
        const el = document.createElement('div');
        el.className = 'rec-card';
        el.innerHTML = `
            <div class="rec-icon">${rec.icon || '🛡️'}</div>
            <div class="rec-content">
                <div class="rec-priority ${priority}">${rec.priority} PRIORITY</div>
                <div class="rec-category">${rec.category}</div>
                <div class="rec-text">${rec.recommendation}</div>
                ${rec.impact ? `<div class="rec-impact">Impact: ${rec.impact}</div>` : ''}
            </div>
        `;
        container.appendChild(el);
    });
}


function renderMetadata(meta) {
    const card = document.getElementById('metadataCard');
    const grid = document.getElementById('metadataGrid');

    if (!meta || Object.keys(meta).length === 0) {
        // [MODIFIED] Always show card, but state no data found
        card.style.display = 'block';
        grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:var(--text-muted); padding: 10px;">Scanned: No hidden EXIF data found in this image.</div>';
        return;
    }

    card.style.display = 'block';
    grid.innerHTML = '';

    // Flattens the object a bit for display
    const items = [];

    // Helper to add item
    const add = (label, val, icon, color) => {
        if (val && val !== 'Unknown' && val !== 'Not Found') {
            items.push({ label, val, icon, color });
        }
    };

    add('Camera Make', meta.camera_make, '📸', 'var(--accent-cyan)');
    add('Camera Model', meta.camera_model, '📷', 'var(--accent-blue)');
    add('Software', meta.software, '💾', 'var(--accent-purple)');
    add('Capture Date', meta.capture_date, '📅', 'var(--accent-orange)');
    add('GPS Status', meta.gps_status, '📍', 'var(--accent-red)');

    if (meta.dimensions) {
        add('Dimensions', `${meta.dimensions.width} x ${meta.dimensions.height} px`, '📐', 'var(--text-secondary)');
    }
    add('File Size', meta.file_size_kb + ' KB', '📁', 'var(--text-secondary)');
    add('Format', meta.format, '🖼️', 'var(--text-secondary)');

    if (items.length === 0) {
        grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:var(--text-muted);">No technical metadata found in this image.</div>';
        return;
    }

    items.forEach(item => {
        const el = document.createElement('div');
        el.className = 'agg-stat'; // Reuse existing style
        el.innerHTML = `
            <div class="agg-stat-value" style="color:${item.color}; font-size:16px;">${item.val}</div>
            <div class="agg-stat-label">${item.icon} ${item.label}</div>
        `;
        grid.appendChild(el);
    });
}

// ─── Risk Gauge Canvas ─────────────────────────────────────────
function drawRiskGauge(score, color) {
    const canvas = document.getElementById('riskGaugeCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const size = 220;
    const center = size / 2;
    const radius = 90;
    const lineWidth = 12;

    ctx.clearRect(0, 0, size, size);

    // Background arc
    ctx.beginPath();
    ctx.arc(center, center, radius, 0.75 * Math.PI, 2.25 * Math.PI);
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.1)';
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Score arc (animated)
    const scoreAngle = 0.75 * Math.PI + (score / 100) * 1.5 * Math.PI;
    const gradient = ctx.createLinearGradient(0, 0, size, size);
    gradient.addColorStop(0, color || '#00f0ff');
    gradient.addColorStop(1, adjustColor(color || '#00f0ff', 30));

    ctx.beginPath();
    ctx.arc(center, center, radius, 0.75 * Math.PI, scoreAngle);
    ctx.strokeStyle = gradient;
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Glow effect
    ctx.beginPath();
    ctx.arc(center, center, radius, 0.75 * Math.PI, scoreAngle);
    ctx.strokeStyle = (color || '#00f0ff') + '33';
    ctx.lineWidth = lineWidth + 8;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Tick marks
    for (let i = 0; i <= 10; i++) {
        const angle = 0.75 * Math.PI + (i / 10) * 1.5 * Math.PI;
        const innerR = radius - 20;
        const outerR = radius - 14;
        ctx.beginPath();
        ctx.moveTo(
            center + Math.cos(angle) * innerR,
            center + Math.sin(angle) * innerR
        );
        ctx.lineTo(
            center + Math.cos(angle) * outerR,
            center + Math.sin(angle) * outerR
        );
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
    }
}

// ─── Utility Functions ─────────────────────────────────────────
function getColorForLevel(level) {
    const l = (level || '').toLowerCase();
    if (l === 'critical') return '#FF1744';
    if (l === 'high') return '#FF9100';
    if (l === 'medium') return '#FFD600';
    return '#00E676';
}

function adjustColor(hex, amount) {
    let r = parseInt(hex.slice(1, 3), 16) || 0;
    let g = parseInt(hex.slice(3, 5), 16) || 0;
    let b = parseInt(hex.slice(5, 7), 16) || 0;
    r = Math.min(255, r + amount);
    g = Math.min(255, g + amount);
    b = Math.min(255, b + amount);
    return `rgb(${r},${g},${b})`;
}

function animateCounter(elementId, target) {
    const el = document.getElementById(elementId);
    if (!el) return;
    let current = 0;
    const step = Math.ceil(target / 40);
    const interval = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(interval);
        }
        el.textContent = current;
    }, 30);
}

// ─── Initialize ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    setupDropZones();
});
