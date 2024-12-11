// Hàm thêm log bot vào chat
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

// Hàm cập nhật ảnh kết quả
function updateBotImage(imageUrl) {
    const chatOutput = document.getElementById('chatOutput');
    const botMessageImage = document.createElement('div');
    botMessageImage.classList.add('bot-message');
    botMessageImage.innerHTML = `<p>Updated image:</p><img src="${imageUrl}" style="max-width:100%; border-radius:10px;">`;
    chatOutput.appendChild(botMessageImage);
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

// Xử lý sự kiện khi gửi form upload
document.getElementById('uploadForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const chatOutput = document.getElementById('chatOutput'); // Vùng hiển thị kết quả
    const fileInput = document.getElementById('fileInput'); // Trường chọn file
    const formData = new FormData();

    if (!fileInput.files[0]) {
        updateBotStatus('Please select an image file.', true);
        return;
    }

    updateBotStatus('Uploading file...');

    formData.append('file', fileInput.files[0]);

    try {
        console.log("Starting file upload..."); // Log bắt đầu upload

        // Gửi yêu cầu POST đến API /upload
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        console.log("Server response received:", response.status, response.statusText); // Log trạng thái phản hồi từ server

        if (response.ok) {
            const result = await response.json();
            console.log("Response JSON:", result); // Log JSON phản hồi từ server

            const objects = result.objects; // Danh sách các vật thể nhận diện
            const imageUrl = result.image_url; // Đường dẫn ảnh đã xử lý

            console.log("Detected objects:", objects); // Log danh sách đối tượng
            console.log("Processed image URL:", imageUrl); // Log URL ảnh

            // Hiển thị ảnh kết quả
            updateBotImage(imageUrl);

            // Làm mới danh sách checkbox
            const objectSelectContainer = document.getElementById('detectedObjects');
            objectSelectContainer.innerHTML = ''; // Xóa nội dung cũ

            if (objects && objects.length > 0) {
                objects.forEach((obj, index) => {
                    const checkboxContainer = document.createElement('div');
                    checkboxContainer.classList.add('checkbox-item');

                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = `obj${index}`;
                    checkbox.value = obj;

                    const label = document.createElement('label');
                    label.htmlFor = `obj${index}`;
                    label.textContent = obj;

                    checkboxContainer.appendChild(checkbox);
                    checkboxContainer.appendChild(label);

                    objectSelectContainer.appendChild(checkboxContainer);
                });

                console.log("Checkboxes created:", objects.length); // Log số lượng checkbox
                document.getElementById('submitDeleteButton').disabled = false; // Bật nút xóa
                updateBotStatus('Detection completed.');
            } else {
                const noObjectsMessage = document.createElement('div');
                noObjectsMessage.classList.add('bot-message');
                noObjectsMessage.textContent = 'No objects detected in the image.';
                chatOutput.appendChild(noObjectsMessage);

                console.log("No objects detected."); // Log khi không có đối tượng
                document.getElementById('submitDeleteButton').disabled = true; // Tắt nút xóa
                updateBotStatus('No objects detected.', true);
            }
        } else {
            const error = await response.json();
            console.error("Error from server:", error); // Log lỗi từ server
            updateBotStatus(`Error: ${error.error}`, true);
        }
    } catch (error) {
        console.error("Upload error:", error); // Log lỗi khi xử lý
        updateBotStatus('An error occurred while uploading the file.', true);
    }

    chatOutput.scrollTop = chatOutput.scrollHeight; // Tự động cuộn xuống
});

// Xử lý sự kiện khi nhấn nút "Xóa vật thể đã chọn"
document.getElementById('submitDeleteButton').addEventListener('click', async function () {
    const chatOutput = document.getElementById('chatOutput'); // Vùng hiển thị kết quả
    const selectedObjects = []; // Danh sách các vật thể được chọn
    const fileInput = document.getElementById('fileInput'); // Trường chọn file

    // Thu thập tất cả các checkbox được chọn
    document.querySelectorAll('#detectedObjects input[type="checkbox"]:checked').forEach(checkbox => {
        selectedObjects.push(checkbox.value);
    });

    if (selectedObjects.length === 0) {
        updateBotStatus('Please select at least one object to delete.', true);
        return;
    }

    const filename = fileInput.files[0]?.name; // Lấy tên file từ input
    if (!filename) {
        updateBotStatus('No file selected. Please upload an image first.', true);
        return;
    }

    updateBotStatus('Removing selected object...');

    try {
        console.log("Sending delete request for:", { filename, object: selectedObjects[0] }); // Log request

        // Gửi yêu cầu POST đến API /remove_object
        const response = await fetch('/remove_object', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: filename,
                object: selectedObjects[0], // Gửi đối tượng đầu tiên
            }),
        });

        if (response.ok) {
            const result = await response.json();
            console.log("Object removed successfully."); // Log thành công
            updateBotStatus('Object removed successfully.');
            updateBotImage(result.image_url);
        } else {
            const error = await response.json();
            console.error("Error response from server:", error); // Log lỗi từ server
            updateBotStatus(`Error: ${error.error}`, true);
        }
    } catch (error) {
        console.error("Deletion error:", error); // Log lỗi khi xử lý
        updateBotStatus('An error occurred while deleting the objects.', true);
    }

    chatOutput.scrollTop = chatOutput.scrollHeight; // Tự động cuộn xuống
});
