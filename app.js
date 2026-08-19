// LUXE WEDDING STUDIO - QUẢN LÝ STUDIO ẢNH CƯỚI (ĐỀ TÀI SỐ 8 - NHÓM 24)
// MSSV: 2212407 - Hoàng Long

const MAX_RENTAL_ITEMS = 3; // Ràng buộc N = 3 bộ

// Dữ liệu mẫu (Database Mock)
let state = {
  serviceTypes: [
    { id: 'LDV01', name: 'Chụp Ảnh Cưới Album', desc: 'Chụp ngoại cảnh, phim trường, studio chuyên nghiệp' },
    { id: 'LDV02', name: 'Quay Phim Phóng Sự Cưới', desc: 'Ghi lại khoảnh khắc ngày cưới với chất lượng 4K Cinematic' },
    { id: 'LDV03', name: 'Trang Điểm & Làm Tóc Cô Dâu', desc: 'Make-up ngày cưới, lễ gia tiên, phong cách Hàn Quốc/Tây' },
    { id: 'LDV04', name: 'Thuê Trang Phục Cưới', desc: 'Váy cưới luxury, áo dài cô dâu, vest chú rể' },
    { id: 'LDV05', name: 'Trang Trí Gia Tiên & Tiệc Cưới', desc: 'Set up hoa tươi, background lễ cưới trọn gói' }
  ],

  services: [
    { id: 'DV01', typeId: 'LDV01', name: 'Gói Chụp Album Studio Classic', price: 6500000, note: 'Bao gồm 1 album 30 trang, 2 ảnh cổng 60x90' },
    { id: 'DV02', typeId: 'LDV01', name: 'Gói Chụp Ngoại Cảnh Đà Lạt / Nha Trang', price: 14500000, note: 'Trọn gói ekip 2 ngày, bao xe di chuyển' },
    { id: 'DV03', typeId: 'LDV02', name: 'Quay Phim Phóng Sự Cưới Highlight', price: 8000000, note: 'Clip highlight 5-7 phút 4K + MV ca nhạc' },
    { id: 'DV04', typeId: 'LDV03', name: 'Trang Điểm Cô Dâu Ngày Cưới (2 Lần)', price: 3500000, note: 'Tại nhà cô dâu, dặm phấn suốt tiệc' },
    { id: 'DV05', typeId: 'LDV04', name: 'Gói Thuê 1 Váy Luxury + 1 Vest Chú Rể', price: 5000000, note: 'Thời hạn thuê 3 ngày 2 đêm' },
    { id: 'DV06', typeId: 'LDV05', name: 'Gói Trang Trí Gia Tiên Hoa Tươi Cao Cấp', price: 12000000, note: 'Bàn thờ gia tiên, bàn hai họ 12 ghế, cổng hoa' }
  ],

  costumes: [
    { id: 'AC01', title: 'Váy Cưới Luxury Hoàng Gia Đính Pha Lê Swarovski', category: 'Váy Cưới Luxury', rentPrice: 3500000, depositPrice: 5000000, status: 'DANG_THUE', img: 'https://images.unsplash.com/photo-1594552072238-b8a33785b261?w=300&auto=format&fit=crop&q=80' },
    { id: 'AC02', title: 'Váy Cưới Đuôi Cá Satin Phong Cách Pháp', category: 'Váy Cưới Luxury', rentPrice: 2800000, depositPrice: 4000000, status: 'SAN_SANG', img: 'https://images.unsplash.com/photo-1532712938310-34cb3982ef74?w=300&auto=format&fit=crop&q=80' },
    { id: 'AC03', title: 'Áo Dài Cưới Gấm Đỏ Thêu Phượng Hoàng', category: 'Áo Dài Cưới Truyền Thống', rentPrice: 1200000, depositPrice: 2000000, status: 'DANG_THUE', img: 'https://images.unsplash.com/photo-1546804784-896d0dca3805?w=300&auto=format&fit=crop&q=80' },
    { id: 'AC04', title: 'Áo Dài Cặp Đôi Tơ Tằm Trắng Tinh Khôi', category: 'Áo Dài Cưới Truyền Thống', rentPrice: 1800000, depositPrice: 2500000, status: 'SAN_SANG', img: 'https://images.unsplash.com/photo-1519741497674-611481863552?w=300&auto=format&fit=crop&q=80' },
    { id: 'AC05', title: 'Bộ Vest Chú Rể Tuxedo Đen Ý Sang Trọng', category: 'Vest Chú Rể Cao Cấp', rentPrice: 1500000, depositPrice: 2000000, status: 'DANG_THUE', img: 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=300&auto=format&fit=crop&q=80' },
    { id: 'AC06', title: 'Bộ Vest Chú Rể Xanh Navy Form Slimfit', category: 'Vest Chú Rể Cao Cấp', rentPrice: 1200000, depositPrice: 1800000, status: 'SAN_SANG', img: 'https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?w=300&auto=format&fit=crop&q=80' },
    { id: 'AC07', title: 'Váy Cưới Chữ A Voan Mềm Bồng Bềnh Hàn Quốc', category: 'Váy Cưới Minimalist', rentPrice: 2000000, depositPrice: 3000000, status: 'SAN_SANG', img: 'https://images.unsplash.com/photo-1596451190630-186aff535bf2?w=300&auto=format&fit=crop&q=80' },
    { id: 'AC08', title: 'Váy Cưới Xòe Cúp Ngực Đính Ngọc Trai', category: 'Váy Cưới Luxury', rentPrice: 4000000, depositPrice: 6000000, status: 'DANG_THUE', img: 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=300&auto=format&fit=crop&q=80' }
  ],

  customers: [
    { id: 'KH01', name: 'Nguyễn Thị Lan Anh', phone: '0912345678', address: 'Phường 2, TP. Đà Lạt', usedServices: ['DV01', 'DV04'] },
    { id: 'KH02', name: 'Trần Văn Hùng', phone: '0987654321', address: 'Phường 8, TP. Đà Lạt', usedServices: ['DV02', 'DV03', 'DV05'] },
    { id: 'KH03', name: 'Phạm Quỳnh Nga', phone: '0905123987', address: 'Phường 1, TP. Đà Lạt', usedServices: ['DV01'] },
    { id: 'KH04', name: 'Lê Hoàng Nam', phone: '0934567890', address: 'Phường 9, TP. Đà Lạt', usedServices: ['DV02', 'DV06'] }
  ],

  rentals: [
    {
      id: 'PT01',
      customerId: 'KH01',
      startDate: '2026-08-16',
      dueDate: '2026-08-18', // Quá hạn 1 ngày so với ngày hiện tại (2026-08-19)
      costumeIds: ['AC01', 'AC05'],
      totalRental: 5000000,
      depositAmount: 7000000,
      status: 'QUA_HAN',
      returnDate: null
    },
    {
      id: 'PT02',
      customerId: 'KH02',
      startDate: '2026-08-14',
      dueDate: '2026-08-17', // Quá hạn 2 ngày
      costumeIds: ['AC03'],
      totalRental: 1200000,
      depositAmount: 2000000,
      status: 'QUA_HAN',
      returnDate: null
    },
    {
      id: 'PT03',
      customerId: 'KH03',
      startDate: '2026-08-18',
      dueDate: '2026-08-21', // Còn trong hạn
      costumeIds: ['AC08'],
      totalRental: 4000000,
      depositAmount: 6000000,
      status: 'DANG_THUE',
      returnDate: null
    },
    {
      id: 'PT04',
      customerId: 'KH04',
      startDate: '2026-08-10',
      dueDate: '2026-08-13',
      costumeIds: ['AC02', 'AC06'],
      totalRental: 4000000,
      depositAmount: 5800000,
      status: 'DA_TRA',
      returnDate: '2026-08-13'
    }
  ]
};

// Format tiền tệ
function formatVND(amount) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

// Khởi chạy ứng dụng
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('currentDate').innerText = new Date().toLocaleDateString('vi-VN', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });

  renderAll();
});

function renderAll() {
  renderKPIs();
  renderDashboardOverdue();
  renderCategoryDistribution();
  renderServiceTypes();
  renderServices();
  renderCostumes();
  renderRentals();
  renderUnreturnedReport();
  renderOverdueReport();
}

// Switch tabs
function switchTab(tabId) {
  document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

  const targetLink = document.querySelector(`.nav-item[href="#${tabId}"]`);
  if (targetLink) targetLink.classList.add('active');

  const targetPane = document.getElementById(`tab-${tabId}`);
  if (targetPane) targetPane.classList.add('active');
}

// 1. KPI & DASHBOARD
function renderKPIs() {
  const totalServices = state.services.length;
  const totalCostumes = state.costumes.length;
  const availableCostumes = state.costumes.filter(c => c.status === 'SAN_SANG').length;
  
  const unreturned = state.rentals.filter(r => r.status === 'DANG_THUE' || r.status === 'QUA_HAN');
  const overdue = state.rentals.filter(r => r.status === 'QUA_HAN');

  document.getElementById('kpi-total-services').innerText = totalServices;
  document.getElementById('kpi-total-costumes').innerText = totalCostumes;
  document.getElementById('kpi-unreturned').innerText = unreturned.length;
  document.getElementById('kpi-overdue').innerText = overdue.length;

  document.getElementById('badge-rentals').innerText = state.rentals.length;
}

function renderDashboardOverdue() {
  const tbody = document.getElementById('dashboard-overdue-tbody');
  const overdueList = state.rentals.filter(r => r.status === 'QUA_HAN');

  if (overdueList.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Không có phiếu thuê nào quá hạn.</td></tr>`;
    return;
  }

  tbody.innerHTML = overdueList.map(r => {
    const cust = state.customers.find(c => c.id === r.customerId);
    const daysLate = getDaysDifference(r.dueDate, '2026-08-19');
    return `
      <tr>
        <td><strong>${r.id}</strong></td>
        <td>
          <strong>${cust ? cust.name : 'Khách lạ'}</strong><br>
          <small class="text-muted">${cust ? cust.phone : ''}</small>
        </td>
        <td><span class="badge">${r.costumeIds.length} bộ</span></td>
        <td>${formatDate(r.dueDate)}</td>
        <td><strong class="text-danger">Trễ ${daysLate} ngày</strong></td>
        <td class="text-right text-primary font-weight-bold">${formatVND(r.depositAmount)}</td>
        <td>
          <button class="btn btn-sm btn-outline-danger" onclick="handleReturnRental('${r.id}')"><i class="fa-solid fa-rotate-left"></i> Nhận trả</button>
        </td>
      </tr>
    `;
  }).join('');
}

function renderCategoryDistribution() {
  const container = document.getElementById('category-distribution-list');
  const total = state.services.length || 1;

  container.innerHTML = state.serviceTypes.map(type => {
    const count = state.services.filter(s => s.typeId === type.id).length;
    const percent = Math.round((count / total) * 100);
    return `
      <div class="cat-item">
        <div class="cat-info">
          <span><strong>${type.name}</strong> (${type.id})</span>
          <span><strong>${count}</strong> dịch vụ (${percent}%)</span>
        </div>
        <div class="cat-bar">
          <div class="cat-fill" style="width: ${percent}%;"></div>
        </div>
      </div>
    `;
  }).join('');
}

// 2. F1 - QUẢN LÝ LOẠI DỊCH VỤ
function renderServiceTypes() {
  const tbody = document.getElementById('types-table-body');
  document.getElementById('count-types').innerText = state.serviceTypes.length;

  tbody.innerHTML = state.serviceTypes.map(t => {
    const count = state.services.filter(s => s.typeId === t.id).length;
    return `
      <tr>
        <td><strong>${t.id}</strong></td>
        <td><strong>${t.name}</strong></td>
        <td class="text-muted">${t.desc || 'Chưa có mô tả'}</td>
        <td class="text-center"><span class="badge" style="background:#6366f1">${count}</span></td>
        <td class="text-center">
          <button class="btn btn-sm btn-outline" onclick="editType('${t.id}')"><i class="fa-solid fa-pen"></i></button>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteType('${t.id}')"><i class="fa-solid fa-trash"></i></button>
        </td>
      </tr>
    `;
  }).join('');

  // Update dropdown filter & form selects
  const filterSelect = document.getElementById('service-type-filter');
  const formSelect = document.getElementById('service-type-id-select');
  
  if (filterSelect) {
    const currentVal = filterSelect.value;
    filterSelect.innerHTML = `<option value="ALL">-- Tất cả loại dịch vụ --</option>` + 
      state.serviceTypes.map(t => `<option value="${t.id}">${t.name} (${t.id})</option>`).join('');
    filterSelect.value = currentVal || 'ALL';
  }

  if (formSelect) {
    formSelect.innerHTML = state.serviceTypes.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
  }
}

function openAddTypeModal() {
  document.getElementById('type-edit-id').value = '';
  document.getElementById('type-id').value = 'LDV0' + (state.serviceTypes.length + 1);
  document.getElementById('type-id').readOnly = false;
  document.getElementById('type-name').value = '';
  document.getElementById('type-desc').value = '';
  document.getElementById('type-modal-title').innerHTML = `<i class="fa-solid fa-layer-group text-primary"></i> Thêm Loại Dịch Vụ Mới`;
  openModal('typeModal');
}

function editType(id) {
  const t = state.serviceTypes.find(x => x.id === id);
  if (!t) return;
  document.getElementById('type-edit-id').value = t.id;
  document.getElementById('type-id').value = t.id;
  document.getElementById('type-id').readOnly = true;
  document.getElementById('type-name').value = t.name;
  document.getElementById('type-desc').value = t.desc;
  document.getElementById('type-modal-title').innerHTML = `<i class="fa-solid fa-pen text-primary"></i> Cập Nhật Loại Dịch Vụ`;
  openModal('typeModal');
}

function handleSaveType(e) {
  e.preventDefault();
  const editId = document.getElementById('type-edit-id').value;
  const id = document.getElementById('type-id').value.trim();
  const name = document.getElementById('type-name').value.trim();
  const desc = document.getElementById('type-desc').value.trim();

  if (editId) {
    const index = state.serviceTypes.findIndex(x => x.id === editId);
    if (index !== -1) {
      state.serviceTypes[index] = { id: editId, name, desc };
    }
  } else {
    state.serviceTypes.push({ id, name, desc });
  }

  closeModal('typeModal');
  renderAll();
  alert('Đã lưu thành công loại dịch vụ!');
}

function deleteType(id) {
  if (confirm(`Bạn có chắc chắn muốn xóa loại dịch vụ [${id}]? Tất cả dịch vụ thuộc loại này cũng sẽ bị ảnh hưởng.`)) {
    state.serviceTypes = state.serviceTypes.filter(x => x.id !== id);
    state.services = state.services.filter(s => s.typeId !== id);
    renderAll();
  }
}

// 3. F2 & F4 - QUẢN LÝ DỊCH VỤ & LIỆT KÊ THEO LOẠI
function renderServices(filteredList = null) {
  const list = filteredList || state.services;
  const tbody = document.getElementById('services-table-body');
  document.getElementById('services-count-display').innerText = list.length;

  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">Không tìm thấy dịch vụ phù hợp.</td></tr>`;
    return;
  }

  tbody.innerHTML = list.map(s => {
    const type = state.serviceTypes.find(t => t.id === s.typeId);
    return `
      <tr>
        <td><strong>${s.id}</strong></td>
        <td><strong>${s.name}</strong></td>
        <td><span class="badge" style="background:#475569">${type ? type.name : s.typeId}</span></td>
        <td class="text-right text-primary font-weight-bold">${formatVND(s.price)}</td>
        <td class="text-muted"><small>${s.note || '-'}</small></td>
        <td class="text-center">
          <button class="btn btn-sm btn-outline" onclick="editService('${s.id}')"><i class="fa-solid fa-pen"></i></button>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteService('${s.id}')"><i class="fa-solid fa-trash"></i></button>
        </td>
      </tr>
    `;
  }).join('');
}

function filterServicesByType() {
  const selectedType = document.getElementById('service-type-filter').value;
  const keyword = document.getElementById('service-search-input').value.toLowerCase().trim();

  let filtered = state.services;
  if (selectedType !== 'ALL') {
    filtered = filtered.filter(s => s.typeId === selectedType);
  }
  if (keyword) {
    filtered = filtered.filter(s => s.name.toLowerCase().includes(keyword) || s.id.toLowerCase().includes(keyword));
  }
  renderServices(filtered);
}

function openAddServiceModal() {
  document.getElementById('service-edit-id').value = '';
  document.getElementById('service-id').value = 'DV0' + (state.services.length + 1);
  document.getElementById('service-id').readOnly = false;
  document.getElementById('service-name').value = '';
  document.getElementById('service-price').value = '';
  document.getElementById('service-note').value = '';
  document.getElementById('service-modal-title').innerHTML = `<i class="fa-solid fa-wand-magic-sparkles text-primary"></i> Thêm Dịch Vụ Mới`;
  openModal('serviceModal');
}

function editService(id) {
  const s = state.services.find(x => x.id === id);
  if (!s) return;
  document.getElementById('service-edit-id').value = s.id;
  document.getElementById('service-id').value = s.id;
  document.getElementById('service-id').readOnly = true;
  document.getElementById('service-type-id-select').value = s.typeId;
  document.getElementById('service-name').value = s.name;
  document.getElementById('service-price').value = s.price;
  document.getElementById('service-note').value = s.note;
  document.getElementById('service-modal-title').innerHTML = `<i class="fa-solid fa-pen text-primary"></i> Cập Nhật Dịch Vụ Cưới`;
  openModal('serviceModal');
}

function handleSaveService(e) {
  e.preventDefault();
  const editId = document.getElementById('service-edit-id').value;
  const id = document.getElementById('service-id').value.trim();
  const typeId = document.getElementById('service-type-id-select').value;
  const name = document.getElementById('service-name').value.trim();
  const price = parseFloat(document.getElementById('service-price').value) || 0;
  const note = document.getElementById('service-note').value.trim();

  if (editId) {
    const idx = state.services.findIndex(x => x.id === editId);
    if (idx !== -1) {
      state.services[idx] = { id: editId, typeId, name, price, note };
    }
  } else {
    state.services.push({ id, typeId, name, price, note });
  }

  closeModal('serviceModal');
  renderAll();
  alert('Đã cập nhật thông tin dịch vụ cưới thành công!');
}

function deleteService(id) {
  if (confirm(`Bạn có chắc chắn muốn xóa dịch vụ [${id}]?`)) {
    state.services = state.services.filter(s => s.id !== id);
    renderAll();
  }
}

// 4. F3 - QUẢN LÝ KHO ÁO CƯỚI & TRANG PHỤC
function renderCostumes(statusFilter = 'ALL') {
  let list = state.costumes;
  if (statusFilter !== 'ALL') {
    list = list.filter(c => c.status === statusFilter);
  }

  const tbody = document.getElementById('costumes-table-body');
  document.getElementById('costume-stat-total').innerText = state.costumes.length;
  document.getElementById('costume-stat-available').innerText = state.costumes.filter(c => c.status === 'SAN_SANG').length;
  document.getElementById('costume-stat-renting').innerText = state.costumes.filter(c => c.status === 'DANG_THUE').length;

  tbody.innerHTML = list.map(c => {
    const isAvail = c.status === 'SAN_SANG';
    return `
      <tr>
        <td><strong>${c.id}</strong></td>
        <td><img src="${c.img}" class="costume-thumb" alt="${c.title}"></td>
        <td>
          <strong>${c.title}</strong>
        </td>
        <td><span class="badge" style="background:#f1f5f9; color:#334155; border:1px solid #cbd5e1">${c.category}</span></td>
        <td class="text-right font-weight-bold">${formatVND(c.rentPrice)}</td>
        <td class="text-right text-primary font-weight-bold">${formatVND(c.depositPrice)}</td>
        <td class="text-center">
          <span class="status-pill ${isAvail ? 'status-available' : 'status-renting'}">
            <i class="fa-solid ${isAvail ? 'fa-check' : 'fa-clock'}"></i>
            ${isAvail ? 'Trong kho' : 'Đang thuê'}
          </span>
        </td>
        <td class="text-center">
          <button class="btn btn-sm btn-outline" onclick="editCostume('${c.id}')"><i class="fa-solid fa-pen"></i></button>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteCostume('${c.id}')"><i class="fa-solid fa-trash"></i></button>
        </td>
      </tr>
    `;
  }).join('');
}

function filterCostumes(status) {
  document.querySelectorAll('#tab-costumes .filter-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
  renderCostumes(status);
}

function openAddCostumeModal() {
  document.getElementById('costume-edit-id').value = '';
  document.getElementById('costume-id').value = 'AC0' + (state.costumes.length + 1);
  document.getElementById('costume-id').readOnly = false;
  document.getElementById('costume-title').value = '';
  document.getElementById('costume-rent-price').value = '';
  document.getElementById('costume-deposit-price').value = '';
  document.getElementById('costume-modal-title').innerHTML = `<i class="fa-solid fa-vest text-primary"></i> Thêm Áo Cưới Mới`;
  openModal('costumeModal');
}

function editCostume(id) {
  const c = state.costumes.find(x => x.id === id);
  if (!c) return;
  document.getElementById('costume-edit-id').value = c.id;
  document.getElementById('costume-id').value = c.id;
  document.getElementById('costume-id').readOnly = true;
  document.getElementById('costume-title').value = c.title;
  document.getElementById('costume-category').value = c.category;
  document.getElementById('costume-rent-price').value = c.rentPrice;
  document.getElementById('costume-deposit-price').value = c.depositPrice;
  document.getElementById('costume-modal-title').innerHTML = `<i class="fa-solid fa-pen text-primary"></i> Cập Nhật Trang Phục Cưới`;
  openModal('costumeModal');
}

function handleSaveCostume(e) {
  e.preventDefault();
  const editId = document.getElementById('costume-edit-id').value;
  const id = document.getElementById('costume-id').value.trim();
  const title = document.getElementById('costume-title').value.trim();
  const category = document.getElementById('costume-category').value;
  const rentPrice = parseFloat(document.getElementById('costume-rent-price').value) || 0;
  const depositPrice = parseFloat(document.getElementById('costume-deposit-price').value) || 0;

  if (editId) {
    const idx = state.costumes.findIndex(x => x.id === editId);
    if (idx !== -1) {
      state.costumes[idx].title = title;
      state.costumes[idx].category = category;
      state.costumes[idx].rentPrice = rentPrice;
      state.costumes[idx].depositPrice = depositPrice;
    }
  } else {
    state.costumes.push({
      id, title, category, rentPrice, depositPrice, status: 'SAN_SANG',
      img: 'https://images.unsplash.com/photo-1594552072238-b8a33785b261?w=300&auto=format&fit=crop&q=80'
    });
  }

  closeModal('costumeModal');
  renderAll();
  alert('Đã lưu trang phục thành công!');
}

function deleteCostume(id) {
  if (confirm(`Bạn có chắc chắn muốn xóa áo cưới [${id}]?`)) {
    state.costumes = state.costumes.filter(c => c.id !== id);
    renderAll();
  }
}

// 5. F3 - PHIẾU THUÊ ÁO CƯỚI & KIỂM TRA RÀNG BUỘC (MAX N=3, ĐẶT CỌC)
function renderRentals(statusFilter = 'ALL') {
  let list = state.rentals;
  if (statusFilter !== 'ALL') {
    list = list.filter(r => r.status === statusFilter);
  }

  const tbody = document.getElementById('rentals-table-body');
  tbody.innerHTML = list.map(r => {
    const cust = state.customers.find(c => c.id === r.customerId);
    const costumeNames = r.costumeIds.map(cid => {
      const c = state.costumes.find(x => x.id === cid);
      return `<div>• <strong>${cid}</strong>: ${c ? c.title : ''}</div>`;
    }).join('');

    let statusBadge = '';
    if (r.status === 'DA_TRA') {
      statusBadge = `<span class="status-pill status-returned"><i class="fa-solid fa-check-double"></i> Đã trả (${formatDate(r.returnDate)})</span>`;
    } else if (r.status === 'QUA_HAN') {
      statusBadge = `<span class="status-pill status-overdue"><i class="fa-solid fa-triangle-exclamation"></i> Quá hạn trả</span>`;
    } else {
      statusBadge = `<span class="status-pill status-renting"><i class="fa-solid fa-clock"></i> Đang thuê</span>`;
    }

    return `
      <tr>
        <td><strong>${r.id}</strong></td>
        <td>
          <strong>${cust ? cust.name : 'Khách lạ'}</strong><br>
          <small class="text-muted"><i class="fa-solid fa-phone"></i> ${cust ? cust.phone : ''}</small>
        </td>
        <td>${formatDate(r.startDate)}</td>
        <td><strong>${formatDate(r.dueDate)}</strong></td>
        <td><div style="font-size:12px; line-height:1.4">${costumeNames}</div></td>
        <td class="text-right font-weight-bold">${formatVND(r.totalRental)}</td>
        <td class="text-right text-primary font-weight-bold">${formatVND(r.depositAmount)}</td>
        <td class="text-center">${statusBadge}</td>
        <td class="text-center">
          ${r.status !== 'DA_TRA' ? 
            `<button class="btn btn-sm btn-outline-danger" onclick="handleReturnRental('${r.id}')"><i class="fa-solid fa-box-open"></i> Nhận trả áo</button>` : 
            `<span class="text-muted"><i class="fa-solid fa-circle-check text-success"></i> Hoàn tất</span>`}
        </td>
      </tr>
    `;
  }).join('');
}

function filterRentals(status) {
  document.querySelectorAll('#tab-rentals .filter-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
  renderRentals(status);
}

function openNewRentalModal() {
  // Reset form
  const form = document.getElementById('newRentalForm');
  form.reset();

  const todayStr = '2026-08-19';
  document.getElementById('rental-start-date').value = todayStr;
  
  // Mặc định hẹn trả sau 3 ngày
  const dueDate = new Date(todayStr);
  dueDate.setDate(dueDate.getDate() + 3);
  document.getElementById('rental-end-date').value = dueDate.toISOString().split('T')[0];

  // Render costume picker (chỉ hiển thị áo đang có sẵn trong kho)
  const picker = document.getElementById('costume-picker-list');
  const availableCostumes = state.costumes.filter(c => c.status === 'SAN_SANG');

  if (availableCostumes.length === 0) {
    picker.innerHTML = `<div class="text-danger p-2">Hiện tại không có áo cưới nào sẵn sàng trong kho để thuê!</div>`;
  } else {
    picker.innerHTML = availableCostumes.map(c => `
      <label class="costume-check-item">
        <input type="checkbox" name="selectedCostumes" value="${c.id}" data-rent="${c.rentPrice}" data-deposit="${c.depositPrice}" onchange="handleCostumeCheckChange()">
        <div>
          <strong>${c.id} - ${c.title}</strong>
          <div class="text-muted" style="font-size:11.5px">Giá thuê: <span class="text-dark">${formatVND(c.rentPrice)}</span> | Cọc quy định: <span class="text-primary font-weight-bold">${formatVND(c.depositPrice)}</span></div>
        </div>
      </label>
    `).join('');
  }

  updateRentalSummary();
  openModal('rentalModal');
}

function handleCostumeCheckChange() {
  const checked = document.querySelectorAll('input[name="selectedCostumes"]:checked');
  
  // KIỂM TRA RÀNG BUỘC ĐỀ BÀI: KHÁCH HÀNG ĐƯỢC THUÊ TỐI ĐA N BỘ
  if (checked.length > MAX_RENTAL_ITEMS) {
    alert(`Quy định studio: Mỗi khách hàng chỉ được thuê TỐI ĐA ${MAX_RENTAL_ITEMS} bộ trang phục trên 1 phiếu!`);
    event.target.checked = false;
  }

  updateRentalSummary();
}

function updateRentalSummary() {
  const checked = document.querySelectorAll('input[name="selectedCostumes"]:checked');
  let totalRent = 0;
  let minDeposit = 0;

  checked.forEach(chk => {
    totalRent += parseFloat(chk.dataset.rent) || 0;
    minDeposit += parseFloat(chk.dataset.deposit) || 0;
  });

  document.getElementById('selected-count-msg').innerText = `Đã chọn: ${checked.length}/${MAX_RENTAL_ITEMS} bộ`;
  document.getElementById('calc-total-rental').innerText = formatVND(totalRent);
  document.getElementById('calc-min-deposit').innerText = formatVND(minDeposit);
  document.getElementById('rental-actual-deposit').value = minDeposit; // Đề xuất cọc đúng quy định
}

function handleSaveRental(e) {
  e.preventDefault();
  const customerId = document.getElementById('rental-customer-select').value;
  const startDate = document.getElementById('rental-start-date').value;
  const dueDate = document.getElementById('rental-end-date').value;
  const actualDeposit = parseFloat(document.getElementById('rental-actual-deposit').value) || 0;

  const checked = document.querySelectorAll('input[name="selectedCostumes"]:checked');
  if (checked.length === 0) {
    alert('Vui lòng chọn ít nhất 1 bộ trang phục cưới!');
    return;
  }

  if (checked.length > MAX_RENTAL_ITEMS) {
    alert(`Không thể thuê vượt quá ${MAX_RENTAL_ITEMS} bộ!`);
    return;
  }

  let totalRent = 0;
  let minDeposit = 0;
  const costumeIds = [];

  checked.forEach(chk => {
    costumeIds.push(chk.value);
    totalRent += parseFloat(chk.dataset.rent) || 0;
    minDeposit += parseFloat(chk.dataset.deposit) || 0;
  });

  // KIỂM TRA RÀNG BUỘC TIỀN CỌC
  if (actualDeposit < minDeposit) {
    if (!confirm(`Tiền cọc (${formatVND(actualDeposit)}) thấp hơn mức cọc quy định tối thiểu (${formatVND(minDeposit)}). Bạn có muốn phê duyệt ngoại lệ?`)) {
      return;
    }
  }

  const newId = 'PT0' + (state.rentals.length + 1);
  state.rentals.unshift({
    id: newId,
    customerId,
    startDate,
    dueDate,
    costumeIds,
    totalRental: totalRent,
    depositAmount: actualDeposit,
    status: 'DANG_THUE',
    returnDate: null
  });

  // Cập nhật trạng thái các áo cưới sang 'DANG_THUE'
  costumeIds.forEach(cid => {
    const c = state.costumes.find(x => x.id === cid);
    if (c) c.status = 'DANG_THUE';
  });

  closeModal('rentalModal');
  renderAll();
  alert(`Lập phiếu thuê ${newId} thành công! Số lượng: ${costumeIds.length} bộ.`);
}

function handleReturnRental(rentalId) {
  const r = state.rentals.find(x => x.id === rentalId);
  if (!r) return;

  if (confirm(`Xác nhận hoàn tất trả đồ cho phiếu thuê [${rentalId}]? Các bộ áo cưới sẽ được nhập lại vào kho.`)) {
    r.status = 'DA_TRA';
    r.returnDate = '2026-08-19';

    // Đổi trạng thái áo cưới về SAN_SANG
    r.costumeIds.forEach(cid => {
      const c = state.costumes.find(x => x.id === cid);
      if (c) c.status = 'SAN_SANG';
    });

    renderAll();
    alert(`Đã xử lý hoàn trả phiếu thuê ${rentalId}. Toàn bộ áo cưới đã được chuyển về kho sẵn sàng!`);
  }
}

// 6. F7 - TRA CỨU THÔNG TIN ÁO CƯỚI & LỊCH SỬ THUÊ MƯỢN
function searchCostumeDetail() {
  const query = document.getElementById('costume-search-query').value.trim().toLowerCase();
  const container = document.getElementById('costume-search-result-container');

  if (!query) {
    container.innerHTML = `<div class="panel p-4 text-center text-muted">Vui lòng nhập mã hoặc tựa đề áo cưới để tìm kiếm thông tin chi tiết.</div>`;
    return;
  }

  const matches = state.costumes.filter(c => 
    c.id.toLowerCase().includes(query) || 
    c.title.toLowerCase().includes(query) ||
    c.category.toLowerCase().includes(query)
  );

  if (matches.length === 0) {
    container.innerHTML = `<div class="panel p-4 text-center text-danger"><i class="fa-solid fa-circle-exclamation"></i> Không tìm thấy bộ áo cưới nào khớp với từ khóa "${query}".</div>`;
    return;
  }

  container.innerHTML = matches.map(c => {
    // Tìm các phiếu thuê có chứa áo này
    const rentalHistory = state.rentals.filter(r => r.costumeIds.includes(c.id));
    const currentRental = rentalHistory.find(r => r.status === 'DANG_THUE' || r.status === 'QUA_HAN');

    return `
      <div class="result-card">
        <div class="costume-detail-view">
          <div>
            <img src="${c.img}" class="costume-detail-img" alt="${c.title}">
            <div class="text-center mt-3">
              <span class="status-pill ${c.status === 'SAN_SANG' ? 'status-available' : 'status-renting'}">
                ${c.status === 'SAN_SANG' ? '● Trong kho sẵn sàng' : '● Đang được thuê'}
              </span>
            </div>
          </div>
          <div>
            <h2>[${c.id}] ${c.title}</h2>
            <p class="text-muted"><i class="fa-solid fa-tag"></i> Phân loại: <strong>${c.category}</strong></p>

            <div class="info-grid">
              <div class="info-item">
                <label>Đơn Giá Thuê Theo Lượt:</label>
                <strong class="text-primary" style="font-size:18px">${formatVND(c.rentPrice)}</strong>
              </div>
              <div class="info-item">
                <label>Tiền Đặt Cọc Quy Định:</label>
                <strong class="text-danger" style="font-size:18px">${formatVND(c.depositPrice)}</strong>
              </div>
              <div class="info-item">
                <label>Tình Trạng Hiện Tại:</label>
                <strong>${c.status === 'SAN_SANG' ? 'Có sẵn trong kho' : 'Đang cho khách hàng mượn'}</strong>
              </div>
              <div class="info-item">
                <label>Tổng Lượt Đã Thuê Mượn:</label>
                <strong>${rentalHistory.length} lượt</strong>
              </div>
            </div>

            <div class="panel mt-3">
              <div class="panel-header" style="background:#f8fafc">
                <div class="panel-title">
                  <i class="fa-solid fa-clock-rotate-left text-primary"></i>
                  <h4>Lịch Sử & Thông Tin Thuê Mượn Của Bộ Áo Này</h4>
                </div>
              </div>
              <div class="panel-body p-0">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Mã Phiếu</th>
                      <th>Khách Hàng Mượn</th>
                      <th>Ngày Thuê</th>
                      <th>Hạn Trả</th>
                      <th>Trạng Thái</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${rentalHistory.length > 0 ? rentalHistory.map(r => {
                      const cust = state.customers.find(x => x.id === r.customerId);
                      return `
                        <tr>
                          <td><strong>${r.id}</strong></td>
                          <td>${cust ? cust.name : r.customerId} (${cust ? cust.phone : ''})</td>
                          <td>${formatDate(r.startDate)}</td>
                          <td>${formatDate(r.dueDate)}</td>
                          <td>${r.status === 'DA_TRA' ? '<span class="text-success">Đã trả</span>' : (r.status === 'QUA_HAN' ? '<span class="text-danger">Quá hạn</span>' : '<span class="text-warning">Đang giữ</span>')}</td>
                        </tr>
                      `;
                    }).join('') : `<tr><td colspan="5" class="text-center text-muted">Chưa có lịch sử thuê mượn nào.</td></tr>`}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// 7. F8 - TRA CỨU DỊCH VỤ CUNG CẤP THEO KHÁCH HÀNG
function searchCustomerServices() {
  const query = document.getElementById('customer-search-query').value.trim().toLowerCase();
  const container = document.getElementById('customer-search-result-container');

  if (!query) {
    container.innerHTML = `<div class="panel p-4 text-center text-muted">Vui lòng nhập tên, mã hoặc số điện thoại khách hàng để tra cứu.</div>`;
    return;
  }

  const matches = state.customers.filter(c => 
    c.id.toLowerCase().includes(query) || 
    c.name.toLowerCase().includes(query) || 
    c.phone.includes(query)
  );

  if (matches.length === 0) {
    container.innerHTML = `<div class="panel p-4 text-center text-danger"><i class="fa-solid fa-circle-exclamation"></i> Không tìm thấy khách hàng nào khớp với từ khóa "${query}".</div>`;
    return;
  }

  container.innerHTML = matches.map(cust => {
    // Các dịch vụ cưới đã đăng ký
    const customerServices = state.services.filter(s => cust.usedServices && cust.usedServices.includes(s.id));
    // Các phiếu thuê mượn áo cưới
    const customerRentals = state.rentals.filter(r => r.customerId === cust.id);

    return `
      <div class="result-card">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:12px; margin-bottom:16px;">
          <div>
            <h2 style="color:var(--primary)"><i class="fa-solid fa-user-circle"></i> [${cust.id}] ${cust.name}</h2>
            <div class="text-muted mt-1"><i class="fa-solid fa-phone"></i> SĐT: <strong>${cust.phone}</strong> | <i class="fa-solid fa-location-dot"></i> Địa chỉ: ${cust.address}</div>
          </div>
          <button class="btn btn-sm btn-primary" onclick="openNewRentalModal()"><i class="fa-solid fa-plus"></i> Tạo Phiếu Thuê</button>
        </div>

        <div class="grid-2-cols">
          <!-- 1. Dịch vụ cưới đã cung cấp -->
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">
                <i class="fa-solid fa-wand-magic-sparkles text-primary"></i>
                <h4>Các Dịch Vụ Cưới Đã Cung Cấp</h4>
              </div>
              <span class="badge" style="background:#475569">${customerServices.length} dịch vụ</span>
            </div>
            <div class="panel-body p-0">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Mã DV</th>
                    <th>Tên Dịch Vụ Cưới</th>
                    <th class="text-right">Đơn Giá</th>
                  </tr>
                </thead>
                <tbody>
                  ${customerServices.length > 0 ? customerServices.map(s => `
                    <tr>
                      <td><strong>${s.id}</strong></td>
                      <td>${s.name}</td>
                      <td class="text-right text-primary font-weight-bold">${formatVND(s.price)}</td>
                    </tr>
                  `).join('') : `<tr><td colspan="3" class="text-center text-muted">Chưa đăng ký gói dịch vụ cưới nào.</td></tr>`}
                </tbody>
              </table>
            </div>
          </div>

          <!-- 2. Phiếu thuê áo cưới -->
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">
                <i class="fa-solid fa-vest text-accent"></i>
                <h4>Phiếu Thuê Áo Cưới Đã Tạo</h4>
              </div>
              <span class="badge" style="background:#795290">${customerRentals.length} phiếu</span>
            </div>
            <div class="panel-body p-0">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Mã Phiếu</th>
                    <th>Ngày Thuê - Hạn Trả</th>
                    <th>Số Bộ</th>
                    <th>Trạng Thái</th>
                  </tr>
                </thead>
                <tbody>
                  ${customerRentals.length > 0 ? customerRentals.map(r => `
                    <tr>
                      <td><strong>${r.id}</strong></td>
                      <td>${formatDate(r.startDate)} <i class="fa-solid fa-arrow-right text-muted"></i> ${formatDate(r.dueDate)}</td>
                      <td><span class="badge">${r.costumeIds.length} bộ</span></td>
                      <td>
                        ${r.status === 'DA_TRA' ? '<span class="status-pill status-returned">Đã trả</span>' : (r.status === 'QUA_HAN' ? '<span class="status-pill status-overdue">Quá hạn</span>' : '<span class="status-pill status-renting">Đang thuê</span>')}
                      </td>
                    </tr>
                  `).join('') : `<tr><td colspan="4" class="text-center text-muted">Chưa có phiếu thuê áo cưới nào.</td></tr>`}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// 8. F5 - BÁO CÁO KHÁCH HÀNG THUÊ CHƯA TRẢ
function renderUnreturnedReport() {
  const unreturned = state.rentals.filter(r => r.status === 'DANG_THUE' || r.status === 'QUA_HAN');
  const tbody = document.getElementById('unreturned-table-body');
  document.getElementById('report-unreturned-count').innerText = `${unreturned.length} Phiếu Chưa Trả`;

  if (unreturned.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">Tuyệt vời! Hiện tại không có khách nào nợ đồ cưới.</td></tr>`;
    return;
  }

  tbody.innerHTML = unreturned.map(r => {
    const cust = state.customers.find(c => c.id === r.customerId);
    const costumeDetails = r.costumeIds.map(cid => {
      const c = state.costumes.find(x => x.id === cid);
      return `<div>• ${cid}: ${c ? c.title : ''}</div>`;
    }).join('');

    const isOverdue = r.status === 'QUA_HAN';

    return `
      <tr>
        <td><strong>${r.id}</strong></td>
        <td><strong>${cust ? cust.name : 'Khách lạ'}</strong></td>
        <td>${cust ? cust.phone : ''}</td>
        <td>${formatDate(r.startDate)}</td>
        <td><strong>${formatDate(r.dueDate)}</strong></td>
        <td><div style="font-size:12px">${costumeDetails}</div></td>
        <td class="text-right text-primary font-weight-bold">${formatVND(r.depositAmount)}</td>
        <td class="text-center">
          ${isOverdue ? '<span class="status-pill status-overdue">Quá hạn</span>' : '<span class="status-pill status-renting">Trong hạn thuê</span>'}
        </td>
        <td class="text-center">
          <button class="btn btn-sm btn-primary" onclick="handleReturnRental('${r.id}')"><i class="fa-solid fa-check"></i> Thu Hồi</button>
        </td>
      </tr>
    `;
  }).join('');
}

// 9. F6 - BÁO CÁO KHÁCH HÀNG THUÊ QUÁ HẠN
function renderOverdueReport() {
  const overdue = state.rentals.filter(r => r.status === 'QUA_HAN');
  const tbody = document.getElementById('overdue-table-body');
  document.getElementById('report-overdue-count').innerText = `${overdue.length} Khách Quá Hạn Cần Thu Hồi`;

  if (overdue.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">Không có khách hàng nào bị quá hạn.</td></tr>`;
    return;
  }

  tbody.innerHTML = overdue.map(r => {
    const cust = state.customers.find(c => c.id === r.customerId);
    const daysLate = getDaysDifference(r.dueDate, '2026-08-19');
    const penaltyFee = daysLate * 200000 * r.costumeIds.length; // Phạt 200k/ngày/bộ

    const costumeNames = r.costumeIds.map(cid => {
      const c = state.costumes.find(x => x.id === cid);
      return `<div>• <strong>${cid}</strong>: ${c ? c.title : ''}</div>`;
    }).join('');

    return `
      <tr style="background:#fff5f5">
        <td><strong class="text-danger">${r.id}</strong></td>
        <td>
          <strong>${cust ? cust.name : 'Khách lạ'}</strong><br>
          <small class="text-danger"><i class="fa-solid fa-phone"></i> ${cust ? cust.phone : ''}</small>
        </td>
        <td><small>${cust ? cust.address : ''}</small></td>
        <td>${formatDate(r.dueDate)}</td>
        <td><strong class="text-danger font-weight-bold">${daysLate} ngày trễ</strong></td>
        <td><div style="font-size:12px">${costumeNames}</div></td>
        <td class="text-right text-primary font-weight-bold">${formatVND(r.depositAmount)}</td>
        <td class="text-right text-danger font-weight-bold">${formatVND(penaltyFee)}</td>
        <td class="text-center">
          <div style="display:flex; gap:6px; justify-content:center">
            <button class="btn btn-sm btn-outline-danger" onclick="alert('Đã gửi tin nhắn SMS cảnh báo và số tiền phạt tới khách hàng ${cust ? cust.name : ''}!')"><i class="fa-solid fa-comment-sms"></i> Nhắc nhở</button>
            <button class="btn btn-sm btn-danger" onclick="handleReturnRental('${r.id}')"><i class="fa-solid fa-rotate-left"></i> Nhận trả</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function sendBatchAlerts() {
  alert('Hệ thống đã gửi thông báo SMS và Zalo tự động đến tất cả khách hàng thuê quá hạn!');
}

// Helpers
function openModal(id) {
  document.getElementById(id).classList.add('open');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

function formatDate(dStr) {
  if (!dStr) return '-';
  const parts = dStr.split('-');
  if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
  return dStr;
}

function getDaysDifference(d1Str, d2Str) {
  const d1 = new Date(d1Str);
  const d2 = new Date(d2Str);
  const diffTime = Math.abs(d2 - d1);
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}
