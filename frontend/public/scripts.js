document.getElementById('uploadForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const chatOutput = document.getElementById('chatOutput');
    const fileInput = document.getElementById('fileInput');

    // Hiển thị thông báo tải file
    const userMessage = document.createElement('div');
    userMessage.classList.add('user-message');
    userMessage.textContent = 'Uploading file...';
    chatOutput.appendChild(userMessage);

    const formData = new FormData();
    if (!fileInput.files[0]) {
        const botMessage = document.createElement('div');
        botMessage.classList.add('bot-message');
        botMessage.textContent = 'Please select an image file.';
        chatOutput.appendChild(botMessage);
        return;
    }

    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            const objects = result.objects; // Danh sách tên các vật thể
            const imageUrl = result.image_url; // Đường dẫn ảnh kết quả

            // Hiển thị ảnh kết quả
            const botMessageImage = document.createElement('div');
            botMessageImage.classList.add('bot-message');
            botMessageImage.innerHTML = `<p>Processed image:</p><img src="${imageUrl}" style="max-width:100%; border-radius:10px;">`;
            chatOutput.appendChild(botMessageImage);

            // Hiển thị danh sách các vật thể
            const botMessageObjects = document.createElement('div');
            botMessageObjects.classList.add('bot-message');
            botMessageObjects.innerHTML = '<p>Select objects to delete:</p>';
            objects.forEach((obj, index) => {
                const checkbox = `<input type="checkbox" id="obj${index}" value="${obj}"> <label for="obj${index}">${obj}</label><br>`;
                botMessageObjects.innerHTML += checkbox;
            });
            chatOutput.appendChild(botMessageObjects);
        } else {
            const error = await response.json();
            const botMessageError = document.createElement('div');
            botMessageError.classList.add('bot-message');
            botMessageError.textContent = `Error: ${error.error}`;
            chatOutput.appendChild(botMessageError);
        }
    } catch (error) {
        console.error('Error:', error);
        const botMessageError = document.createElement('div');
        botMessageError.classList.add('bot-message');
        botMessageError.textContent = 'An error occurred while uploading the file.';
        chatOutput.appendChild(botMessageError);
    }

    // Cuộn xuống dưới cùng
    chatOutput.scrollTop = chatOutput.scrollHeight;
});
