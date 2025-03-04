
// 存储房间的数据
var roomData = [];


// -----------------------函数区-------------------------------------------------

document.addEventListener('DOMContentLoaded', function () {
    fetchRoomData();
    fetchSeatsData();
    // 禁用结束时间输入框
    document.getElementById('endTime').disabled = true;
    // 监听开始时间输入框的输入事件
    document.getElementById('timeSlot').addEventListener('input', function () {
        // 如果开始时间输入框有值，则启用结束时间输入框
        if (this.value) {
            document.getElementById('endTime').disabled = false;
        } else {
            // 如果开始时间输入框为空，则禁用结束时间输入框
            document.getElementById('endTime').disabled = true;
        }
    });
});


// 添加数据处理函数
function SyncData() {
    event.preventDefault()

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const timeSlot = document.getElementById('timeSlot').value;
    const endTime = document.getElementById('endTime').value; // 获取结束时间
    const room = document.getElementById('room').value;
    const seat = document.getElementById('seat').value;
    const status = "待抢座";

    // 验证用户名是否为11位数字的手机号码
    if (!/^\d{11}$/.test(username)) {
        alert('请输入11位数字的手机号码！');
        return; // 如果验证失败，终止函数执行
    }
    // 将时间转换为Date对象以便比较
    const startTime = new Date(`1970-01-01T${timeSlot}`);
    const end = new Date(`1970-01-01T${endTime}`);

    // 检查开始时间是否小于结束时间
    if (startTime >= end) {
        alert('预约开始时间必须小于预约结束时间！');
        return; // 如果验证失败，终止函数执行
    }

    // 检查时间间隔是否超过4小时
    const maxDuration = 4 * 60 * 60 * 1000; // 4小时的毫秒数
    if (end - startTime > maxDuration) {
        alert('预约时长不能超过4小时！');
        return; // 如果验证失败，终止函数执行
    }
    // 检查开始时间是否不早于8:00
    const minStartTime = new Date(`1970-01-01T08:00`);
    if (startTime < minStartTime) {
        alert('预约开始时间不能早于8:00！');
        return; // 如果验证失败，终止函数执行
    }

    // 检查结束时间是否不晚于22:00
    const maxEndTime = new Date(`1970-01-01T22:00`);
    if (end > maxEndTime) {
        alert('预约结束时间不能晚于22:00！');
        return; // 如果验证失败，终止函数执行
    }

    const roomInfo = roomData.find(room1 => room1[2] === room);
    if (!roomInfo) {
        console.error('No room found for room_id:', room);
    }
    const roomName = roomInfo ? room : '未知房间';
    const roomId = roomInfo ? roomInfo[1] : '未知ID';
    const roomInfoString = `${roomName}/${seat}号`; // 使用模板字符串拼接
    // 创建要发送到服务器的数据对象
    const data = {
        username: username,
        password: password,
        timeslot: timeSlot,
        endtime: endTime,
        roomid: roomId,
        seat: seat,
        status: status
    };

    // 发送POST请求到服务器
    fetch('/api/get/contact', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    }).then(response => response.json())
        .then(result => {
            // 处理服务器返回的数据
            if (result.success) {
                // 根据需要更新界面或执行其他操作
                const row = document.createElement('tr');
                const autoReservationButtonStyle = 'background-color:  #008CBA; color: white;';
                row.innerHTML = `
                    <td>${username}</td>
                    <td id="password-${seat.roomId}" class="hidden-password" onclick="togglePasswordVisibility(this)" data-password="${password}">${'•'.repeat(password.length)}</td>
                    <td>${timeSlot} - ${endTime}</td> <!-- 显示开始和结束时间 -->
                    <td style="display: none;" data-room-id="${roomId}"></td>
                    <td>${roomInfoString}</td>
                    <td>${status}</td>
                    <td class="actions">
                        <button style=style="${autoReservationButtonStyle}" onclick="AutoReservation(this)">关闭</button>
                        <button  onclick="cancelSeat(this)">退座</button>
                        <button onclick="editRow(this)" >编辑</button>
                        <button onclick="deleteRow(this)" >删除</button>
                    </td>
                `;
                document.getElementById('seatsTable').getElementsByTagName('tbody')[0].appendChild(row);
                row.style.opacity = '0';
                setTimeout(() => {
                    row.style.opacity = '1';
                }, 10);
                alert('同步成功！');
                location.replace(location.href);
            } else {
                alert('同步失败: ' + result.message);
                // 根据需要处理错误情况
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            console.error('Error details:', error.message, error.stack); // 打印
            alert('发生错误，请稍后再试。');
        });
}


// 获取房间数据的函数
function fetchRoomData() {
    fetch('/api/get/room_data')
        .then(response => response.json())
        .then(data => {
            roomData = data; // 保存房间数据到全局变量
            const roomSelect = document.getElementById('room');
            data.forEach(room => {
                const option = document.createElement('option');
                option.value = room[2];
                option.textContent = room[2];
                roomSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching room data:', error));
}


// 获取座位数据的函数
function fetchSeatsData() {
    fetch('/api/get/seats_data')
        .then(response => response.json())
        .then(data => {

            const tableBody = document.getElementById('seatsTableBody');
            let index = 1;
            // 按开始时间排序
            data.sort((a, b) => {
                const timeA = new Date(`1970-01-01T${a.time_period.split(' - ')[0]}`);
                const timeB = new Date(`1970-01-01T${b.time_period.split(' - ')[0]}`);
                return timeA - timeB;
            });

            data.forEach(seat => {
                // 根据房间号查找房间名称
                const roomInfo = roomData.find(room => room[1] === seat.roomid);
                if (!roomInfo) {
                    console.error('No room found for room_id:', seat.roomid);
                }
                const roomName = roomInfo ? roomInfo[2] : '未知房间';
                const roomId = roomInfo ? roomInfo[1] : '未知ID';
                const roomInfoString = `${roomName}/${seat.seat}号`; // 使用模板字符串拼接
                const autoReservationButtonText = seat.is_auto_reservation === 0 ? '启用' : '关闭';
                const autoReservationButtonStyle = seat.is_auto_reservation === 1 ? 'background-color: #FF8000; color: white;' : 'background-color: #008CBA; color: white;';
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${seat.account}</td>
                    <td id="password-${seat.id}" class="hidden-password" onclick="togglePasswordVisibility(this)" data-password="${seat.password}">${'•'.repeat(seat.password.length)}</td>
                    <td>${seat.time_period}</td>
                    <td>${roomInfoString}</td>
                    <td style="display: none;" data-room-id="${roomId}"></td>
                    <td>${seat.status}</td>
                    <td class="actions">
                        <button style="${autoReservationButtonStyle}"  onclick="AutoReservation(this)">${autoReservationButtonText}</button>
                        <button onclick="cancelSeat(this)">退座</button>
                        <button onclick="editRow(this)">编辑</button>
                        <button onclick="deleteRow(this)">删除</button>
                    </td>
                `;
                // 应用动画类
                row.classList.add('table-row-enter');
                setTimeout(() => {
                    tableBody.appendChild(row);
                    // 动画结束后移除动画类
                    row.addEventListener('animationend', () => {
                        row.classList.remove('table-row-enter');
                    });
                }, (100 * index++)); // 延迟时间逐渐增加，创建逐行添加效果
            });

        })
        .catch(error => console.error('Error fetching seats data:', error));
    ;
}


// 切换自动预约的函数
function AutoReservation(button) {
    const row = button.parentNode.parentNode;
    const account = row.cells[0].innerText;
    if (button.innerText === '启用') {

        sendSeatAction_reservation(button, '/api/set/auto_reservation', {account, data: true});
    } else {

        sendSeatAction_reservation(button, '/api/set/auto_reservation', {account, data: false});
    }
}


// 发送座位操作的函数
function sendSeatAction_reservation(button, url, data) {
    fetch(url, {
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
                if (result.end === true) {
                    button.innerText = '关闭';
                    button.style.backgroundColor = '#FF8000'; // 启用状态下的按钮颜色
                } else {
                    button.innerText = '启用';
                    button.style.backgroundColor = '#008CBA'; // 关闭状态下的按钮颜色
                }
            } else {
                alert('操作失败: ' + result.message);
            }
        })
        .catch(error => {
            console.error('Error sending seat action:', error);
            alert('发生错误，请稍后再试。');
        });
}

// 退座处理函数
function cancelSeat(button) {
    const row = button.parentNode.parentNode;
    const account = row.cells[0].innerText;
    sendSeatAction_cancel_seat('/api/set/cancel_seat', {account});
}


// 发送退座操作的函数
function sendSeatAction_cancel_seat(url, data) {
    fetch(url, {
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
            } else {
                alert('操作失败: ' + result.message);
            }
        })
        .catch(error => {
            console.error('Error sending seat action:', error);
            alert('发生错误，请稍后再试。');
        });
}


//--------------------------------------按键逻辑部分---------------------------------------------------------------

// 修改 editRow 函数以填充表单
function editRow(button) {
    const row = button.parentNode.parentNode;
    const cells = row.getElementsByTagName('td');
    const username = cells[0].textContent;
    const password = cells[1].getAttribute('data-password');
    const timePeriod = cells[2].textContent; // 假设时间格式为 "开始时间 - 结束时间"
    const roomSeatText = cells[3].textContent; // 假设房间和座位格式为 "房间/座位号"

    // 提取房间名称，假设房间名称和座位号之间用"/"分隔
    const room = roomSeatText.split('/')[0].trim(); // 获取房间名称并移除空格

    // 填充表单
    document.getElementById('username').value = username;
    document.getElementById('password').value = password;

    // 获取房间下拉菜单
    const roomSelect = document.getElementById('room');

    // 遍历房间下拉菜单的选项，找到匹配的房间并设置为选中状态
    let roomFound = false;
    for (let i = 0; i < roomSelect.options.length; i++) {
        // 输出每个选项的文本内容，用于调试
        // console.log(`Option ${i}:${roomSelect.options[i].textContent}`);
        // 比较时确保文本内容的大小写一致，并且只比较房间名称（不包含座位号）
        if (roomSelect.options[i].textContent.trim().toLowerCase() === room.toLowerCase()) {
            roomSelect.selectedIndex = i; // 设置为选中状态
            roomFound = true;
            updateSeats(room)
            break; // 找到匹配项后退出循环
        }

    }

    // 如果没有找到匹配的房间，输出调试信息
    if (!roomFound) {
        console.error(`Room "${room}" not found in the dropdown options.`);
    }
    // 正则表达式来检查时间格式是否为 "HH:mm - HH:mm"
    const timeFormatRegex = /^(?:[01]\d|2[0-3]):[0-5]\d\s*-\s*(?:[01]\d|2[0-3]):[0-5]\d$/;

    // 检查时间字符串是否符合预期格式
    if (!timeFormatRegex.test(timePeriod)) {
        console.error('Time period string is not in the expected "HH:mm - HH:mm" format.');
        console.log('Actual time period string:', timePeriod);
        return;
    }

    // 使用 split 方法分割时间字符串，确保使用正确的分隔符
    const times = timePeriod.split('-');

    // 提取开始和结束时间，并确保它们不为空
    const startTime = times[0].trim();
    const endTime = times[1].trim();

    // 设置时间到表单元素
    document.getElementById('timeSlot').value = startTime;
    document.getElementById('endTime').value = endTime;

    // 添加新行后平滑滚动到页面底部
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth'
    });
}


// 根据选定的房间删除座位选项的函数
function deleteRow(button) {
    // 获取按钮所在的行
    const row = button.parentNode.parentNode;

    // 获取账号、密码、时间、座位和房间ID信息
    const account = row.cells[0].innerText;
    const password = row.cells[1].innerText;
    const time_period = row.cells[2].innerText;
    const seat = row.cells[3].innerText.split('/')[1]; // 假设座位号在roomName/seatNumber格式中
    const roomId = row.querySelector('[data-room-id]').getAttribute('data-room-id');

    // 创建要发送到服务器的数据对象
    const dataToDelete = {
        account: account,
        password: password,
        time_period: time_period,
        seat: seat,
        room_id: roomId
    };

    // 发送删除请求到服务器
    fetch('/api/delete/appointment', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToDelete),
    }).then(response => response.json())
        .then(result => {
            if (result.success) {
                // 删除行
                button.closest('tr').remove();
                // 显示弹窗提示
                alert('删除成功！');
                row.style.overflow = 'hidden'; // 防止内容溢出
                row.style.height = `${row.offsetHeight}px`; // 设置行的高度
                // 逐步减少行的高度和透明度
                row.style.transition = 'opacity 0.5s ease, height 0.5s ease';
                row.style.opacity = '0';
                row.style.height = '0px';
                // 当过渡完成后，删除行
                row.addEventListener('transitionend', function () {
                    row.parentNode.removeChild(row);
                });

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

// JavaScript 函数，用于根据选定的房间更新座位选项
// 根据选定的房间更新座位选项的函数
function updateSeats(selectedRoomName) {
    var seatsSelect = document.getElementById('seat');
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

//密码切换可见
function togglePasswordVisibility(element) {
    // 从元素的数据属性中获取密码
    const password = element.getAttribute('data-password');
    // 切换显示隐藏密码
    if (element.textContent === '•'.repeat(password.length)) {
        element.textContent = password;
        element.classList.remove('hidden-password');
        element.classList.add('visible-password');
    } else {
        element.textContent = '•'.repeat(password.length);
        element.classList.remove('visible-password');
        element.classList.add('hidden-password');
    }
}
