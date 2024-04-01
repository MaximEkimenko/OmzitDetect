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
            const downloadFile = (blob, fileName) => {
              const link = document.createElement('a');
              // create a blobURI pointing to our Blob
              link.href = URL.createObjectURL(blob);
              link.download = fileName;
              // some browser needs the anchor to be in the doc
              document.body.append(link);
              link.click();
              link.remove();
              // in case the Blob uses a lot of memory
              setTimeout(() => URL.revokeObjectURL(link.href), 7000);
            };
            downloadFile(blob, `${source}.xlsx`);
        }
    }



    async function getNewFileHandle() {
      const opts = {
                    suggestedName: `${source}.xlsx`,
                    types: [{
                        description: 'Excel File',
                        accept: {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']},
                    }],
            };
      return await window.showSaveFilePicker(opts);
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