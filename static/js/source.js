const apiUrl = window.location.origin;
let pathArray = window.location.pathname.split('/');
const hostname = pathArray[2]
const source = pathArray[3]

let merged_intervals = []

document.addEventListener("DOMContentLoaded", (event) => {

    async function getSourceData () {
        let sourcesDataUrl = new URL(`api/sources/${hostname}/${source}`, apiUrl);
        let response = await fetch(sourcesDataUrl);
        if (response.ok) {
            data = await response.json();
            return data
        }
    }

    async function applySourceData () {
        let sourceData = await getSourceData()
        let video = document.getElementById("videoStream")
        video.src = `${sourceData.video_link}?${Math.random()}`

        document.getElementById("playVideo").onclick = async function () {
            let response = await fetch(sourceData.start_link);
            if (response.ok) {
                // Добавляем ?${Math.random()} чтобы обновилась картинка, иначе достается из кэша
                video.src = `${sourceData.video_link}?${Math.random()}`
            }
        }

        document.getElementById("stopVideo").onclick = async function () {
            let response = await fetch(sourceData.stop_link);
            if (response.ok) {
                // Добавляем ?${Math.random()} чтобы обновилась картинка, иначе достается из кэша
                video.src = `${sourceData.video_link}?${Math.random()}`
            }
        }

        document.getElementById("source_name").value = sourceData.settings.name
        document.getElementById("video_source").value = sourceData.settings.create.video_source
        document.getElementById("unknown_save_step").value = sourceData.settings.start.unknown_save_step
        document.getElementById("skipped_frames_coeff").value = sourceData.settings.start.skipped_frames_coeff
        document.getElementById("faces_distance").value = sourceData.settings.start.faces_distance
        document.getElementById("x0").value = sourceData.settings.start.crop[2]
        document.getElementById("x1").value = sourceData.settings.start.crop[3]
        document.getElementById("y0").value = sourceData.settings.start.crop[0]
        document.getElementById("y1").value = sourceData.settings.start.crop[1]
        video.onload = function() {
           document.getElementById("width").value = this.naturalWidth;
        }
        merged_intervals = sourceData.settings.start.intervals
        intervalsToTimeLine(merged_intervals)
    }

    async function postData(url = '', data = {}) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        console.log(data)
        return await response;
    }

    async function saveSourceData () {
        let x0 = Number(document.getElementById("x0").value)
        let x1 = Number(document.getElementById("x1").value)
        let y0 = Number(document.getElementById("y0").value)
        let y1 = Number(document.getElementById("y1").value)
        let newData = {
            "name": document.getElementById("source_name").value,
            "create": {
                "video_source": document.getElementById("video_source").value,
            },
            "start": {
                "unknown_save_step": Number(document.getElementById("unknown_save_step").value),
                "skipped_frames_coeff": Number(document.getElementById("skipped_frames_coeff").value),
                "faces_distance": Number(document.getElementById("faces_distance").value),
                "intervals": merged_intervals,
                "crop": [y0, y1, x0, x1],
                "width": Number(document.getElementById("width").value),
            },
        }
        let saveSourceDataUrl = new URL(`api/sources/${hostname}/${source}`, apiUrl);
        let response = await postData(saveSourceDataUrl, newData)
    }

    document.getElementById('saveSettingsBtn').onclick = async function () {
        await saveSourceData()
    }

    applySourceData()

});