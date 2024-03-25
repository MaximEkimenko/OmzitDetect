let addIntervalButton = document.getElementById('addInterval');

let timeLine = document.getElementById('timeline');
let formIntervals = document.getElementById('intervalsInput');
let settingsBtn = document.getElementById('settingsBtn');
let sourceSelect = document.getElementById('sourceSelect');
let videoStream = document.getElementById('videoStream');
let baseUrl = 'http://127.0.0.1:8000/'

// Получение параметров запроса
const params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
});

console.log(params)

async function postData(url = '', data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    return await response;
}


document.getElementById('playVideo').onclick = async function () {
    console.log('{{ start_link }}')
    let response = await fetch('{{ start_link }}');
}
document.getElementById('stopVideo').onclick = async function () {
    let response = await fetch('{{ stop_link }}');
}

document.getElementById('saveSettingsBtn').onclick = function () {
    let settings_save_url = new URL(`video_settings/${sourceSelect.value}`, baseUrl)
    console.log(settings)
    postData(settings_save_url, settings)
}

let merged_intervals

let merged_time_intervals = ''

let settings

//settingsBtn.onclick = async function () {
//    let settings_url = new URL(`video_settings/${sourceSelect.value}`, baseUrl)
//    let response = await fetch(settings_url);
//    if (response.ok) {
//      settings = await response.json();
//      merged_intervals = settings.start.intervals
//      document.getElementById('source_name').value = sourceSelect.value
//      document.getElementById('video_source').value = settings.create.video_source
//      document.getElementById('x0').value = settings.create.crop[2]
//      document.getElementById('x1').value = settings.create.crop[3]
//      document.getElementById('y0').value = settings.create.crop[0]
//      document.getElementById('y1').value = settings.create.crop[1]
//      document.getElementById('unknown_save_step').value = settings.start.unknown_save_step
//      document.getElementById('width').value = settings.start.width
//      document.getElementById('skipped_frames_coeff').value = settings.start.skipped_frames_coeff
//      document.getElementById('faces_distance').value = settings.start.faces_distance
//      document.getElementById('is_record').checked = settings.stream.is_record
//      document.getElementById('is_recognized').checked = settings.stream.is_recognized
//      intervalsToTimeLine(merged_intervals)
//    } else {
//      alert("HTTP error: " + response.status);
//    }
//}

//sourceSelect.onchange = function () {
//    let video_url = new URL(`video_stream/${sourceSelect.value}`, baseUrl)
//    videoStream.src = video_url
//}



