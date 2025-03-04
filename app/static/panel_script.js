// 初始化函数
init_all();


function init_all() {

    document.getElementById("myModal").addEventListener('onclick', function () {
        this.style.display = "none";
    });

    document.getElementById("add_button").onclick = function () {
        document.getElementById("myModal").style.display = "block";
        document.getElementById('reservation_account').value = '';
        document.getElementById('reservation_password').value = '';
    };

    document.getElementById("close_add").onclick = function () {
        document.getElementById("myModal").style.display = "none";

    };

    document.getElementById("close_server").onclick = function () {
        document.getElementById("myModal_server").style.display = "none";
    };

    document.querySelectorAll(".switch").forEach(switchElement => {
        switchElement.addEventListener("change", function () {
            const isChecked = this.checked; // 获取当前开关的状态（true 或 false）
            const switchId = this.id; // 获取当前开关的 ID
            const switchLabel = this.labels[0].textContent.trim(); // 获取对应的 label 文本
            // 输出当前开关的状态变化
            console.log(`开关 ${switchLabel} (${switchId}) 的状态已改变为: ${isChecked ? "开启" : "关闭"}`);
            // 根据开关 ID 更新对应的状态字段
            switch (switchId) {
                case "s0":
                    statusUpdates.refresh_status = isChecked;
                    break;
                case "s1":
                    statusUpdates.sign_back_status = isChecked;
                    break;
                case "s2":
                    statusUpdates.sign_in_status = isChecked;
                    break;
                case "s3":
                    statusUpdates.reservation_status = isChecked;
                    break;
                case "s4":
                    statusUpdates.monitor_sign_in_status = isChecked;
                    break;
            }
            update_server_Statuses();
        });
    });


    // 生成时间段
    for (let hour = startTime; hour < endTime; hour++) {
        for (let minute = 0; minute < 60; minute += 30) {
            const start = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
            const endHour = hour + (minute === 30 ? 1 : 0);
            const endMinute = minute === 30 ? 0 : 30;
            const end = `${String(endHour).padStart(2, '0')}:${String(endMinute).padStart(2, '0')}`;
            timeSlots.push({start, end});
        }
    }

    timeSlots.forEach((slot, index) => {
        const slotDiv = document.createElement('div');
        slotDiv.classList.add('time-slot');
        slotDiv.textContent = `${slot.start} - ${slot.end}`;
        slotDiv.addEventListener('click', () => selectTimeSlot(index));
        document.getElementById('time-slots').appendChild(slotDiv);
    });

    fetchReservations().then(r => {
        const room_select = document.getElementById('room_select');
        roomData.forEach(room => {
            const option = document.createElement('option');
            option.value = room[2];
            option.textContent = room[2];
            room_select.appendChild(option);
        });
        updateSwitchVisibility();
    });
}


// 选择时间段
function selectTimeSlot(index) {
    if (firstSelectedIndex === null) {
        // 第一次选择，记录第一个选中的时间点
        firstSelectedIndex = index;
        selectedSlots = [index]; // 正式选中第一个时间点
        highlightMaxDuration(index); // 高亮显示最长时间范围
    } else {
        // 第二次选择，判断是否是同一个时间点
        if (firstSelectedIndex === index) {
            // 如果是同一个时间点，直接确认选择这个时间段
            firstSelectedIndex = null; // 重置第一个选中的时间点
            highlightedSlots = []; // 清空高亮状态
            // 获取选择的开始时间和结束时间
            selectedStart = timeSlots[index].start;
            selectedEnd = timeSlots[index].end;
            console.log(`选择的时间范围: ${selectedStart} ${selectedEnd}`);
        } else {
            // 不是同一个时间点，根据两个时间点确定正式选中的范围
            const start = Math.min(firstSelectedIndex, index);
            const end = Math.max(firstSelectedIndex, index);
            // 计算选择的时长是否超过最大时长限制
            const duration = (end - start) / 2 + 0.5; // 每个时间槽代表半小时
            if (duration > maxDuration) {
                // alert(`选择的时长不能超过${maxDuration}小时，请重新选择！`);
                // 取消选择
                firstSelectedIndex = null;
                selectedSlots = [];
                highlightedSlots = [];
                selectTimeSlot(index);
            } else {
                selectedSlots = []; // 清空之前的正式选中状态
                for (let i = start; i <= end; i++) {
                    selectedSlots.push(i);
                }
                firstSelectedIndex = null; // 重置第一个选中的时间点
                highlightedSlots = []; // 清空高亮状态
                // 获取选择的开始时间和结束时间
                selectedStart = timeSlots[start].start;
                selectedEnd = timeSlots[end].end;
                console.log(`选择的时间范围: ${selectedStart} ${selectedEnd}`);
            }
        }
    }

    // 更新UI
    updateTimeSlotsUI();
}

// 高亮显示最长时间范围
function highlightMaxDuration(startIndex) {
    highlightedSlots = [];
    const maxSlots = maxDuration * 2; // 最长选择时长对应的槽位数
    for (let i = 0; i < maxSlots; i++) {
        const nextIndex = startIndex + i;
        if (nextIndex < timeSlots.length) {
            highlightedSlots.push(nextIndex);
        } else {
            break; // 防止超出时间槽范围
        }
    }
}

// 更新时间槽的UI
function updateTimeSlotsUI() {
    const slots = document.querySelectorAll('.time-slot');
    slots.forEach((slot, index) => {
        if (selectedSlots.includes(index)) {
            slot.classList.add('selected');
            slot.classList.remove('highlight');
        } else if (highlightedSlots.includes(index)) {
            slot.classList.add('highlight');
            slot.classList.remove('selected');
        } else {
            slot.classList.remove('selected', 'highlight');
        }
    });
}


// 清空选择
function clearSelection() {
    firstSelectedIndex = null;
    selectedSlots = [];
    highlightedSlots = [];
    updateTimeSlotsUI();
}

// 高亮显示指定的时间范围
function highlightTimeRange(start, end) {
    clearSelection(); // 清空当前选择和高亮
    const startSlot = timeSlots.findIndex(slot => slot.start === start);
    const endSlot = timeSlots.findIndex(slot => slot.end === end);

    if (startSlot !== -1 && endSlot !== -1) {
        const startIdx = Math.min(startSlot, endSlot);
        const endIdx = Math.max(startSlot, endSlot);
        for (let i = startIdx; i <= endIdx; i++) {
            selectedSlots.push(i);
        }
        // 获取选择的开始时间和结束时间
        selectedStart = timeSlots[startIdx].start;
        selectedEnd = timeSlots[endIdx].end;
        updateTimeSlotsUI();
    } else {
        console.error("输入的时间范围无效");
    }
}


function createUserCard(data) {
    const card = document.createElement("div");
    card.className = "card user-card";

    // 使用模板字符串生成模块内容
    card.innerHTML = `
        <div class="box overview">
            <div class="simple">
                <div class="simple-1">
                    <i class="fa-solid fa-user"></i>
                    <p>预约账户</p>
                </div>
                <div id="show-account">
                    <p>${data.account}</p>
                </div>
            </div>
            <div class="status">
                <h2 class="status-text">${data.status}</h2>
            </div>
        </div>

        <div class="user-info">
            <div class="info">
                <div class="info-text">
                    <p><i class="fa-solid fa-lock"></i> 预约密码</p>
                    <p class="password-toggle" data-password="${data.password}" title="点击切换显示密码" >***********</p>
                </div>
                <div class="info-text">
                    <p><i class="fa-solid fa-clock"></i> 预约时间</p>
                    <p id="show-time">${data.time}</p>
                </div>
                <div class="info-text">
                    <p><i class="fa-solid fa-couch"></i> 预约房间</p>
                    <p id="show-room">${data.room_seat}</p>
                </div>
                <div class="info-text">
                    <p><i class="fa-solid fa-chair"></i></i> 预约座位</p>
                    <p id="show-seat">${data.seat_id}座位</p>
                </div>
            </div>
            <div class="box">
                <div class="btn-box">
                    <button onclick="service(this)">服务</button>
                    <button onclick="releaseSeat(this)">退座</button>
                    <button onclick="editInfo(this)">修改</button>
                    <button onclick="deleteCard(this)">删除</button>
                </div>
            </div>
        </div>
    `;

    // 为密码切换功能添加事件监听
    const passwordToggle = card.querySelector(".password-toggle");
    passwordToggle.addEventListener("click", function () {
        const realPassword = this.getAttribute("data-password");
        const currentText = this.textContent;

        if (currentText === "***********") {
            this.textContent = realPassword; // 显示真实密码
        } else {
            this.textContent = "***********"; // 隐藏密码
        }
    });

    // 根据状态设置背景颜色
    const statusDiv = card.querySelector(".status");
    const statusColor = statusColors[data.status];
    if (statusColor) {
        statusDiv.style.backgroundColor = statusColor;
    }

    return card;

}

// 动态添加模块到指定位置的函数
function addCardsToContent(dataArray) {
    // 找到 <div class="content" id="content"> 容器
    const contentContainer = document.getElementById("content");
    if (!contentContainer) {
        console.error("未找到 ID 为 'content' 的容器");
        return;
    }

    // 找到 <div class="top"> 元素
    const topElement = contentContainer.querySelector(".top");
    if (!topElement) {
        console.error("未找到类名为 'top' 的元素");
        return;
    }
    if (dataArray.length === 0) {
        // 获取元素
        const element = document.getElementById("show_no_thing");
        const logoImage = document.getElementById('show_no_thing');
        logoImage.onload = function () {
            logoImage.style.animationPlayState = 'running';
        };
        element.style.display = "flex";

    }

    // 在 <div class="top"> 的下方插入模块
    dataArray.forEach(data => {
        const card = createUserCard(data); // 调用封装的函数生成模块
        contentContainer.insertBefore(card, topElement.nextSibling); // 插入到 <div class="top"> 的下一个兄弟元素之前
    });
}

function service(button) {
    document.getElementById("myModal_server").style.display = "flex";
    // 获取当前点击的按钮
    // 找到按钮所在的卡片（向上查找直到找到 class="card user-card" 的元素）
    const user_card = button.closest(".card.user-card");

    if (!user_card) {
        alert("无法找到对应的卡片！");
        return;
    }
    // 从卡片中提取 data.account 等信息
    let account = user_card.querySelector("#show-account p").textContent;
    document.getElementById("show_server_user").innerText = account;
    fetch_server_Statuses(account);
    statusUpdates.reservation_account = account;
}

function releaseSeat(button) {
    // 获取当前点击的按钮
    // 找到按钮所在的卡片（向上查找直到找到 class="card user-card" 的元素）
    const user_card = button.closest(".card.user-card");

    if (!user_card) {
        alert("无法找到对应的卡片！");
        return;
    }

    // 从卡片中提取 data.account 等信息
    const account = user_card.querySelector("#show-account p").textContent;
    const data = {
        account: account
    };

    fetch('/api/cancel/reservation_seat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert(result.message || '操作成功！');
                location.replace(location.href);
            } else {
                alert('操作失败: ' + result.message);
            }
        })
        .catch(error => {
            console.error('Error sending seat action:', error);
            alert('发生错误，请稍后再试。');
        });
}

function editInfo(button) {
    // 找到按钮所在的卡片（向上查找直到找到 class="card user-card" 的元素）
    const user_card = button.closest(".card.user-card");

    if (!user_card) {
        alert("无法找到对应的卡片！");
        return;
    }

    // 从卡片中提取 data.account 等信息
    const account = user_card.querySelector("#show-account p").textContent;
    const time = user_card.querySelector("#show-time").textContent;
    const room = user_card.querySelector("#show-room").textContent;
    const seat = user_card.querySelector("#show-seat").textContent;

    // 获取密码值（从 data-password 属性中获取）
    const password = user_card.querySelector(".password-toggle").getAttribute("data-password");

    // 拆分时间
    const [startTime, endTime] = time.split("-").map(t => t.trim());

    // 提取座位编号（去掉“座位”字样，并去掉前导零）
    const seatNumber = parseInt(seat.replace("座位", "").trim(), 10);
    // 输出或使用这些值
    // console.log("Account:", account);
    // console.log("Password:", password);
    // console.log("Start Time:", startTime);
    // console.log("End Time:", endTime);
    // console.log("Room:", room);
    // console.log("Seat:", seatNumber);

    document.getElementById('reservation_account').value = account;
    document.getElementById('reservation_password').value = password;
    selectedStart = startTime;
    selectedEnd = endTime; // 获取结束时间
    highlightTimeRange(startTime, endTime);
    document.getElementById('room_select').value = room;
    updateSeats(room)
    document.getElementById('seat_show_num').selectedIndex = (parseInt(seat, 10) - 1);
    document.getElementById("myModal").style.display = "block";
}

function deleteCard(button) {
// 找到按钮所在的卡片（向上查找直到找到 class="card user-card" 的元素）
    const user_card = button.closest(".card.user-card");

    if (!user_card) {
        alert("无法找到对应的卡片！");
        return;
    }

    // 从卡片中提取 data.account 等信息
    const account = user_card.querySelector("#show-account p").textContent;
    const time = user_card.querySelector("#show-time").textContent;
    const room = user_card.querySelector("#show-room").textContent;
    const seat = user_card.querySelector("#show-seat").textContent;


    // 弹出确认对话框
    const isConfirmed = confirm(`确定要删除以下预约信息吗？\n\n预约账户: ${account}\n预约时间: ${time}\n预约位置: ${room}-${seat}`);

    // 如果用户确认删除
    if (!isConfirmed) {
        return;
    }
    // 创建要发送到服务器的数据对象
    const dataToDelete = {
        account: account
    };

    if (user_card) {
        // 发送删除请求到服务器
        fetch('/api/delete/reservation', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dataToDelete),
        }).then(response => response.json())
            .then(result => {
                if (result.success) {
                    // 添加动画类
                    user_card.classList.add("shrink-and-fade"); // 缩小并淡出1
                    // card.classList.add("slide-out-right"); // 滑出
                    // 设置一个短暂的延迟，等待动画完成后再删除
                    setTimeout(() => {
                        user_card.remove();
                    }, 300); // 动画时长为 0.3s，延迟 300ms
                } else {
                    // 处理失败情况
                    alert('删除失败: ' + result.message);
                }
            })
            .catch(error => {
                console.error('Error deleting seat:', error);
                alert('发生错误，请稍后再试。');
            });
    }
}


// 根据选定的房间更新座位选项的函数
function updateSeats(selectedRoomName) {
    var seatsSelect = document.getElementById('seat_show_num');
    seatsSelect.innerHTML = ''; // 清空当前座位选项

    // 在全局变量 roomData 中查找对应的房间数据
    var roomInfo = roomData.find(room => room[2] === selectedRoomName);
    if (roomInfo) {
        // 假设第一个元素是座位数量，第二个元素是房间ID，第三个元素是房间名称
        var seatCount = roomInfo[0]; // 座位数量
        var roomId = roomInfo[1]; // 房间ID

        // 根据座位数量生成座位数组
        var availableSeats = Array.from({length: seatCount}, (_, i) => i + 1);

        // 为每个座位创建一个选项
        availableSeats.forEach(function (seat) {
            var option = document.createElement('option');
            option.value = seat; // 座位编号
            option.textContent = `座位${seat}`; // 座位显示文本
            seatsSelect.appendChild(option);
        });
        // 在找到房间信息后，设置隐藏字段的值为房间ID
        var roomIdInput = document.getElementById('roomId');
        if (roomInfo) {
            roomIdInput.value = roomInfo[1]; // roomInfo[1] 是房间ID
        }
    } else {
        console.error('Room info not found for:', selectedRoomName);
    }
}


// 添加数据处理函数
function SyncData() {
    const reservation_account = document.getElementById('reservation_account').value;
    const reservation_password = document.getElementById('reservation_password').value;
    const start_time = selectedStart;
    const end_time = selectedEnd; // 获取结束时间
    const room = document.getElementById('room_select').value;
    const seat = document.getElementById('seat_show_num').value;

    // 验证用户名是否为11位数字的手机号码
    if (!/^\d{11}$/.test(reservation_account)) {
        alert('请输入11位数字的手机号码！');
        return;
    }

    // 检查每个字段是否为空
    if (!reservation_account) {
        console.error("账号不能为空！");
        alert("账号不能为空！");
        return;
    } else if (!reservation_password) {
        console.error("密码不能为空！");
        alert("密码不能为空！");
        return;
    } else if (!start_time) {
        console.error("开始时间不能为空！");
        alert("开始时间不能为空！");
        return;
    } else if (!end_time) {
        console.error("结束时间不能为空！");
        alert("结束时间不能为空！");
        return;
    } else if (!room) {
        console.error("房间选择不能为空！");
        alert("房间选择不能为空！");
        return;
    } else if (!seat) {
        console.error("座位选择不能为空！");
        alert("座位选择不能为空！");
        return;
    }


    const room_info = roomData.find(room1 => room1[2] === room);
    if (!room_info) {
        console.error('No room found for room_id:', room);
    }
    const room_name = room_info ? room : '未知房间';
    const room_id = room_info ? room_info[1] : '未知ID';

    // 创建要发送到服务器的数据对象
    const data = {
        reservation_account: reservation_account,
        reservation_password: reservation_password,
        start_time: start_time,
        end_time: end_time,
        room_id: room_id,
        seat_id: seat
    };
    console.log(data);
    // 发送POST请求到服务器
    fetch('/api/new_reservation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    }).then(response => response.json())
        .then(result => {
            // 处理服务器返回的数据
            if (result.success) {
                alert('同步成功！');
                location.replace(location.href);
            } else {
                alert('同步失败: ' + result.message);
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            alert('发生错误，请稍后再试。');
        });
}

async function fetchReservations() {
    return fetch('/api/get/reservation', {
        method: 'GET',
        credentials: 'include'  // 确保cookies被发送
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // console.log(data.data);
                // 处理数据，例如更新页面内容
                reservationsData = data.data.map(item => ({
                    account: item.username,
                    password: item.password,
                    time: `${item.time[0]}-${item.time[1]}`,
                    room_seat: findRoomName(item.room_id),
                    seat_id: item.seat_id[0],
                    // status: status[item.account_status] || '未知状态'
                    status: item.account_status || '未知状态'
                }));
                addCardsToContent(reservationsData)
            } else {
                const element = document.getElementById("show_no_thing");
                const logoImage = document.getElementById('show_no_thing');
                logoImage.onload = function () {
                    logoImage.style.animationPlayState = 'running';
                };
                element.style.display = "flex";
            }
        })
        .catch(error => {
            console.error('Error fetching reservations:', error);
        });
}


// 从后端获取状态并设置开关状态
function fetch_server_Statuses(reservation_account) {

    const data = {
        reservation_account: reservation_account
    };

    fetch('/api/get/server_statuses', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
    }).then(response => response.json())
        .then(result => {
            if (result.success) {
                // 直接将 result.data 映射为开关状态
                const switchStates = {
                    s0: result.data.refresh_status,
                    s1: result.data.sign_back_status,
                    s2: result.data.sign_in_status,
                    s3: result.data.reservation_status
                };
                statusUpdates.refresh_status = result.data.refresh_status;
                statusUpdates.reservation_status = result.data.reservation_status;
                statusUpdates.sign_in_status = result.data.sign_in_status;
                statusUpdates.sign_back_status = result.data.sign_back_status;
                statusUpdates.monitor_sign_in_status = result.data.monitor_sign_in_status;
                setSwitchStates(switchStates);
            } else {
                alert(result.message || "获取状态失败！");
            }
        })
        .catch(error => {
            console.error("Error fetching statuses:", error);
            alert("发生错误，请稍后再试。");
        });
}

// 从后端获取状态并设置开关状态
function update_server_Statuses() {
    // 发送状态更新到后端
    fetch('/api/update/server_statuses', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(statusUpdates),
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                console.log("状态更新成功:", result.message);
            } else {
                console.error("状态更新失败:", result.message);
            }
        })
        .catch(error => {
            console.error("Error updating statuses:", error);
        });
}

// 根据 room_id 查找房间名称
function findRoomName(roomId) {
    // 尝试将 roomId 转换为数字
    const roomIdNum = Number(roomId);
    // 查找房间信息，确保 roomIdNum 是数字
    const roomInfo = roomData.find(room => Number(room[1]) === roomIdNum);
    return roomInfo ? roomInfo[2] : '未知房间';
}


// 自定义设置开关状态的函数
function setSwitchStates(states) {
    if (typeof states !== "object" || states === null) {
        console.error("传入的状态必须是一个对象");
        return;
    }

    for (const id in states) {
        const switchElement = document.getElementById(id);
        if (!switchElement) {
            console.error(`未找到 ID 为 ${id} 的开关`);
            continue;
        }

        switchElement.checked = states[id]; // 设置开关状态
        console.log(`已将开关 ${id} 的状态设置为: ${states[id] ? "开启" : "关闭"}`);
    }
}

// 根据权限级别更新开关的可见性
function updateSwitchVisibility() {
    const permissionLevel = userData.permissionLevel;

    // 获取所有开关的父元素（<li>）
    const s0Li = document.getElementById("s0-li");
    const s1Li = document.getElementById("s1-li");
    const s2Li = document.getElementById("s2-li");
    const s3Li = document.getElementById("s3-li");

    // 根据权限级别设置可见性
    switch (permissionLevel) {
        case 0:
            s0Li.style.display = "block";
            s1Li.style.display = "block";
            s2Li.style.display = "none";
            s3Li.style.display = "none";
            break;
        case 1:
            s0Li.style.display = "block";
            s1Li.style.display = "block";
            s2Li.style.display = "block";
            s3Li.style.display = "none";
            break;
        case 2:
            s0Li.style.display = "block";
            s1Li.style.display = "block";
            s2Li.style.display = "block";
            s3Li.style.display = "block";
            break;
        case 3:
            // 假设权限级别为 3 时，所有开关都显示
            s0Li.style.display = "block";
            s1Li.style.display = "block";
            s2Li.style.display = "block";
            s3Li.style.display = "block";
            break;
        default:
            console.error("无效的权限级别:", permissionLevel);
            break;
    }
}