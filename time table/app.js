const API_BASE = 'http://127.0.0.1:5000/api';

// --- State ---
let currentView = 'login';
let currentPage = 'dashboard';
let cache = {
    departments: [],
    subjects: [],
    faculty: [],
    rooms: []
};
let scheduleViewMode = 'grid';
let currentScheduleEntries = [];

// --- DOM Elements ---
const views = {
    login: document.getElementById('loginView'),
    app: document.getElementById('appView')
};

const pages = {
    dashboard: document.getElementById('dashboard'),
    create: document.getElementById('create'),
    schedule: document.getElementById('schedule'),
    faculty: document.getElementById('faculty'),
    manage: document.getElementById('manage'),
    autoschedule: document.getElementById('autoschedule')
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Check login state
    if(sessionStorage.getItem('tt_admin_logged')) {
        switchView('app');
        loadDashboardData();
        prefetchData();
    }
    
    // Setup Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navigateTo(item.dataset.target);
        });
    });

    // Login Form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);

    // Toggle Password Visibility
    const eyeOpenSVG = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
    const eyeClosedSVG = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;

    document.getElementById('togglePassword').addEventListener('click', function(e) {
        const passwordInput = document.getElementById('password');
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            this.innerHTML = eyeClosedSVG;
        } else {
            passwordInput.type = 'password';
            this.innerHTML = eyeOpenSVG;
        }
    });

    // Create Form
    document.getElementById('createTimetableForm').addEventListener('submit', handleCreateTimetable);
    document.getElementById('tt-dept').addEventListener('change', updateFilteredDropdowns);

    // Filter btn
    document.getElementById('applyFiltersBtn').addEventListener('click', loadSchedule);

    // Form Event Listeners
    document.getElementById('addFacultyForm').addEventListener('submit', handleAddFaculty);
    document.getElementById('addDeptForm').addEventListener('submit', handleAddDept);
    document.getElementById('addSubjectForm').addEventListener('submit', handleAddSubject);
    document.getElementById('addRoomForm').addEventListener('submit', handleAddRoom);

    // PDF Export
    document.getElementById('exportPdfBtn').addEventListener('click', exportToPdf);

    // Schedule View Toggles
    if (document.getElementById('viewGridBtn')) {
        document.getElementById('viewGridBtn').addEventListener('click', () => {
            scheduleViewMode = 'grid';
            document.getElementById('viewGridBtn').className = 'btn btn-secondary active';
            document.getElementById('viewTableBtn').className = 'btn btn-outline';
            document.getElementById('scheduleGrid').style.display = 'grid';
            document.getElementById('scheduleTableContainer').style.display = 'none';
        });
    }
    if (document.getElementById('viewTableBtn')) {
        document.getElementById('viewTableBtn').addEventListener('click', () => {
            scheduleViewMode = 'table';
            document.getElementById('viewTableBtn').className = 'btn btn-secondary active';
            document.getElementById('viewGridBtn').className = 'btn btn-outline';
            document.getElementById('scheduleGrid').style.display = 'none';
            document.getElementById('scheduleTableContainer').style.display = 'block';
            if (currentScheduleEntries.length > 0) {
                renderScheduleTable(currentScheduleEntries);
            }
        });
    }
    
    if (document.getElementById('filter-classes-dept')) {
        document.getElementById('filter-classes-dept').addEventListener('change', () => {
            if (typeof renderManageSubjectTable === 'function') {
                renderManageSubjectTable();
            }
        });
    }
    
    if (document.getElementById('auto-dept')) {
        document.getElementById('auto-dept').addEventListener('change', updateAutoFilteredDropdowns);
    }
    if (document.getElementById('autoAddReqBtn')) {
        document.getElementById('autoAddReqBtn').addEventListener('click', addAutoReqRow);
    }
    if (document.getElementById('autoScheduleForm')) {
        document.getElementById('autoScheduleForm').addEventListener('submit', handleAutoSchedule);
    }
});

// --- View/Page Management ---
function switchView(viewName) {
    Object.values(views).forEach(v => v.classList.remove('active'));
    views[viewName].classList.add('active');
    currentView = viewName;
}

window.navigateTo = function(pageId) {
    // Update sidebar active states
    document.querySelectorAll('.nav-item').forEach(nav => {
        if(nav.dataset.target === pageId) nav.classList.add('active');
        else nav.classList.remove('active');
    });
    // Switch the page
    switchPage(pageId);
}

function switchPage(pageName) {
    Object.values(pages).forEach(p => p.classList.remove('active'));
    pages[pageName].classList.add('active');
    currentPage = pageName;

    // Load data based on page
    if(pageName === 'dashboard') loadDashboardData();
    if(pageName === 'create' || pageName === 'autoschedule') prefetchData();
    if(pageName === 'faculty') loadFacultyList();
    if(pageName === 'schedule') loadSchedule();
    if(pageName === 'manage') loadManageData();
    
    // Auto Schedule specific init
    if(pageName === 'autoschedule') {
        const reqContainer = document.getElementById('autoRequirementsContainer');
        if (reqContainer && reqContainer.children.length === 0) {
            // Wait for prefetch
            setTimeout(() => {
                if (typeof updateAutoFilteredDropdowns === 'function') {
                    updateAutoFilteredDropdowns();
                } else {
                    addAutoReqRow();
                }
            }, 500);
        }
    }
}

// --- Auth ---
async function handleLogin(e) {
    e.preventDefault();
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    const err = document.getElementById('loginError');
    
    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p})
        });
        const data = await res.json();
        if(res.ok && data.success) {
            err.textContent = '';
            sessionStorage.setItem('tt_admin_logged', 'true');
            switchView('app');
            loadDashboardData();
            prefetchData();
        } else {
            err.textContent = data.message || 'Login failed';
        }
    } catch (e) {
        err.textContent = 'Server connection error';
    }
}

function handleLogout() {
    sessionStorage.removeItem('tt_admin_logged');
    switchView('login');
}

// --- Data Fetching ---
async function loadDashboardData() {
    try {
        const res = await fetch(`${API_BASE}/dashboard`);
        const data = await res.json();
        document.getElementById('statClasses').textContent = data.classes || 0;
        document.getElementById('statFaculty').textContent = data.faculty || 0;
        document.getElementById('statRooms').textContent = data.rooms || 0;
    } catch(e) { console.error(e); }
}

async function prefetchData() {
    try {
        const [deptRes, subRes, facRes, roomRes] = await Promise.all([
            fetch(`${API_BASE}/departments`),
            fetch(`${API_BASE}/subjects`),
            fetch(`${API_BASE}/faculty`),
            fetch(`${API_BASE}/rooms`)
        ]);
        cache.departments = await deptRes.json();
        cache.subjects = await subRes.json();
        cache.faculty = await facRes.json();
        cache.rooms = await roomRes.json();
        
        populateAllDropdowns();
    } catch(e) { console.error(e); }
}

function populateAllDropdowns() {
    // Populate Department dropdowns
    const deptOptions = cache.departments.map(d => `<option value="${d.name}">${d.name}</option>`).join('');
    
    document.getElementById('tt-dept').innerHTML = deptOptions;
    document.getElementById('fac-dept').innerHTML = deptOptions;
    document.getElementById('sub-dept').innerHTML = deptOptions;
    document.getElementById('filter-dept').innerHTML = `<option value="">All</option>` + deptOptions;

    document.getElementById('tt-room').innerHTML = cache.rooms.map(r => `<option value="${r.id}">${r.room_number}</option>`).join('');
    
    if (document.getElementById('filter-classes-dept')) {
        document.getElementById('filter-classes-dept').innerHTML = `<option value="">All Departments</option>` + deptOptions;
    }
    
    if (document.getElementById('auto-dept')) {
        document.getElementById('auto-dept').innerHTML = deptOptions;
        if (typeof updateAutoFilteredDropdowns === 'function') {
            updateAutoFilteredDropdowns();
        }
    }
    
    updateFilteredDropdowns();
}

function updateFilteredDropdowns() {
    const selectedDept = document.getElementById('tt-dept').value;
    if (!selectedDept) {
        document.getElementById('tt-subject').innerHTML = '';
        document.getElementById('tt-faculty').innerHTML = '';
        return;
    }
    
    const filteredSubjects = cache.subjects.filter(s => s.department === selectedDept);
    const filteredFaculty = cache.faculty.filter(f => f.department === selectedDept);
    
    let subHtml = filteredSubjects.map(s => `<option value="${s.id}">${s.name} (${s.code})</option>`).join('');
    if (!subHtml) subHtml = `<option value="">No Subjects</option>`;
    
    let facHtml = filteredFaculty.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
    if (!facHtml) facHtml = `<option value="">No Faculty</option>`;
    
    document.getElementById('tt-subject').innerHTML = subHtml;
    document.getElementById('tt-faculty').innerHTML = facHtml;
}

// --- Timetable Logic ---
async function handleCreateTimetable(e) {
    e.preventDefault();
    const payload = {
        department: document.getElementById('tt-dept').value,
        semester: document.getElementById('tt-semester').value,
        section: document.getElementById('tt-section').value,
        subject_id: parseInt(document.getElementById('tt-subject').value) || null,
        faculty_id: parseInt(document.getElementById('tt-faculty').value) || null,
        room_id: parseInt(document.getElementById('tt-room').value),
        day_of_week: document.getElementById('tt-day').value,
        time_slot: document.getElementById('tt-time').value,
    };
    
    const msgBox = document.getElementById('tt-message');
    
    if (!payload.subject_id || !payload.faculty_id) {
        msgBox.className = 'message-box error';
        msgBox.textContent = 'Please ensure a Subject and Faculty are selected.';
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/timetables`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if(!res.ok) {
            msgBox.className = 'message-box error';
            msgBox.textContent = data.message || 'Error occurred';
        } else {
            msgBox.className = 'message-box success';
            msgBox.textContent = 'Timetable entry added successfully!';
            loadDashboardData(); // Refresh bg stats
            setTimeout(() => { msgBox.className = 'message-box'; }, 3000);
        }
    } catch(e) {
        msgBox.className = 'message-box error';
        msgBox.textContent = 'Server connection error';
    }
}

// --- Schedule View ---
const TIME_SLOTS = [
    "09:00 - 09:50",
    "09:50 - 10:40",
    "10:40 - 11:00 (Break)",
    "11:00 - 11:50",
    "11:50 - 12:40",
    "12:40 - 01:20 (Lunch)",
    "01:20 - 02:10",
    "02:10 - 03:00",
    "03:00 - 03:20 (Break)",
    "03:20 - 04:10"
];
const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

async function loadSchedule() {
    const dept = document.getElementById('filter-dept').value;
    const sec = document.getElementById('filter-sec').value;
    
    let url = `${API_BASE}/timetables?`;
    if(dept) url += `department=${encodeURIComponent(dept)}&`;
    if(sec) url += `section=${encodeURIComponent(sec)}`;
    
    try {
        const res = await fetch(url);
        const entries = await res.json();
        currentScheduleEntries = entries;
        if (scheduleViewMode === 'grid') {
            renderScheduleGrid(entries);
        } else {
            renderScheduleTable(entries);
        }
    } catch(e) { console.error(e); }
}

function renderScheduleGrid(entries) {
    const grid = document.getElementById('scheduleGrid');
    grid.innerHTML = '';
    grid.classList.add('flipped');
    
    // Header Row (Time Slots)
    grid.innerHTML += `<div class="grid-header" style="font-size:0.85rem">Day / Time</div>`;
    TIME_SLOTS.forEach(time => {
        grid.innerHTML += `<div class="grid-header" style="font-size:0.85rem">${time}</div>`;
    });
    
    // Rows (Days)
    DAYS.forEach(day => {
        grid.innerHTML += `<div class="grid-time block">${day}</div>`;
        
        TIME_SLOTS.forEach(time => {
            const isBreak = time.includes("Break") || time.includes("Lunch");
            
            if (isBreak) {
                grid.innerHTML += `<div class="grid-cell" style="background: rgba(255, 255, 255, 0.02); min-height: 80px;"></div>`;
                return;
            }
            
            const cellEntries = entries.filter(e => e.time_slot === time && e.day_of_week === day);
            
            let cellContent = '';
            cellEntries.forEach(entry => {
                cellContent += `
                    <div class="tt-item">
                        <strong>${entry.subject_name}</strong>
                        <span>${entry.faculty_name}</span>
                        <span>Room: ${entry.room_number} | Sec: ${entry.section}</span>
                        <button class="delete-tt" onclick="deleteEntry(${entry.id})" title="Remove class">×</button>
                    </div>
                `;
            });
            
            grid.innerHTML += `<div class="grid-cell">${cellContent}</div>`;
        });
    });
}

function renderScheduleTable(entries) {
    const tbody = document.querySelector('#scheduleTable tbody');
    tbody.innerHTML = '';
    
    if (entries.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;">No scheduled classes found.</td></tr>`;
        return;
    }

    // Sort entries by Day then Time
    const sortedEntries = [...entries].sort((a, b) => {
        const dayDiff = DAYS.indexOf(a.day_of_week) - DAYS.indexOf(b.day_of_week);
        if (dayDiff !== 0) return dayDiff;
        return TIME_SLOTS.indexOf(a.time_slot) - TIME_SLOTS.indexOf(b.time_slot);
    });

    sortedEntries.forEach(entry => {
        tbody.innerHTML += `
            <tr>
                <td>${entry.day_of_week}</td>
                <td>${entry.time_slot}</td>
                <td><strong>${entry.subject_name}</strong></td>
                <td>${entry.faculty_name}</td>
                <td>${entry.room_number}</td>
                <td>${entry.section}</td>
                <td>
                    <button class="btn btn-outline" style="padding:4px 8px; font-size:12px;" onclick="deleteEntry(${entry.id})" title="Remove class">Remove</button>
                </td>
            </tr>
        `;
    });
}

window.deleteEntry = async function(id) {
    if(!confirm("Are you sure you want to remove this scheduled class?")) return;
    try {
        await fetch(`${API_BASE}/timetables/${id}`, { method: 'DELETE' });
        loadSchedule();
        loadDashboardData();
    } catch(e) { console.error(e); }
}

// --- Faculty Management ---
async function loadFacultyList() {
    try {
        const res = await fetch(`${API_BASE}/faculty`);
        const data = await res.json();
        const tbody = document.querySelector('#facultyTable tbody');
        tbody.innerHTML = data.map(f => `
            <tr>
                <td>${f.name}</td>
                <td>${f.department}</td>
                <td><strong>${f.workload}</strong> hrs/week</td>
                <td><button class="btn btn-outline" style="padding:4px 8px; font-size:12px;" onclick="deleteFaculty(${f.id})">Remove</button></td>
            </tr>
        `).join('');
    } catch(e) { console.error(e); }
}

async function handleAddFaculty(e) {
    e.preventDefault();
    const name = document.getElementById('fac-name').value;
    const dept = document.getElementById('fac-dept').value;
    
    try {
        await fetch(`${API_BASE}/faculty`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, department: dept})
        });
        document.getElementById('addFacultyForm').reset();
        loadFacultyList();
    } catch(e) { console.error(e); }
}

// --- Export to PDF ---
function exportToPdf() {
    const element = document.getElementById('schedule-export-wrapper');
    
    // Temporarily apply high-contrast print mode 
    element.classList.add('pdf-export-mode');

    const opt = {
        margin:       10,
        filename:     'Timetable_Schedule.pdf',
        image:        { type: 'jpeg', quality: 1.0 },
        html2canvas:  { scale: 3, useCORS: true },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'landscape' }
    };
    
    html2pdf().set(opt).from(element).save().then(() => {
        // Remove high-contrast print mode after generation completes
        element.classList.remove('pdf-export-mode');
    });
}

// --- Manage Subjects & Rooms & Depts ---
async function loadManageData() {
    try {
        const [deptRes, subRes, roomRes] = await Promise.all([
            fetch(`${API_BASE}/departments`),
            fetch(`${API_BASE}/subjects`),
            fetch(`${API_BASE}/rooms`)
        ]);
        const departments = await deptRes.json();
        const subjects = await subRes.json();
        const rooms = await roomRes.json();
        
        const dBody = document.querySelector('#deptTable tbody');
        dBody.innerHTML = departments.map(d => `
            <tr>
                <td>${d.name}</td>
                <td><button class="btn btn-outline" style="padding:4px 8px; font-size:12px;" onclick="deleteDept(${d.id})">Remove</button></td>
            </tr>
        `).join('');

        renderManageSubjectTable();

        const rBody = document.querySelector('#roomTable tbody');
        rBody.innerHTML = rooms.map(r => `
            <tr>
                <td>${r.room_number}</td>
                <td>${r.capacity}</td>
                <td><button class="btn btn-outline" style="padding:4px 8px; font-size:12px;" onclick="deleteRoom(${r.id})">Remove</button></td>
            </tr>
        `).join('');
        
        // Update cache
        cache.departments = departments;
        cache.subjects = subjects;
        cache.rooms = rooms;
        populateAllDropdowns();
        
    } catch(e) { console.error(e); }
}

function renderManageSubjectTable() {
    const sBody = document.querySelector('#subjectTable tbody');
    if(!sBody) return;
    
    const filterEl = document.getElementById('filter-classes-dept');
    const filterDept = filterEl ? filterEl.value : '';
    
    let filteredSubjects = cache.subjects || [];
    if (filterDept) {
        filteredSubjects = filteredSubjects.filter(s => s.department === filterDept);
    }
    
    sBody.innerHTML = filteredSubjects.map(s => `
        <tr>
            <td>${s.name}</td>
            <td>${s.code}</td>
            <td><button class="btn btn-outline" style="padding:4px 8px; font-size:12px;" onclick="deleteSubject(${s.id})">Remove</button></td>
        </tr>
    `).join('');
}

async function handleAddDept(e) {
    e.preventDefault();
    const name = document.getElementById('dept-name').value;
    
    try {
        await fetch(`${API_BASE}/departments`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name})
        });
        document.getElementById('addDeptForm').reset();
        loadManageData();
    } catch(e) { console.error(e); }
}

async function handleAddSubject(e) {
    e.preventDefault();
    const name = document.getElementById('sub-name').value;
    const code = document.getElementById('sub-code').value;
    const dept = document.getElementById('sub-dept').value;
    
    try {
        await fetch(`${API_BASE}/subjects`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, code, department: dept})
        });
        document.getElementById('addSubjectForm').reset();
        document.getElementById('sub-dept').value = "Computer Science";
        loadManageData();
    } catch(e) { console.error(e); }
}

async function handleAddRoom(e) {
    e.preventDefault();
    const num = document.getElementById('room-num').value;
    const cap = parseInt(document.getElementById('room-cap').value) || 40;
    
    try {
        await fetch(`${API_BASE}/rooms`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({room_number: num, capacity: cap})
        });
        document.getElementById('addRoomForm').reset();
        document.getElementById('room-cap').value = "40";
        loadManageData();
    } catch(e) { console.error(e); }
}

window.deleteSubject = async function(id) {
    if(!confirm("Remove this subject? Note: It might be assigned to timetables.")) return;
    try {
        await fetch(`${API_BASE}/subjects/${id}`, { method: 'DELETE' });
        loadManageData();
    } catch(e) { console.error(e); }
}

window.deleteRoom = async function(id) {
    if(!confirm("Remove this room? Note: It might be assigned to timetables.")) return;
    try {
        await fetch(`${API_BASE}/rooms/${id}`, { method: 'DELETE' });
        loadManageData();
    } catch(e) { console.error(e); }
}

window.deleteDept = async function(id) {
    if(!confirm("Remove this department? Note: It might be assigned to timetables or faculty.")) return;
    try {
        await fetch(`${API_BASE}/departments/${id}`, { method: 'DELETE' });
        loadManageData();
    } catch(e) { console.error(e); }
}

window.deleteFaculty = async function(id) {
    if(!confirm("Remove this faculty member? Note: They might be assigned to active timetables.")) return;
    try {
        await fetch(`${API_BASE}/faculty/${id}`, { method: 'DELETE' });
        loadFacultyList();
        loadDashboardData(); // Update dashboard counts
    } catch(e) { console.error(e); }
}

// --- Auto Schedule Logic ---
window.updateAutoFilteredDropdowns = function() {
    const selectedDept = document.getElementById('auto-dept').value;
    if (!selectedDept) return;
    
    const container = document.getElementById('autoRequirementsContainer');
    if (!container) return;
    container.innerHTML = '';
    
    const filteredSubjects = cache.subjects.filter(s => s.department === selectedDept);
    
    if (filteredSubjects.length === 0) {
        addAutoReqRow();
        return;
    }
    
    filteredSubjects.forEach(subject => {
        const row = document.createElement('div');
        row.className = 'auto-req-row grid-3';
        row.style.cssText = 'display: grid; grid-template-columns: 2fr 2fr 1fr auto; gap: 10px; align-items: center; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px;';
        
        row.innerHTML = `
            <select class="form-control auto-sub" required></select>
            <select class="form-control auto-fac" required></select>
            <input type="number" class="form-control auto-count" required min="1" max="10" placeholder="Lectures/week" value="${subject.name.includes('Lab') ? 2 : 3}">
            <button type="button" class="btn btn-outline" style="padding: 6px 12px; color: #f87171; border-color: #f87171;" onclick="this.parentElement.remove()">X</button>
        `;
        
        container.appendChild(row);
        populateAutoRowDropdowns(row, selectedDept);
        
        const subSelect = row.querySelector('.auto-sub');
        if(subSelect) subSelect.value = subject.id;
    });
}

function populateAutoRowDropdowns(row, dept) {
    const subSelect = row.querySelector('.auto-sub');
    const facSelect = row.querySelector('.auto-fac');
    
    const filteredSubjects = cache.subjects.filter(s => s.department === dept);
    const filteredFaculty = cache.faculty.filter(f => f.department === dept);
    
    let subHtml = filteredSubjects.map(s => `<option value="${s.id}">${s.name} (${s.code})</option>`).join('');
    let facHtml = filteredFaculty.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
    
    const curSub = subSelect.value;
    const curFac = facSelect.value;
    
    subSelect.innerHTML = subHtml || '<option value="">No Subjects</option>';
    facSelect.innerHTML = facHtml || '<option value="">No Faculty</option>';
    
    if(curSub) subSelect.value = curSub;
    if(curFac) facSelect.value = curFac;
}

window.addAutoReqRow = function() {
    const container = document.getElementById('autoRequirementsContainer');
    const row = document.createElement('div');
    row.className = 'auto-req-row grid-3';
    row.style.cssText = 'display: grid; grid-template-columns: 2fr 2fr 1fr auto; gap: 10px; align-items: center; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px;';
    
    row.innerHTML = `
        <select class="form-control auto-sub" required></select>
        <select class="form-control auto-fac" required></select>
        <input type="number" class="form-control auto-count" required min="1" max="10" placeholder="Lectures/week" value="3">
        <button type="button" class="btn btn-outline" style="padding: 6px 12px; color: #f87171; border-color: #f87171;" onclick="this.parentElement.remove()">X</button>
    `;
    
    container.appendChild(row);
    const dept = document.getElementById('auto-dept').value;
    populateAutoRowDropdowns(row, dept);
}

window.handleAutoSchedule = async function(e) {
    e.preventDefault();
    const rows = document.querySelectorAll('.auto-req-row');
    const requirements = Array.from(rows).map(row => ({
        subject_id: parseInt(row.querySelector('.auto-sub').value),
        faculty_id: parseInt(row.querySelector('.auto-fac').value),
        count: parseInt(row.querySelector('.auto-count').value)
    }));
    
    if (requirements.length === 0) {
        alert("Please add at least one subject requirement.");
        return;
    }
    
    const payload = {
        department: document.getElementById('auto-dept').value,
        semester: document.getElementById('auto-sem').value,
        section: document.getElementById('auto-sec').value,
        requirements: requirements
    };
    
    const msgBox = document.getElementById('auto-message');
    msgBox.className = 'message-box';
    msgBox.textContent = 'Generating schedule, please wait...';
    
    try {
        const res = await fetch(`${API_BASE}/auto_schedule`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (!res.ok) {
            msgBox.className = 'message-box error';
            msgBox.textContent = data.message || 'Scheduling failed due to conflicts.';
        } else {
            msgBox.className = 'message-box success';
            msgBox.textContent = 'Timetable generated successfully!';
            setTimeout(() => {
                msgBox.className = 'message-box';
                navigateTo('schedule');
            }, 1500);
        }
    } catch(err) {
        console.error(err);
        msgBox.className = 'message-box error';
        msgBox.textContent = 'Server connection error';
    }
}
