// Hàm thêm log bot vào khung chat
function updateBotStatus(message, isError = false) {
    const chatOutput = document.getElementById('chatOutput');
    const botMessage = document.createElement('div');
    botMessage.classList.add('bot-message');
    if (isError) {
        botMessage.classList.add('error-message'); // Thêm class nếu là lỗi
    }
    botMessage.textContent = message;
    chatOutput.appendChild(botMessage);
    chatOutput.scrollTop = chatOutput.scrollHeight; // Tự động cuộn xuống
}

// Hàm hiển thị ảnh kết quả từ server
function updateBotImage(imageUrl) {
    const chatOutput = document.getElementById('chatOutput');
    const botMessageImage = document.createElement('div');
    botMessageImage.classList.add('bot-message');
    botMessageImage.innerHTML = `<p>Ảnh đã được cập nhật:</p><img src="${imageUrl}" style="max-width:100%; border-radius:10px;">`;
    chatOutput.appendChild(botMessageImage);
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

// Hàm làm mới danh sách checkbox các vật thể
function updateCheckboxList(objects) {
    const objectSelectContainer = document.getElementById('detectedObjects');
    objectSelectContainer.innerHTML = ''; // Xóa nội dung cũ

    if (objects.length === 0) {
        updateBotStatus('Không phát hiện được vật thể nào.', true);
        document.getElementById('submitDeleteButton').disabled = true;
        return;
    }

    objects.forEach((obj, index) => {
        const checkboxContainer = document.createElement('div');
        checkboxContainer.classList.add('checkbox-item');

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `obj${index}`;
        checkbox.value = obj.id; // Sử dụng ID duy nhất
        checkbox.dataset.box = JSON.stringify(obj.box); // Gắn bounding box vào data-attribute

        const label = document.createElement('label');
        label.htmlFor = `obj${index}`;
        label.textContent = `${obj.name} (ID: ${obj.id})`; // Hiển thị tên và ID đối tượng

        checkboxContainer.appendChild(checkbox);
        checkboxContainer.appendChild(label);
        objectSelectContainer.appendChild(checkboxContainer);
    });

    // Kích hoạt nút xóa nếu có đối tượng
    document.getElementById('submitDeleteButton').disabled = false;
}

// Biến toàn cục lưu metadata các bounding boxes
let objectsMetadata = [];

// Xử lý khi người dùng gửi form upload
document.getElementById('uploadForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const chatOutput = document.getElementById('chatOutput');
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();

    if (!fileInput.files[0]) {
        updateBotStatus('Vui lòng chọn một file ảnh.', true);
        return;
    }

    updateBotStatus('Đang tải lên...');
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            updateBotImage(result.image_url); // Hiển thị ảnh kết quả
            updateCheckboxList(result.objects); // Cập nhật danh sách checkbox
            objectsMetadata = result.objects; // Lưu metadata của bounding boxes
            updateBotStatus('Hoàn tất nhận diện.');
        } else {
            const error = await response.json();
            updateBotStatus(`Lỗi: ${error.error}`, true);
        }
    } catch (error) {
        updateBotStatus('Có lỗi xảy ra khi tải lên file.', true);
    }
});

// Xử lý khi nhấn nút "Xóa vật thể đã chọn"
document.getElementById('submitDeleteButton').addEventListener('click', async function () {
    const chatOutput = document.getElementById('chatOutput');
    const selectedObjects = [];
    const selectedBoundingBoxes = [];
    const fileInput = document.getElementById('fileInput');

    // Thu thập tất cả checkbox được chọn
    document.querySelectorAll('#detectedObjects input[type="checkbox"]:checked').forEach(checkbox => {
        const objectId = checkbox.value;
        const objectBox = checkbox.dataset.box; // Lấy dữ liệu bounding box từ data-attribute
        selectedObjects.push(parseInt(objectId)); // Gửi ID
        selectedBoundingBoxes.push(JSON.parse(objectBox)); // Gửi bounding box
    });

    if (selectedObjects.length === 0) {
        updateBotStatus('Vui lòng chọn ít nhất một vật thể để xóa.', true);
        return;
    }

    const filename = fileInput.files[0]?.name;
    if (!filename) {
        updateBotStatus('Không có file nào được chọn. Vui lòng tải lên ảnh trước.', true);
        return;
    }

    updateBotStatus('Đang xóa các vật thể đã chọn...');

    try {
        const response = await fetch('/remove_object', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: filename,
                objects: selectedObjects, // Gửi danh sách các ID cần xóa
                bounding_boxes: selectedBoundingBoxes // Gửi bounding boxes
            }),
        });

        if (response.ok) {
            const result = await response.json();
            updateBotImage(result.image_url); // Hiển thị ảnh cập nhật
            updateBotStatus('Xóa vật thể thành công.');
        } else {
            const error = await response.json();
            updateBotStatus(`Lỗi: ${error.error}`, true);
        }
    } catch (error) {
        updateBotStatus('Có lỗi xảy ra khi xóa các vật thể.', true);
    }
});




// Xử lý khi nhấn nút "Reset"
document.getElementById('resetButton').addEventListener('click', async function () {
    updateBotStatus('Resetting...');

    try {
        const response = await fetch('/reset', {
            method: 'POST',
        });

        if (response.ok) {
            // Cập nhật thông báo reset thành công
            document.getElementById('chatOutput').innerHTML = ''; // Xóa nội dung hiện tại
            updateBotStatus('Chào mừng, vui lòng tải ảnh lên'); // Thêm thông báo vào khung chat

            // Xóa tất cả nội dung liên quan
            document.getElementById('detectedObjects').innerHTML = '';
            document.getElementById('fileInput').value = '';
            document.getElementById('submitDeleteButton').disabled = true;
        } else {
            const error = await response.json();
            updateBotStatus(`Error: ${error.error}`, true);
        }
    } catch (error) {
        updateBotStatus('An error occurred while resetting.', true);
    }
});

