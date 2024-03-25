const apiUrl = window.location.origin;

document.addEventListener("DOMContentLoaded", (event) => {
    const sourcesTable = document.getElementById('sources-table');
    let sourcesTableBody = document.createElement("tbody");
    sourcesTable.appendChild(sourcesTableBody);

    // Получение списка всех известных сервисов и проверка их состояния
    async function getSources () {
        let sourcesDataUrl = new URL(`api/sources/`, apiUrl);
        let response = await fetch(sourcesDataUrl);
        if (response.ok) {
            sources = await response.json();
            // Создание строк
            for (let i = 0; i < sources.length; i++) {
                await createSourceRow(sources[i])
            }
            // Обновление цветов строк
            for (let i = 0; i < sources.length; i++) {
                await colorRow(sources[i], i)
            }
        }
    }

    // Обновление цвета строки
    async function colorRow (sourceData, row_index) {
        // Row Color
        let status = await pingService(sourceData.address, sourceData.source_name)
        let row = sourcesTableBody.getElementsByTagName('tr')[row_index]
        if (status == 1) {
            // Если сервис запущен, а видео нет
            row.className = "table-success"
            row.getElementsByTagName('td')[2].innerHTML = 'No'
        } else if (status == 0) {
            // Если сервис недоступен
            row.className = "table-danger"
        } else if (status == 2) {
            // Если сервис запущен и видео запущено
            row.className = "table-success"
            row.getElementsByTagName('td')[2].innerHTML = 'Yes'
        }
    }

    // Создание строки
    async function createSourceRow (sourceData) {
        let row = document.createElement("tr");

        // Source Name
        let col1 = document.createElement("td");
        let link = document.createElement("a");
        link.href = new URL(`/sources/${sourceData.hostname}/${sourceData.source_name}`, apiUrl);
        link.innerHTML = sourceData.source_name;
        col1.appendChild(link);
        row.appendChild(col1);

        // Hostname
        let col2 = document.createElement("td");
        col2.innerHTML = sourceData.hostname;
        row.appendChild(col2);

        let col3 = document.createElement("td");
        col3.innerHTML = "";
        row.appendChild(col3);

        let col4 = document.createElement("td");
        let recordsLink = document.createElement("a");
        recordsLink.href = new URL(`/records/${sourceData.hostname}/${sourceData.source_name}`, apiUrl);
        recordsLink.innerHTML = "Show";
        col4.appendChild(recordsLink);
        row.appendChild(col4);

        sourcesTableBody.innerHTML = ""
        sourcesTableBody.appendChild(row);
    }

    // fetch с таймаутом
    const fetchTimeout = (url, options, timeout = 5000) => {
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), timeout);
      return fetch(url, {...options, signal: controller.signal})
        .finally(() => clearTimeout(id));
    };

    // Пингует сервис и проверяет, запущено ли видео
    async function pingService (hostAddress, sourceName) {
        let pingUrl = new URL(`/ping/${sourceName}`, hostAddress);
        // Если сервис недоступен
        let status = 0
        try {
          let response = await fetchTimeout(pingUrl, {}, 5000)
                if (response.ok) {
                    let data = await response.json()
                    if (data.video) {
                        // Если сервис запущен и видео запущено
                        status = 2
                    } else {
                        // Если сервис запущен, а видео нет
                        status = 1
                    }
                }
        } catch (e) {
        }
        return status
    }

    getSources()

    // Обновление списка сервисов и их состояний каждые 10 секунд
    let updateSourcesInterval = window.setInterval(function(){
        getSources()
    }, 10000);
});
