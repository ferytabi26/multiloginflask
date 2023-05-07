function updateText(text) {
    document.querySelector('#mode').textContent = text;
}
function lampu(status){
    if(status=="on"){
        document.querySelector('#lampu_on').style.backgroundColor = 'green';
        document.querySelector('#lampu_off').style.backgroundColor = '#4C5560';
    }
    if(status=="off"){
        document.querySelector('#lampu_on').style.backgroundColor = '#4C5560';
        document.querySelector('#lampu_off').style.backgroundColor = 'red';
    }
}

var dataku;
const socket = io.connect('http://localhost:5000');

// fungsi untuk mengambil data baru dari server
function getNewData() {
  // kirim event get_new_data ke server
    socket.emit('get_new_data');
}

// setiap interval waktu, panggil fungsi getNewData
setInterval(getNewData, 1000);

// meng-handle event new_data dari server
socket.on('new_data', function(data) {
    $('#table_body').empty();
    // ulangi setiap baris data dan masukkan ke dalam tabel
    data.data.forEach(function(row) {
        var newRow = $('<tr>');
        newRow.append($('<td>').text(row[1]));
        newRow.append($('<td>').text(row[2]));
        newRow.append($('<td>').text(row[3]));
        newRow.append($('<td>').text(row[4]));
        newRow.append($('<td>').text(row[5]));
        $('#table_body').append(newRow);
    });
});
