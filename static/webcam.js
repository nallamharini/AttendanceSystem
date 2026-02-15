const video = document.getElementById('video');

navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => { video.srcObject = stream; });

function capture() {
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    const imageData = canvas.toDataURL('image/jpeg');

    fetch('/attendance/mark/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageData })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText = data.message;
    });
}
