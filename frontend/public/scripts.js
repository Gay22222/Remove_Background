// Thêm sự kiện 'submit' vào form upload
document.getElementById('uploadForm').addEventListener('submit', async function (e) {
    e.preventDefault(); // Ngăn chặn hành vi mặc định của form (reload trang)

    const chatOutput = document.getElementById('chatOutput'); // Vùng hiển thị kết quả
    const fileInput = document.getElementById('fileInput'); // Trường chọn file

    // Hiển thị thông báo "Uploading file..."
    const userMessage = document.createElement('div');
    userMessage.classList.add('user-message'); // CSS class cho tin nhắn của người dùng
    userMessage.textContent = 'Uploading file...';
    chatOutput.appendChild(userMessage); // Thêm thông báo vào chatOutput

    const formData = new FormData(); // Tạo formData để gửi file đến server
    if (!fileInput.files[0]) {
        // Nếu không có file được chọn
        const botMessage = document.createElement('div');
        botMessage.classList.add('bot-message'); // CSS class cho tin nhắn của bot
        botMessage.textContent = 'Please select an image file.'; // Hiển thị lỗi
        chatOutput.appendChild(botMessage); // Thêm thông báo lỗi vào chatOutput
        return; // Kết thúc hàm
    }

    formData.append('file', fileInput.files[0]); // Thêm file đã chọn vào formData

    try {
        // Gửi yêu cầu POST đến API /upload
        const response = await fetch('/upload', {
            method: 'POST', // Phương thức POST
            body: formData, // Dữ liệu gửi đi là formData
        });

        if (response.ok) {
            // Nếu server trả về phản hồi thành công
            const result = await response.json(); // Chuyển phản hồi sang JSON
            const objects = result.objects; // Danh sách tên các vật thể nhận diện
            const imageUrl = result.image_url; // Đường dẫn ảnh kết quả

            // Hiển thị ảnh kết quả đã xử lý
            const botMessageImage = document.createElement('div');
            botMessageImage.classList.add('bot-message'); // CSS class cho tin nhắn của bot
            botMessageImage.innerHTML = `<p>Processed image:</p><img src="${imageUrl}" style="max-width:100%; border-radius:10px;">`;
            chatOutput.appendChild(botMessageImage); // Thêm ảnh kết quả vào chatOutput

            // Hiển thị danh sách các vật thể nhận diện được dưới dạng checkbox
            const botMessageObjects = document.createElement('div');
            botMessageObjects.classList.add('bot-message'); // CSS class cho tin nhắn của bot
            botMessageObjects.innerHTML = '<p>Select objects to delete:</p>';
            objects.forEach((obj, index) => {
                // Tạo checkbox cho mỗi vật thể nhận diện
                const checkbox = `<input type="checkbox" id="obj${index}" value="${obj}"> <label for="obj${index}">${obj}</label><br>`;
                botMessageObjects.innerHTML += checkbox;
            });
            chatOutput.appendChild(botMessageObjects); // Thêm danh sách checkbox vào chatOutput
        } else {
            // Nếu server trả về lỗi
            const error = await response.json(); // Chuyển phản hồi lỗi sang JSON
            const botMessageError = document.createElement('div');
            botMessageError.classList.add('bot-message'); // CSS class cho tin nhắn của bot
            botMessageError.textContent = `Error: ${error.error}`; // Hiển thị lỗi từ server
            chatOutput.appendChild(botMessageError); // Thêm thông báo lỗi vào chatOutput
        }
    } catch (error) {
        // Bắt lỗi trong quá trình gửi hoặc xử lý phản hồi từ server
        console.error('Error:', error); // Log lỗi ra console để debug
        const botMessageError = document.createElement('div');
        botMessageError.classList.add('bot-message'); // CSS class cho tin nhắn của bot
        botMessageError.textContent = 'An error occurred while uploading the file.'; // Hiển thị thông báo lỗi chung
        chatOutput.appendChild(botMessageError); // Thêm thông báo lỗi vào chatOutput
    }

    // Tự động cuộn xuống cuối khung chat sau khi thêm nội dung mới
    chatOutput.scrollTop = chatOutput.scrollHeight;
});
