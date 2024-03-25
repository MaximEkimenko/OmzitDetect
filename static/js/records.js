const apiUrl = window.location.origin;
let pathArray = window.location.pathname.split('/');
const hostname = pathArray[2]
const source = pathArray[3]

document.addEventListener("DOMContentLoaded", (event) => {

    document.getElementById("exportExcelBtn").onclick = async function () {
        let sourceData = await getSourceData()
        let getExcelUrl = new URL(`${source}/xlsx/`, sourceData.records_link);
        let response = await fetch(getExcelUrl)
        if (response.ok) {
            let blob = await response.blob()
            const handle = await showSaveFilePicker({
                    suggestedName: `${source}.xlsx`,
                    types: [{
                        description: 'Excel File',
                        accept: {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']},
                    }],
            });
            const writableStream = await handle.createWritable();
            await writableStream.write(blob);
            await writableStream.close();
        }
    }

    async function getSourceData () {
        let sourcesDataUrl = new URL(`api/sources/${hostname}/${source}`, apiUrl);
        let response = await fetch(sourcesDataUrl);
        if (response.ok) {
            data = await response.json();
            return data
        }
    }

    async function getSourceRecords (url) {
        let sourceRecordsUrl = new URL(`${source}`, url);
        let response = await fetch(sourceRecordsUrl);
        if (response.ok) {
            data = await response.json();
            return data
        }
    }

    async function createTableData () {
        let sourceData = await getSourceData()
        let records = await getSourceRecords(sourceData.records_link)
        return records
    }

    async function createTable () {
      let tableData = await createTableData()
      $('#dataTable').DataTable(
        {
          data: tableData,
          columns: [
            {title: 'id'},
            {title: 'Name'},
            {title: 'Datetime'},
            {title: 'Photo'},
            {title: 'Source'},
          ]
        }
      );
    }

    createTable()

})